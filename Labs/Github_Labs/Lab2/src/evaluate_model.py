import pickle, os, json
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib, sys
import argparse

sys.path.insert(0, os.path.abspath('..'))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", type=str, required=True, help="Timestamp from GitHub Actions")
    args = parser.parse_args()

    # Access the timestamp
    timestamp = args.timestamp
    try:
        model_version = f'model_{timestamp}_dt_model'  # Use a timestamp as the version
        model = joblib.load(f'{model_version}.joblib')
    except Exception:
        raise ValueError('Failed to catching the latest model')

    try:
        # Load the held-out test set saved by train_model.py
        with open('data/X_test.pickle', 'rb') as f:
            X = pickle.load(f)
        with open('data/y_test.pickle', 'rb') as f:
            y = pickle.load(f)
    except Exception:
        raise ValueError('Failed to catching the data')

    y_predict = model.predict(X)
    metrics = {"Accuracy": accuracy_score(y, y_predict),
               "F1_Score": f1_score(y, y_predict),
               "Precision": precision_score(y, y_predict),
               "Recall": recall_score(y, y_predict)}
    print(json.dumps(metrics, indent=4))

    # Save metrics to a JSON file
    with open(f'{timestamp}_metrics.json', 'w') as metrics_file:
        json.dump(metrics, metrics_file, indent=4)
