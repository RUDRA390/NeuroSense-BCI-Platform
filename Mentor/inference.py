"""
inference.py

Loads a "packaged" EEGNet model and runs prediction on a single raw
motor-imagery trial.

A package is a single .pt file (torch.save'd dict) containing BOTH the model
weights AND the exact preprocessing metadata used when that model was
trained (frequency band, per-channel normalization stats, Euclidean
Alignment matrix if used). This is deliberate: your original notebook only
saved model weights (90 .pt files, one per subject per CV fold), with no
saved record of the per-fold scaler/EA stats used to preprocess that fold's
data. Re-deriving those stats at inference time (e.g. by normalizing a
single incoming trial against itself) would NOT reproduce training-time
preprocessing faithfully and would quietly hurt accuracy. The fix is to
save everything needed together, once, at export time -- see
colab_package_export_snippet.py for the training-side half of this.
"""
import os
import numpy as np
import torch
import torch.nn as nn
from scipy.signal import butter, sosfiltfilt

CLASS_NAMES = ["Left Hand", "Right Hand", "Feet", "Tongue"]


# ---- EEGNet architecture -- must match your notebook's definition exactly ----
class EEGNet(nn.Module):
    def __init__(self, n_classes, n_channels, n_samples, F1=8, D=2, F2=16,
                 kernel_length=125, dropout_rate=0.5):
        super().__init__()
        self.n_channels = n_channels
        self.n_samples = n_samples
        self.firstconv = nn.Sequential(
            nn.Conv2d(1, F1, (1, kernel_length), padding=(0, kernel_length // 2), bias=False),
            nn.BatchNorm2d(F1),
        )
        self.depthwiseConv = nn.Sequential(
            nn.Conv2d(F1, F1 * D, (n_channels, 1), groups=F1, bias=False),
            nn.BatchNorm2d(F1 * D),
            nn.ELU(),
            nn.AvgPool2d((1, 4)),
            nn.Dropout(dropout_rate),
        )
        self.separableConv = nn.Sequential(
            nn.Conv2d(F1 * D, F1 * D, (1, 16), padding=(0, 8), groups=F1 * D, bias=False),
            nn.Conv2d(F1 * D, F2, (1, 1), bias=False),
            nn.BatchNorm2d(F2),
            nn.ELU(),
            nn.AvgPool2d((1, 8)),
            nn.Dropout(dropout_rate),
        )
        with torch.no_grad():
            dummy = torch.zeros(1, 1, n_channels, n_samples)
            out = self.separableConv(self.depthwiseConv(self.firstconv(dummy)))
            flat_dim = out.view(1, -1).shape[1]
        self.classify = nn.Linear(flat_dim, n_classes)

    def forward(self, x):
        x = self.firstconv(x)
        x = self.depthwiseConv(x)
        x = self.separableConv(x)
        x = x.flatten(1)
        return self.classify(x)


def _bandpass(signal_2d, low, high, sfreq, order=4):
    """signal_2d: (channels, samples)"""
    nyq = sfreq / 2.0
    sos = butter(order, [low / nyq, min(high / nyq, 0.999)], btype="band", output="sos")
    return sosfiltfilt(sos, signal_2d, axis=1)


def _center_crop(x, crop_samples):
    total = x.shape[1]
    start = max(total - crop_samples, 0) // 2
    return x[:, start:start + crop_samples]


class MotorImageryModel:
    """Wraps one packaged EEGNet model plus its preprocessing metadata."""

    def __init__(self, package_path, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        pkg = torch.load(
              package_path,
              map_location=self.device,
              weights_only=False
        )

        self.sfreq = pkg["sfreq"]
        self.band = pkg["band"]  # (lowcut, highcut)
        self.crop_samples = pkg["n_samples"]
        self.n_channels = pkg["n_channels"]
        self.class_names = pkg.get("class_names", CLASS_NAMES)
        self.scaler_mean = pkg["scaler_mean"]  # shape (1, n_channels, 1)
        self.scaler_std = pkg["scaler_std"]
        self.use_ea = pkg.get("use_ea", False)
        self.ea_matrix = pkg.get("ea_matrix", None)  # shape (n_channels, n_channels) or None
        self.label = pkg.get("label", os.path.basename(package_path))

        self.model = EEGNet(
            n_classes=len(self.class_names),
            n_channels=self.n_channels,
            n_samples=self.crop_samples,
        ).to(self.device)
        self.model.load_state_dict(pkg["model_state_dict"])
        self.model.eval()

    def preprocess(self, raw_trial):
        """raw_trial: numpy array (n_channels, n_samples_raw), UNFILTERED, in the
        same channel order used for training, sampled at self.sfreq (250 Hz)."""
        if raw_trial.shape[0] != self.n_channels:
            raise ValueError(
                f"Expected {self.n_channels} channels, got {raw_trial.shape[0]}. "
                f"Check channel order/count matches the BCI IV 2a 22-channel montage "
                f"(EOG channels must already be removed/regressed out)."
            )

        x = _bandpass(raw_trial.astype(np.float64), self.band[0], self.band[1], self.sfreq)
        x = x.astype(np.float32)

        if self.use_ea and self.ea_matrix is not None:
            x = self.ea_matrix @ x

        x = (x - self.scaler_mean[0]) / self.scaler_std[0]
        x = _center_crop(x, self.crop_samples)

        if x.shape[1] < self.crop_samples:
            raise ValueError(
                f"Trial too short after cropping: need >= {self.crop_samples} samples "
                f"({self.crop_samples / self.sfreq:.1f}s at {self.sfreq} Hz), got {x.shape[1]}."
            )
        return x

    @torch.no_grad()
    def predict(self, raw_trial):
        x = self.preprocess(raw_trial)
        tensor = torch.from_numpy(x).unsqueeze(0).unsqueeze(0).to(self.device)  # (1, 1, C, T)
        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        pred_idx = int(probs.argmax())
        return {
            "predicted_class": self.class_names[pred_idx],
            "predicted_index": pred_idx,
            "probabilities": {name: float(p) for name, p in zip(self.class_names, probs)},
            "model_used": self.label,
        }


class ModelRegistry:
    """Loads every .pt package found in a directory once, at server startup,
    so Flask never reloads weights mid-request."""

    def __init__(self, models_dir, device=None):
        self.models = {}
        if not os.path.isdir(models_dir):
            print(f"WARNING: models directory '{models_dir}' does not exist yet. "
                  f"Run the Colab export snippet and copy the .pt files there.")
            return
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith(".pt"):
                key = fname[:-3]
                path = os.path.join(models_dir, fname)
                try:
                    self.models[key] = MotorImageryModel(path, device=device)
                    print(f"Loaded model package: {key}")
                except Exception as e:
                    print(f"Skipping {fname}: could not load as a model package ({e})")

    def list_models(self):
        return list(self.models.keys())

    def get(self, key):
        if key not in self.models:
            raise KeyError(f"No model named '{key}'. Available: {self.list_models()}")
        return self.models[key]
