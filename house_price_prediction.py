"""
House Price Prediction - Linear Regression
==========================================
Trains a Linear Regression model to predict house prices, compares it with a
baseline and two other models, analyses the residuals, and saves the trained
model, metrics and plots.

Usage:
    python house_price_prediction.py
    python house_price_prediction.py --input house_price.csv --target price
    python house_price_prediction.py --log-target     # helps when prices are skewed
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sns.set_theme(style="whitegrid")


# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Train a house price prediction model.")
    p.add_argument("--input", default="house_price.csv", help="Path to input CSV file")
    p.add_argument("--target", default="price", help="Name of the target column")
    p.add_argument("--output-dir", default="output", help="Folder for model, metrics and plots")
    p.add_argument("--test-size", type=float, default=0.2, help="Fraction of data for testing")
    p.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    p.add_argument("--log-target", action="store_true",
                   help="Train on log(price); useful when prices are right-skewed")
    p.add_argument("--show", action="store_true", help="Display plots interactively")
    return p.parse_args()


def load_data(filepath: str, target: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        sys.exit(f"Error: file not found -> {filepath}")

    df = pd.read_csv(path)
    if target not in df.columns:
        sys.exit(f"Error: target column '{target}' not found. Available: {list(df.columns)}")
    if not pd.api.types.is_numeric_dtype(df[target]):
        sys.exit(f"Error: target column '{target}' must be numeric.")

    before = len(df)
    df = df.drop_duplicates()
    if len(df) < before:
        print(f"Removed {before - len(df)} duplicate row(s).")

    before = len(df)
    df = df.dropna(subset=[target])
    if len(df) < before:
        print(f"Dropped {before - len(df)} row(s) with missing target values.")

    if len(df) < 20:
        sys.exit("Error: not enough rows to train and evaluate a model.")
    return df.reset_index(drop=True)


def build_model(X: pd.DataFrame, regressor, log_target: bool = False) -> Pipeline:
    """Preprocessing + model in one Pipeline.

    Numeric: median-impute + scale.  Categorical: most-frequent-impute + one-hot.
    Because this lives inside the Pipeline, it is fitted on training data only,
    so there is no data leakage.
    """
    numeric = X.select_dtypes(include=np.number).columns.tolist()
    categorical = X.select_dtypes(exclude=np.number).columns.tolist()

    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                          ("scaler", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])

    if log_target:
        regressor = TransformedTargetRegressor(
            regressor=regressor, func=np.log1p, inverse_func=np.expm1)
    return Pipeline([("preprocessor", preprocessor), ("model", regressor)])


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------
def regression_metrics(y_true, y_pred) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def compare_models(X_train, X_test, y_train, y_test, seed, log_target) -> pd.DataFrame:
    """Baseline vs Linear Regression vs Ridge vs Random Forest."""
    candidates = {
        "Baseline (mean)": DummyRegressor(strategy="mean"),
        "Linear Regression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=seed, n_jobs=-1),
    }
    rows = []
    for name, reg in candidates.items():
        model = build_model(X_train, reg, log_target)
        cv = cross_validate(model, X_train, y_train, cv=5,
                            scoring=("r2", "neg_root_mean_squared_error"))
        model.fit(X_train, y_train)
        m = regression_metrics(y_test, model.predict(X_test))
        rows.append({
            "model": name,
            "cv_r2_mean": cv["test_r2"].mean(),
            "cv_r2_std": cv["test_r2"].std(),
            "cv_rmse": -cv["test_neg_root_mean_squared_error"].mean(),
            "test_mae": m["mae"], "test_rmse": m["rmse"], "test_r2": m["r2"],
        })
    return pd.DataFrame(rows).set_index("model")


# --------------------------------------------------------------------------
# Plots
# --------------------------------------------------------------------------
def finish(fig, path: Path, show: bool):
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_actual_vs_predicted(y_test, y_pred, out: Path, show: bool):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(y_test, y_pred, alpha=0.6, edgecolor="k")
    lo, hi = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
    ax.plot([lo, hi], [lo, hi], "r--", label="Perfect prediction")
    ax.set(title="Actual vs Predicted House Prices", xlabel="Actual price", ylabel="Predicted price")
    ax.legend()
    finish(fig, out / "actual_vs_predicted.png", show)


def plot_residuals(y_test, y_pred, out: Path, show: bool):
    resid = y_test - y_pred
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(y_pred, resid, alpha=0.6, edgecolor="k")
    axes[0].axhline(0, color="red", ls="--")
    axes[0].set(title="Residuals vs Predicted", xlabel="Predicted price", ylabel="Residual (actual - predicted)")
    sns.histplot(resid, kde=True, ax=axes[1], color="#2a6fbb")
    axes[1].set(title="Distribution of Residuals", xlabel="Residual")
    finish(fig, out / "residual_analysis.png", show)


def plot_coefficients(pipeline: Pipeline, out: Path, show: bool, top: int = 15):
    names = pipeline.named_steps["preprocessor"].get_feature_names_out()
    reg = pipeline.named_steps["model"]
    reg = getattr(reg, "regressor_", reg)  # unwrap if log-target is used
    coefs = pd.Series(reg.coef_, index=names)
    coefs = coefs.reindex(coefs.abs().sort_values().index).tail(top)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(coefs.index, coefs.values, color=np.where(coefs.values > 0, "#2a9d8f", "#e76f51"))
    ax.axvline(0, color="black", lw=0.8)
    ax.set(title=f"Top {top} Linear Regression Coefficients (scaled features)", xlabel="Coefficient")
    finish(fig, out / "feature_coefficients.png", show)
    return coefs.sort_values(ascending=False)


def plot_model_comparison(table: pd.DataFrame, out: Path, show: bool):
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(table.index, table["test_r2"], color="#2a6fbb")
    ax.bar_label(bars, fmt="%.3f", padding=3)
    ax.set(title="Test R² by Model", ylabel="R² (higher is better)")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    finish(fig, out / "model_comparison.png", show)


# --------------------------------------------------------------------------
def main():
    args = parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not args.show:
        matplotlib.use("Agg")

    df = load_data(args.input, args.target)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns.")
    print(df.head())

    X, y = df.drop(columns=[args.target]), df[args.target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed)

    # 1) Compare models (cross-validation on train + final test scores)
    table = compare_models(X_train, X_test, y_train, y_test, args.seed, args.log_target)
    print("\nModel comparison:")
    print(table.round(4).to_string())
    table.round(4).to_csv(out / "model_comparison.csv")

    # 2) Final model: Linear Regression
    model = build_model(X_train, LinearRegression(), args.log_target)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics = regression_metrics(y_test, y_pred)

    print("\nLinear Regression - test set performance:")
    print(f"  MAE:   {metrics['mae']:,.2f}")
    print(f"  RMSE:  {metrics['rmse']:,.2f}")
    print(f"  R²:    {metrics['r2']:.4f}")

    # 3) Plots
    plot_actual_vs_predicted(y_test, y_pred, out, args.show)
    plot_residuals(y_test, y_pred, out, args.show)
    coefs = plot_coefficients(model, out, args.show)
    plot_model_comparison(table, out, args.show)
    print("\nStrongest positive coefficients:")
    print(coefs.head(5).round(3).to_string())

    # 4) Save model + metrics
    joblib.dump(model, out / "house_price_model.joblib")
    (out / "metrics.json").write_text(json.dumps({
        "rows": len(df), "test_size": args.test_size, "seed": args.seed,
        "log_target": args.log_target, **metrics}, indent=2))
    print(f"\nSaved model, metrics and plots to '{out}/'")

    # 5) Example prediction on a house the model has NOT seen
    sample = X_test.iloc[[0]]
    print(f"Example (unseen house): predicted {model.predict(sample)[0]:,.2f}, "
          f"actual {y_test.iloc[0]:,.2f}")


if __name__ == "__main__":
    main()
