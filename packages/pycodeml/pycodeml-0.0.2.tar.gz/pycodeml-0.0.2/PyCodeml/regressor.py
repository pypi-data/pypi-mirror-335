import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

class RegressorTrainer:
    def __init__(self, dataset, target_column):
        """
        Initialize the trainer with a dataset and target column.
        Args:
            dataset (pd.DataFrame): Clean numeric dataset.
            target_column (str): Name of the column to predict.
        """
        self.dataset = dataset
        self.target_column = target_column
        self.models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(),
            "Support Vector Machine": SVR(),
            "Decision Tree": DecisionTreeRegressor(),
            "Gradient Boosting": GradientBoostingRegressor(),
            "Ridge Regression": Ridge(),
            "Lasso Regression": Lasso(),
            "Elastic Net": ElasticNet(),
        }
        self.best_model = None
        self.best_r2 = float('-inf')

    def train_and_get_best_model(self):
        """
        Train multiple models and return the one with the highest R² score.
        Returns:
            Trained model with the best R² score.
        """
        X = self.dataset.drop(columns=[self.target_column])
        y = self.dataset[self.target_column]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        for model_name, model in self.models.items():
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            r2 = r2_score(y_test, predictions)

            if r2 > self.best_r2:
                self.best_r2 = r2
                self.best_model = model

        print(f"Best Model: {type(self.best_model).__name__} with R²: {self.best_r2:.4f}")
        return self.best_model

    def save_best_model(self, path="best_model.pkl"):
        """
        Save the best model to a file.
        Args:
            path (str): File path for saving the model.
        """
        if self.best_model:
            with open(path, "wb") as file:
                pickle.dump(self.best_model, file)
            print(f"Best model saved to {path}")
        else:
            print("No model to save. Train models first!")
