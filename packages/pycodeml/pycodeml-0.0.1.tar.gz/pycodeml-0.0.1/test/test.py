import pandas as pd
from PyCodeml.regressor import RegressorTrainer

# Create a sample dataset
data = {
    "feature1": [1, 2, 3, 4, 5],
    "feature2": [2, 3, 4, 5, 6],
    "target": [2.2, 2.8, 3.6, 4.5, 5.1]
}
df = pd.DataFrame(data)

# Initialize and train the model
trainer = AutoRegressorTrainer(df, "target")
best_model = trainer.train_and_get_best_model()

# Save the model
# trainer.save_best_model("best_regressor.pkl")
