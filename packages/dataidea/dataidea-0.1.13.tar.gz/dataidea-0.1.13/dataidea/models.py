import joblib

def load_model(filename='model.di'):
    """
    Load a model from a file using joblib.

    Parameters:
    filename (str): The path to the file containing the model.

    Returns:
    object: The loaded model.
    """
    return joblib.load(filename)

def save_model(model, filename='model.di'):
    """
    Save a model to a file using joblib.

    Parameters:
    model (object): The model to be saved.
    filename (str): The path to the file where the model will be saved.

    Returns:
    None
    """
    joblib.dump(model, filename)

__all__ = ['load_model', 'save_model']