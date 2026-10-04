import mlflow, datetime, os, pickle
from joblib import dump
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import sys
from sklearn.ensemble import RandomForestClassifier
import argparse

sys.path.insert(0, os.path.abspath('..'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", type=str, required=True, help="Timestamp from GitHub Actions")
    args = parser.parse_args()

    # Access the timestamp
    timestamp = args.timestamp

    # Use the timestamp in your script
    print(f"Timestamp received from GitHub Actions: {timestamp}")

    # Load a real dataset and hold out 20% for evaluation
    X, y = load_breast_cancer(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Save the held-out test set so evaluate_model.py scores on unseen data
    os.makedirs('data', exist_ok=True)
    with open('data/X_test.pickle', 'wb') as f:
        pickle.dump(X_test, f)
    with open('data/y_test.pickle', 'wb') as f:
        pickle.dump(y_test, f)

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    dataset_name = "Breast Cancer Wisconsin"
    current_time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    experiment_name = f"{dataset_name}_{current_time}"
    experiment_id = mlflow.create_experiment(f"{experiment_name}")

    with mlflow.start_run(experiment_id=experiment_id,
                        run_name= f"{dataset_name}"):

        params = {
                    "dataset_name": dataset_name,
                    "number of datapoint": X_train.shape[0],
                    "number of dimensions": X_train.shape[1],
                    "n_estimators": 200,
                    "max_depth": 8}

        mlflow.log_params(params)

        forest = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=0)
        forest.fit(X_train, y_train)

        y_predict = forest.predict(X_train)
        mlflow.log_metrics({'Train Accuracy': accuracy_score(y_train, y_predict),
                            'Train F1 Score': f1_score(y_train, y_predict)})

        # After retraining the model
        model_version = f'model_{timestamp}'  # Use a timestamp as the version
        model_filename = f'{model_version}_dt_model.joblib'
        dump(forest, model_filename)
