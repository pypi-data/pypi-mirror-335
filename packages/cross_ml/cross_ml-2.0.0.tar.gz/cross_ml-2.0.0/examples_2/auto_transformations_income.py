import json

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, load_wine
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from cross import CrossTransformer, auto_transform
from cross.auto_parameters.shared import evaluate_model
from sklearn.ensemble import RandomForestClassifier


def load_data():
    file_path = "examples_2/adult.data"
    column_names = ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status",
                "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss",
                "hours-per-week", "native-country", "income"]

    # Cargar el dataset desde el archivo
    df = pd.read_csv(file_path, names=column_names, na_values=" ?", skipinitialspace=True)
    df = df.rename(columns={"income": "target"})

    le = LabelEncoder()
    df["target"] = le.fit_transform(df["target"])

    return df



if __name__ == "__main__":
    df = load_data()
    x, y = df.drop(columns="target"), df["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.33, random_state=42
    )

    # model = KNeighborsClassifier()
    model = RandomForestClassifier()
    scoring = "roc_auc"  # "accuracy"
    direction = "maximize"

    # Evalute baseline model
    x_base = x.copy()
    x_base = x_base.fillna(0)
    score = evaluate_model(x_base, y, model, scoring)
    print(f"Baseline score: {score}")

    # Auto transformations
    transformations = auto_transform(x_train, y_train, model, scoring, direction)

    # Evalute model with transformation
    transformer = CrossTransformer(transformations)
    x_train = transformer.fit_transform(x_train, y_train)
    x_test = transformer.transform(x_test, y_test)

    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = f1_score(y_test, y_pred)
    score2 = evaluate_model(x, y, model, scoring, transformer=transformer)

    print(f"Transformations score: {score} - {score2}")

    print(json.dumps(transformations, indent=4))



# Evaluate 1056
# Evaluate 1577
# Evaluate 1227
# Evaluate 1115

# quantile vs normalization

