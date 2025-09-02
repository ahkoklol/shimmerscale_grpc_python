import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

class StockForecastingServiceML:
    def __init__(self, excel_service):
        self.excel_service = excel_service
        self.model = None
        self.offset = 1.0  # small offset to handle negative EPS

    def prepare_features(self, df, target_years=5, max_lag=5):
        """
        Prepare lag features and target for 5-year EPS growth prediction.
        Negative EPS is handled via offset.
        """
        df = df.sort_values("year").reset_index(drop=True)

        # Lag features
        for lag in range(1, max_lag + 1):
            df[f"eps_lag_{lag}"] = df["eps"].shift(lag)
            df[f"revenue_lag_{lag}"] = df["total_revenue"].shift(lag)
            df[f"net_income_lag_{lag}"] = df["net_income"].shift(lag)

        # Target: 5-year EPS growth with offset to avoid negative/zero issues
        df["eps_shifted"] = df["eps"] + self.offset
        df["eps_future_shifted"] = df["eps"].shift(-target_years) + self.offset
        df["eps_growth_5y"] = (df["eps_future_shifted"] / df["eps_shifted"]) ** (1 / target_years) - 1

        df = df.dropna().reset_index(drop=True)
        feature_cols = [c for c in df.columns if "lag" in c]
        X = df[feature_cols]
        y = df["eps_growth_5y"]

        return X, y, df["year"]

    def train_model(self, ticker):
        df = self.excel_service._load_excel(ticker)
        X, y, years = self.prepare_features(df)

        if len(X) < 5:
            print(f"[ML] Not enough data to train model for {ticker}")
            return None

        tscv = TimeSeriesSplit(n_splits=3)
        preds, actuals = [], []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model = xgb.XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            preds.extend(y_pred)
            actuals.extend(y_test)

        mape = mean_absolute_percentage_error(actuals, preds) * 100
        rmse = np.sqrt(mean_squared_error(actuals, preds))
        print(f"[ML] Cross-validated MAPE={mape:.2f}%, RMSE={rmse:.2f}")

        # Train final model on all data
        self.model = xgb.XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        self.model.fit(X, y)
        return self.model

    def predict_5y_growth(self, ticker, recent_years=5):
        df = self.excel_service._load_excel(ticker)
        df = df.sort_values("year").reset_index(drop=True)
        df_recent = df.tail(recent_years)

        # Build features for prediction using most recent years
        X_pred = []
        for lag in range(1, recent_years + 1):
            X_pred.append(df_recent.iloc[-lag]["eps"])
            X_pred.append(df_recent.iloc[-lag]["total_revenue"])
            X_pred.append(df_recent.iloc[-lag]["net_income"])

        X_pred = np.array(X_pred).reshape(1, -1)

        if self.model is None:
            self.train_model(ticker)

        growth_pred = self.model.predict(X_pred)[0]
        print(f"[ML] Predicted 5-year EPS CAGR for {ticker} = {growth_pred:.4f}")
        return growth_pred
