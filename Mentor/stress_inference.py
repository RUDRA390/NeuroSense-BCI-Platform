"""
stress_inference.py

Stress detection inference pipeline for NeuroSense.

Pipeline:
    Raw EEG (32, 3200)
        -> 1-40 Hz Butterworth band-pass filter
        -> per-channel normalization
        -> 8 statistical features per channel
        -> 256 features
        -> saved StandardScaler
        -> XGBoost model
        -> Non-Stress / Stress
"""

import json
from pathlib import Path

import numpy as np
import xgboost as xgb

from scipy.io import loadmat


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "xgboost_stress_model.json"
SCALER_PATH = MODEL_DIR / "scaler.json"


# ==========================================================
# PREPROCESSING CONFIGURATION
# ==========================================================

FS = 128
LOWCUT = 1
HIGHCUT = 40
FILTER_ORDER = 4

EXPECTED_CHANNELS = 32
EXPECTED_SAMPLES = 3200
EXPECTED_FEATURES = 256


# ==========================================================
# LOAD MODEL + SCALER ONCE
# ==========================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"XGBoost model not found: {MODEL_PATH}"
    )

if not SCALER_PATH.exists():
    raise FileNotFoundError(
        f"Scaler not found: {SCALER_PATH}"
    )


stress_model = xgb.XGBClassifier()
stress_model.load_model(MODEL_PATH)

with SCALER_PATH.open() as scaler_file:
    scaler_metadata = json.load(scaler_file)

scaler_mean = np.asarray(scaler_metadata["mean"], dtype=np.float64)
scaler_scale = np.asarray(scaler_metadata["scale"], dtype=np.float64)


# ==========================================================
# BAND-PASS FILTER
# ==========================================================

def bandpass_filter(
    signal_data: np.ndarray,
    lowcut: float = LOWCUT,
    highcut: float = HIGHCUT,
    fs: float = FS,
    order: int = FILTER_ORDER,
) -> np.ndarray:
    """
    Apply a Butterworth band-pass filter.
    """

    nyquist = 0.5 * fs

    low = lowcut / nyquist
    high = highcut / nyquist

    frequencies = np.fft.rfftfreq(signal_data.size, d=1 / fs)
    spectrum = np.fft.rfft(signal_data)
    spectrum[(frequencies < lowcut) | (frequencies > highcut)] = 0
    return np.fft.irfft(spectrum, n=signal_data.size)


# ==========================================================
# PREPROCESS EEG
# ==========================================================

def preprocess_eeg(eeg_signal: np.ndarray) -> np.ndarray:
    """
    Apply the same preprocessing used during model training.

    Expected input:
        (32, 3200)

    Returns:
        normalized EEG with shape (32, 3200)
    """

    eeg_signal = np.asarray(eeg_signal, dtype=np.float64)

    if eeg_signal.ndim != 2:
        raise ValueError(
            f"EEG data must be 2-dimensional. "
            f"Received shape: {eeg_signal.shape}"
        )

    if eeg_signal.shape != (
        EXPECTED_CHANNELS,
        EXPECTED_SAMPLES,
    ):
        raise ValueError(
            f"Expected EEG shape "
            f"({EXPECTED_CHANNELS}, {EXPECTED_SAMPLES}), "
            f"but received {eeg_signal.shape}"
        )

    # ----------------------------
    # Band-pass filter
    # ----------------------------

    filtered_signal = np.zeros_like(eeg_signal, dtype=np.float64)

    for channel in range(eeg_signal.shape[0]):
        filtered_signal[channel] = bandpass_filter(
            eeg_signal[channel]
        )

    # ----------------------------
    # Channel-wise normalization
    # ----------------------------

    normalized_signal = (
        filtered_signal
        - filtered_signal.mean(
            axis=1,
            keepdims=True,
        )
    ) / (
        filtered_signal.std(
            axis=1,
            keepdims=True,
        )
    )

    return normalized_signal


# ==========================================================
# FEATURE EXTRACTION
# ==========================================================

