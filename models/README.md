# Models Directory

When you run the training notebook on Google Colab (`gnani_scam_detector_colab.ipynb`), it will export a zip archive named `gnani_scam_models.zip`.

### To integrate your trained models:
1. Extract the contents of `gnani_scam_models.zip` directly into this `models/` directory.
2. The folder structure should look like this:
   ```
   models/
   ├── setfit_intent_model/       <-- Fine-tuned SetFit / MiniLM model files
   │   ├── model_head.pkl
   │   ├── config.json
   │   └── ...
   ├── xgboost_scam_model.json    <-- Trained XGBoost Stacking model
   └── feature_config.json        <-- Feature weights and thresholds
   ```
3. Restart or reload the server. The web app will automatically detect these files, log:
   `"🚀 SUCCESSFULLY LOADED TRAINED COLAB MODELS!"`, and switch to your trained model inference!
