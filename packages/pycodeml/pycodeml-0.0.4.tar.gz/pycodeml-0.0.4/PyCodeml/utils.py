import pickle

def save_model(model, path):
    """Save a trained model to a file."""
    with open(path, "wb") as file:
        pickle.dump(model, file)
    print(f"Model saved to {path}")

def load_model(path):
    """Load a trained model from a file."""
    with open(path, "rb") as file:
        model = pickle.load(file)
    print(f"Model loaded from {path}")
    return model
