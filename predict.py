"""
Predict house prices for new houses using the trained model.

Usage:
    python predict.py --input new_houses.csv --output predictions.csv

new_houses.csv must have the same feature columns as the training data
(without the price column).
"""

import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Predict prices with the trained model.")
    p.add_argument("--model", default="output/house_price_model.joblib")
    p.add_argument("--input", required=True, help="CSV of houses to price")
    p.add_argument("--output", default="predictions.csv")
    args = p.parse_args()

    if not Path(args.model).exists():
        sys.exit(f"Error: model not found -> {args.model}. Run house_price_prediction.py first.")
    if not Path(args.input).exists():
        sys.exit(f"Error: file not found -> {args.input}")

    model = joblib.load(args.model)
    df = pd.read_csv(args.input)
    df["predicted_price"] = model.predict(df).round(2)
    df.to_csv(args.output, index=False)
    print(df.head())
    print(f"\nSaved {len(df)} predictions to {args.output}")


if __name__ == "__main__":
    main()
