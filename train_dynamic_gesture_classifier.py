#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
from pathlib import Path

import numpy as np
import tensorflow as tf


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset',
        default='model/dynamic_gesture_classifier/dynamic_gesture_dataset.csv',
    )
    parser.add_argument(
        '--label',
        default='model/dynamic_gesture_classifier/dynamic_gesture_label.csv',
    )
    parser.add_argument('--output', default='model/dynamic_gesture_classifier')
    parser.add_argument('--sequence_length', type=int, default=30)
    parser.add_argument('--feature_dim', type=int, default=126)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--validation_split', type=float, default=0.2)
    return parser.parse_args()


def load_labels(label_path):
    with open(label_path, encoding='utf-8-sig') as f:
        return [row[0] for row in csv.reader(f) if row]


def load_dataset(dataset_path, sequence_length, feature_dim):
    rows = np.loadtxt(
        dataset_path,
        delimiter=',',
        dtype=np.float32,
        encoding='utf-8-sig',
    )
    if rows.ndim == 1:
        rows = np.expand_dims(rows, axis=0)

    y = rows[:, 0].astype(np.int32)
    x = rows[:, 1:].reshape((-1, sequence_length, feature_dim))
    return x, y


def build_model(sequence_length, feature_dim, num_classes):
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(sequence_length, feature_dim)),
        tf.keras.layers.Conv1D(64, 3, padding='same', activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Conv1D(64, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Conv1D(128, 3, padding='same', activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax'),
    ])
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'],
    )
    return model


def train_validation_split(x, y, validation_split, seed=42):
    rng = np.random.default_rng(seed)
    train_indexes = []
    val_indexes = []

    for label_id in np.unique(y):
        indexes = np.where(y == label_id)[0]
        rng.shuffle(indexes)
        val_count = max(1, int(round(len(indexes) * validation_split)))
        val_indexes.extend(indexes[:val_count])
        train_indexes.extend(indexes[val_count:])

    rng.shuffle(train_indexes)
    rng.shuffle(val_indexes)
    return x[train_indexes], y[train_indexes], x[val_indexes], y[val_indexes]


def save_tflite_model(model, output_path):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(tflite_model)


def main():
    args = get_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    labels = load_labels(args.label)
    x, y = load_dataset(args.dataset, args.sequence_length, args.feature_dim)
    x_train, y_train, x_val, y_val = train_validation_split(
        x,
        y,
        args.validation_split,
    )
    model = build_model(args.sequence_length, args.feature_dim, len(labels))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
        )
    ]

    history = model.fit(
        x_train,
        y_train,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_data=(x_val, y_val),
        callbacks=callbacks,
        shuffle=True,
    )

    h5_path = output_dir / 'dynamic_gesture_classifier.h5'
    tflite_path = output_dir / 'dynamic_gesture_classifier.tflite'
    model.save(h5_path)
    save_tflite_model(model, tflite_path)

    last_acc = history.history['accuracy'][-1]
    last_val_acc = history.history.get('val_accuracy', [0.0])[-1]
    print(
        f'Saved: {h5_path}, {tflite_path}. accuracy={last_acc:.4f}, val_accuracy={last_val_acc:.4f}',
        flush=True,
    )


if __name__ == '__main__':
    main()
