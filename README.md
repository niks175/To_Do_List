# House Price Prediction Using Linear Regression

A machine learning project that predicts house prices with **Linear Regression** in Python (scikit-learn). It covers the full workflow: data loading and cleaning, a leak-free preprocessing pipeline, model comparison, evaluation, residual analysis, and a saved model you can use on new houses.

## Project Goal

Predict a house's sale price from its features (size, rooms, location, and so on) and measure how reliable those predictions are.

## Dataset

- **Source:** *[add dataset name and link, e.g. Kaggle]*
- **Rows / columns:** *[add after running]*
- **Target:** `price`

Put your CSV in the project folder as `house_price.csv`, or pass a different file with `--input`.

## Project Structure

```
├── house_price_prediction.py   # Train, compare, evaluate and save the model
├── predict.py                  # Predict prices for new houses
├── house_price.csv             # Dataset
├── requirements.txt
├── output/                     # Created when you run the script
│   ├── house_price_model.joblib
│   ├── metrics.json
│   ├── model_comparison.csv
│   └── *.png                   # Plots
└── README.md
```

## Method

1. **Load and validate** the data: checks the target column, removes duplicates and rows with a missing price.
2. **Preprocess inside a Pipeline** (so nothing leaks from the test set):
   - Numeric columns: fill missing values with the median, then standardise.
   - Categorical columns: fill with the most frequent value, then one-hot encode.
3. **Split** into 80% training and 20% testing (fixed random seed).
4. **Compare models** with 5-fold cross-validation and a final test score: a mean-price baseline, Linear Regression, Ridge and Random Forest.
5. **Evaluate** the Linear Regression model with MAE, RMSE and R².
6. **Check the model's assumptions** with residual plots, and inspect the largest coefficients.
7. **Save** the trained pipeline, metrics and plots.

## Getting Started

```bash
git clone https://github.com/niks175/Qskill-House-Price-Prediction-Using-Linear-Regression.git
cd Qskill-House-Price-Prediction-Using-Linear-Regression
pip install -r requirements.txt
python house_price_prediction.py
```

Options:

```bash
python house_price_prediction.py --input house_price.csv --target price
python house_price_prediction.py --log-target    # train on log(price) if prices are skewed
python house_price_prediction.py --test-size 0.3 --seed 7
```

### Predict prices for new houses

Create a CSV with the same feature columns as the training data (no `price` column), then run:

```bash
python predict.py --input new_houses.csv --output predictions.csv
```

## Results

> Run the script and copy your numbers from `output/model_comparison.csv` here.

| Model | CV R² | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Baseline (mean) | | | | |
| **Linear Regression** | | | | |
| Ridge | | | | |
| Random Forest | | | | |

**How to read the metrics**
- **MAE:** the average size of the error, in price units.
- **RMSE:** like MAE but punishes large errors more.
- **R²:** the share of price variation the model explains (1.0 is perfect; 0 is no better than guessing the average).

## Visualizations

| | |
|---|---|
| ![Actual vs predicted](output/actual_vs_predicted.png) | ![Residual analysis](output/residual_analysis.png) |
| ![Feature coefficients](output/feature_coefficients.png) | ![Model comparison](output/model_comparison.png) |

## Key Insights

*Write 3 to 4 findings from your own results, for example which features have the largest coefficients and how Linear Regression compares with the baseline and Random Forest.*

## Limitations

- Linear Regression assumes a straight-line relationship between features and price, and can miss complex patterns.
- Results come from one dataset; prices in other cities or years may behave differently.
- Outliers and strongly correlated features can distort coefficients.

## Tech Stack

Python, pandas, NumPy, scikit-learn, Matplotlib, Seaborn, joblib

## Contributing

Suggestions and improvements are welcome. Open an issue or submit a pull request.