def extract_features(eeg_signal: np.ndarray) -> np.ndarray:
    """
    Extract the exact 8 statistical features used during training.

    For every channel:

        1. Mean
        2. Standard deviation
        3. Variance
        4. RMS
        5. Maximum
        6. Minimum
        7. Skewness
        8. Kurtosis

    32 channels × 8 features = 256 features
    """

    eeg_signal = np.asarray(eeg_signal)

    features = []

    for channel in eeg_signal:
        mean = np.mean(channel)
        centered = channel - mean
        standard_deviation = np.std(channel)
        variance = np.var(channel)
        safe_standard_deviation = max(standard_deviation, np.finfo(float).eps)
        features.extend([
            mean,
            standard_deviation,
            variance,
            np.sqrt(np.mean(channel ** 2)),
            np.max(channel),
            np.min(channel),
            np.mean(centered ** 3) / safe_standard_deviation ** 3,
            np.mean(centered ** 4) / safe_standard_deviation ** 4 - 3,
        ])

    feature_vector = np.asarray(features, dtype=np.float64)

    if feature_vector.shape != (EXPECTED_FEATURES,):
        raise ValueError(
            f"Expected {EXPECTED_FEATURES} features, "
            f"but generated {feature_vector.shape}"
        )

    return feature_vector


# ==========================================================
# LOAD EEG FROM .MAT
# ==========================================================

def load_mat_eeg(mat_path: str | Path) -> np.ndarray:
    """
    Load EEG data from a MATLAB .mat file.

    The notebook stores the EEG signal under the key:
        'Data'
    """

    mat_path = Path(mat_path)

    if not mat_path.exists():
        raise FileNotFoundError(
            f"EEG file not found: {mat_path}"
        )

    mat_data = loadmat(mat_path)

    if "Data" not in mat_data:
        available = [
            key
            for key in mat_data.keys()
            if not key.startswith("__")
        ]

        raise KeyError(
            f"'Data' variable not found in {mat_path}. "
            f"Available variables: {available}"
        )

    eeg_signal = np.asarray(
        mat_data["Data"],
        dtype=np.float64,
    )

    return eeg_signal


# ==========================================================
# PREDICT FROM EEG ARRAY
# ==========================================================

def predict_stress(eeg_signal: np.ndarray) -> dict:
    """
    Run the complete stress prediction pipeline.

    Returns:
        {
            "label": "Stress" / "Non-Stress",
            "prediction": 0 / 1,
            "stress_probability": float,
            "non_stress_probability": float
        }
    """

    # 1. Preprocess
    normalized_signal = preprocess_eeg(eeg_signal)

    # 2. Extract 256 features
    features = extract_features(normalized_signal)

    # 3. Convert to 2D for sklearn/xgboost
    features_2d = features.reshape(
        1,
        -1,
    )

    # 4. Scale with the SAVED scaler
    scaled_features = (features_2d - scaler_mean) / scaler_scale

    # 5. XGBoost prediction
    prediction = stress_model.predict(
        scaled_features
    )

    probabilities = stress_model.predict_proba(
        scaled_features
    )[0]

    predicted_class = int(prediction[0])

    non_stress_probability = float(
        probabilities[0]
    )

    stress_probability = float(
        probabilities[1]
    )

    label = (
        "Stress"
        if predicted_class == 1
        else "Non-Stress"
    )

    return {
        "label": label,
        "prediction": predicted_class,
        "stress_probability": stress_probability,
        "non_stress_probability": non_stress_probability,
    }


# ==========================================================
# PREDICT DIRECTLY FROM .MAT FILE
# ==========================================================

def predict_stress_from_mat(
    mat_path: str | Path,
) -> dict:
    """
    Load a .mat EEG recording and run stress prediction.
    """

    eeg_signal = load_mat_eeg(mat_path)

    return predict_stress(eeg_signal)


# ==========================================================
# BASIC MODEL VALIDATION
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NEUROSENSE STRESS INFERENCE")
    print("=" * 60)

    print("Model:", MODEL_PATH)
    print("Scaler:", SCALER_PATH)

    print()
    print("Model features:", stress_model.n_features_in_)
    print("Model classes:", stress_model.classes_)
    print("Scaler features:", len(scaler_mean))

    print()
    print("Preprocessing:")
    print("Sampling frequency:", FS)
    print("Band:", LOWCUT, "-", HIGHCUT, "Hz")
    print("Expected EEG shape:",
          (EXPECTED_CHANNELS, EXPECTED_SAMPLES))

    print()
    print("Stress inference module loaded successfully.")
