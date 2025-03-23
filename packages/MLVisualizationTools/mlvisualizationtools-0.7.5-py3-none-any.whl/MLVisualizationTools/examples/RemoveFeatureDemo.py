from MLVisualizationTools import RemoveFeature
from MLVisualizationTools.backend import fileloader
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #stops agressive error message printing
from tensorflow import keras

def main(verbose=True):
    """Run the demo. Disable show for testing purposes."""
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    header = list(df.columns)
    header.remove("Survived")

    X = df[header]
    Y = df["Survived"]

    RemoveFeature.testFeatureRemoval(model, X, Y, verbose=verbose)

print("This demo shows remove feature analysis.")
print("To run the demo, call Demo.main()")

if __name__ == "__main__":
    main(verbose=True)