import json
import os
from datetime import datetime, timezone

import numpy as np
import tensorflow as tf
from sklearn import datasets
from sklearn.model_selection import train_test_split

MODEL_DIR = os.environ.get('MODEL_DIR', '.')

if __name__ == '__main__':
    # Fix the seeds so every image build trains the same model
    tf.keras.utils.set_random_seed(42)

    # Load the Iris dataset
    iris = datasets.load_iris()
    X, y = iris.data.astype(np.float32), iris.target

    # Split the dataset into training and testing sets (stratified so each class is balanced)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    # Standardize features INSIDE the model with a Normalization layer.
    # The original lab used a StandardScaler here but never saved it, so the
    # server fed raw measurements to a model trained on scaled ones and almost
    # every prediction came out as "Virginica". Baking the scaling into the
    # model means the saved .keras file accepts raw centimetre values.
    normalizer = tf.keras.layers.Normalization(name='standardize')
    normalizer.adapt(X_train)

    # Build a simple TensorFlow model
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(4,)),
        normalizer,
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # Hold out part of the training set for validation; the test set is only
    # used once at the end. Stop early once validation loss stops improving.
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=15, restore_best_weights=True)
    history = model.fit(X_train, y_train, epochs=200, validation_split=0.2,
                        callbacks=[early_stop], verbose=2)

    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test accuracy: {test_accuracy:.4f}  (loss {test_loss:.4f})")

    model.save(os.path.join(MODEL_DIR, 'my_model.keras'))

    # Save training metrics next to the model so the server can report them
    metrics = {
        'test_accuracy': round(float(test_accuracy), 4),
        'test_loss': round(float(test_loss), 4),
        'epochs_trained': len(history.history['loss']),
        'train_samples': int(len(X_train)),
        'test_samples': int(len(X_test)),
        'trained_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }
    with open(os.path.join(MODEL_DIR, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    print("Model was trained and saved")
