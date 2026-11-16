import json
import os

from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np

app = Flask(__name__, static_folder='statics')

# Settings come from environment variables so the same image can be configured
# at `docker run` time. PORT defaults to 80 to match EXPOSE 80 in the dockerfile
# and the "80:80" mapping in docker-compose.yml (the original app listened on
# 4000, so neither setup could reach it).
PORT = int(os.environ.get('PORT', 80))
MODEL_PATH = os.environ.get('MODEL_PATH', 'my_model.keras')
METRICS_PATH = os.environ.get('METRICS_PATH', 'metrics.json')

# Load the TensorFlow model
model = tf.keras.models.load_model(MODEL_PATH)
class_labels = ['Setosa', 'Versicolor', 'Virginica']
feature_names = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

# Training metrics written by model_training.py (optional)
try:
    with open(METRICS_PATH) as f:
        model_metrics = json.load(f)
except FileNotFoundError:
    model_metrics = None


def parse_features(data):
    """Read the four measurements from a request, or raise ValueError."""
    missing = [name for name in feature_names if name not in data or data[name] in ('', None)]
    if missing:
        raise ValueError(f"Missing field(s): {', '.join(missing)}")
    values = []
    for name in feature_names:
        try:
            value = float(data[name])
        except (TypeError, ValueError):
            raise ValueError(f"'{name}' must be a number")
        if not 0 < value < 30:
            raise ValueError(f"'{name}' must be between 0 and 30 cm")
        values.append(value)
    return values


@app.route('/')
def home():
    return "Welcome to the Iris Classifier API!"

@app.route('/health')
def health():
    # Used by the Docker HEALTHCHECK and handy for checking which model is loaded
    return jsonify({"status": "ok", "model": MODEL_PATH, "metrics": model_metrics})

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Accept both the HTML form and JSON bodies (e.g. from curl or another service)
        data = request.get_json(silent=True) or request.form
        try:
            features = parse_features(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Perform the prediction
        input_data = np.array(features, dtype=np.float32)[np.newaxis, ]
        probabilities = model.predict(input_data, verbose=0)[0]
        best = int(np.argmax(probabilities))

        # Return the predicted class plus how confident the model is
        return jsonify({
            "predicted_class": class_labels[best],
            "confidence": round(float(probabilities[best]), 4),
            "probabilities": {label: round(float(p), 4)
                              for label, p in zip(class_labels, probabilities)},
        })
    return render_template('predict.html')

if __name__ == "__main__":
    # debug=False: the debugger lets anyone who can reach the port run code
    app.run(debug=False, host='0.0.0.0', port=PORT)
