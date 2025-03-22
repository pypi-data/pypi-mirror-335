import pandas as pd
from PyCodeml.regressor import RegressorTrainer
from PyCodeml.utils import load_model
 # Create a sample dataset
data = {
    "feature1": [1, 2, 3, 4, 5, 8, 4, 9, 2, 5, 7, 9],
    "feature2": [2, 3, 4, 5, 6, 4, 6, 7, 9, 8, 7, 6,],
    "target": [2.2, 2.8, 3.6, 4.5, 5.1,2.6, 2.4, 3.3, 4.6, 5.2,7.8,6.7]
}
df = pd.DataFrame(data)

# Initialize and train the model
trainer = RegressorTrainer(df, "target")
best_model = trainer.train_and_get_best_model()

# Save the model
trainer.save_best_model("best_regressor.pkl")





# from pycode.utils import load_model  # Import the function

# Load the saved model
# model = load_model("best_regressor.pkl")

# # Check if the model loaded successfully before using it
# if model:
#     test_data = [[1, 3]]  
#     prediction = model.predict(test_data)
#     print("Predicted Value:", prediction)
# else:
#     print("Failed to load model.")