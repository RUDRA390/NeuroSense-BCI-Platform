# ============================================================
# EXPORT SNIPPET -- paste this as a NEW cell in MOTOR_IMAGERY.ipynb, AFTER
# `per_subject_metrics, histories = main()` has finished running.
#
# It reuses classes/functions already defined in your notebook (Config, CFG,
# best_band, build_subject_data, EuclideanAligner, ChannelScaler, EEGDataset,
# EEGNet, get_model, Trainer, SUBJECTS, CLASS_NAMES, SFREQ, device) -- it does
# NOT redefine them, so it must run in the same notebook session, not a
# separate script.
#
# What it produces: one "package" per deployable model -- a single .pt file
# containing BOTH the trained weights AND the exact preprocessing stats used
# (frequency band, per-channel scaler mean/std, Euclidean Alignment matrix).
# This replaces the 90-file-per-training-fold structure, which was built for
# cross-validated *evaluation*, not for shipping a model to a website.
# ============================================================
import os
import shutil

EXPORT_DIR = "/content/deploy_models"
os.makedirs(EXPORT_DIR, exist_ok=True)


def save_package(path, model, scaler, ea, cfg, band, label):
    torch.save({
        "model_state_dict": model.state_dict(),
        "n_classes": len(CLASS_NAMES),
        "n_channels": model.n_channels,
        "n_samples": model.n_samples,
        "sfreq": SFREQ,
        "band": band,
        "scaler_mean": scaler.mean_,
        "scaler_std": scaler.std_,
        "use_ea": cfg.use_euclidean_alignment,
        "ea_matrix": ea.R_inv_sqrt_ if ea is not None else None,
        "class_names": CLASS_NAMES,
        "label": label,
    }, path)
    print(f"Saved {path}")


def train_final_model(X_train_full, y_train_full, cfg, band, label):
    """Trains ONE final model on (nearly) all available data for this unit --
    no held-out-fold ensemble, no 10 separate files. A small stratified slice
    is still held out purely so early stopping / SWA-top-k has a val signal."""
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.15,
        stratify=y_train_full, random_state=cfg.seed)

    ea = None
    if cfg.use_euclidean_alignment:
        ea = EuclideanAligner().fit(X_tr)
        X_tr = ea.transform(X_tr)
        X_val = ea.transform(X_val)

    scaler = ChannelScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_val_s = scaler.transform(X_val)

    crop_samples = int(cfg.crop_seconds * SFREQ)
    train_loader = DataLoader(EEGDataset(X_tr_s, y_tr, crop_samples, train=True),
                               batch_size=cfg.batch_size, shuffle=True)
    val_loader = DataLoader(EEGDataset(X_val_s, y_val, crop_samples, train=False),
                             batch_size=cfg.batch_size, shuffle=False)

    n_channels = X_tr_s.shape[1]
    model = get_model(cfg.model_name, n_classes=len(CLASS_NAMES),
                       n_channels=n_channels, n_samples=crop_samples)
    trainer = Trainer(model, cfg)
    trainer.fit(train_loader, val_loader, verbose=False)
    print(f"  [{label}] final model trained.")
    return trainer.model, scaler, ea


# ---- 1. GENERIC (subject-independent, pooled across all 9 subjects) ----
# This is the model to actually ship for real website visitors, since none
# of them are the original 9 recorded subjects.
cfg = replace(CFG, lowcut=best_band[0], highcut=best_band[1])

X_pool, y_pool = [], []
for subject in SUBJECTS:
    X_tr, y_tr, _, _ = build_subject_data(subject, cfg)
    X_pool.append(X_tr)
    y_pool.append(y_tr)
X_pool = np.concatenate(X_pool, axis=0)
y_pool = np.concatenate(y_pool, axis=0)

set_seed(cfg.seed)
generic_model, generic_scaler, generic_ea = train_final_model(
    X_pool, y_pool, cfg, best_band, label="GENERIC")
save_package(os.path.join(EXPORT_DIR, "generic_eegnet_package.pt"),
             generic_model, generic_scaler, generic_ea, cfg, best_band, "GENERIC")

# ---- 2. OPTIONAL: one finalized model per subject (9 files, not 90) ----
# Only run this if you also want subject-specific options selectable in the
# UI dropdown (useful for demoing against the known dataset subjects).
# Skip it (set to False) if you only want the generic model for real
# deployment -- per-subject models will NOT generalize to a new visitor.
EXPORT_PER_SUBJECT = True
if EXPORT_PER_SUBJECT:
    for subject in SUBJECTS:
        set_seed(cfg.seed)
        X_tr, y_tr, _, _ = build_subject_data(subject, cfg)
        model, scaler, ea = train_final_model(X_tr, y_tr, cfg, best_band, label=subject)
        save_package(os.path.join(EXPORT_DIR, f"{subject}_final_package.pt"),
                     model, scaler, ea, cfg, best_band, subject)

# ---- Zip and download ----
shutil.make_archive("/content/deploy_models", "zip", EXPORT_DIR)
from google.colab import files
files.download("/content/deploy_models.zip")
print("\nUnzip this into your Flask app's models/ folder.")
