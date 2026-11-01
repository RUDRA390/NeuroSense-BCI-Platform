# Motor Imagery EEGNet -- Flask Deployment

## What changed vs. your notebook

Your notebook trains and saves 90 files (9 subjects x 10 CV folds). That
structure exists for *evaluating* the model reliably, not for *shipping* it.
For deployment you need one deployable file, with its exact preprocessing
stats saved alongside it. `colab_package_export_snippet.py` produces that:

- `generic_eegnet_package.pt` -- one EEGNet trained on **pooled data from all
  9 subjects**. This is the model a real website should use, since a new
  visitor is not any of the 9 recorded subjects, and none of the 90
  subject-specific fold models will reliably transfer to them.
- `A01_final_package.pt` ... `A09_final_package.pt` (optional) -- one
  finalized model per subject, trained on that subject's full data (no
  held-out folds). Useful only if you want to demo against the known
  dataset subjects specifically, selectable in the dropdown.

Each `.pt` package bundles the model weights **and** the frequency band,
per-channel normalization stats, and Euclidean Alignment matrix used during
training, so Flask preprocesses incoming trials exactly the way the model
was trained -- it never has to guess or re-derive those stats.

## Setup

1. In your Colab notebook, after `main()` has finished, paste and run
   `colab_package_export_snippet.py` as a new cell. It downloads
   `deploy_models.zip`.
2. Unzip it and copy the `.pt` files into this folder's `models/` directory.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the server:
   ```
   python app.py
   ```
5. Open `http://localhost:5000` in a browser.

## Expected input format

The UI/`/predict` endpoint expects a `.npy` file containing **one trial**:
a NumPy array of shape `(22, 1000)` -- 22 EEG channels (BCI IV 2a montage,
EOG channels already removed, same channel order as training), sampled at
250 Hz, covering the 4 seconds immediately following the motor-imagery cue
(matches `tmin=0.0` to `tmax=4.0` in your `Config`). The backend applies the
same bandpass filter, optional Euclidean Alignment, per-channel
normalization, and center-crop to 3 seconds (750 samples) that training
used, then runs EEGNet and returns the predicted class plus per-class
probabilities.

If you're not extracting trials from raw recordings yourself yet, you can
build a quick test `.npy` from one of your notebook's existing epochs:
```python
np.save("demo_trial.npy", X_test[0])  # X_test from build_subject_data(...)
```

## What this does NOT do yet

- No live/streaming EEG device integration -- this expects a pre-extracted,
  cue-aligned trial. Hooking up a real headset needs an acquisition layer
  that timestamps the cue and slices out this same 4-second window.
- No per-new-user calibration/fine-tuning. The generic model is a fixed,
  non-personalized baseline. If you want per-user calibration later (a short
  motor-imagery session from each new visitor, fine-tuned on top of the
  generic model), that would be a new `/calibrate` endpoint reusing
  `train_final_model()` from the export snippet -- ask if you want that
  built next.
