from MLVisualizationTools import Analytics, Interfaces, DataInterfaces, Graphs, Colorizers
from MLVisualizationTools.backend import fileloader
import pandas as pd

from sklearn import tree


try:
    import plotly
except ImportError:
    raise ImportError("Plotly is required to run this demo. If you don't have plotly installed, install it with"
                      " `pip install plotly' or run the matplotlib demo instead.")

def main(show=True):
    """Run the demo. Disable show for testing purposes."""
    model = tree.DecisionTreeClassifier()
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    header = list(df.columns)
    header.remove("Survived")

    X = df[header].values
    Y = df["Survived"].values

    model.fit(X, Y)
    print("Trained decision tree with accuracy: ", model.score(X, Y))


    AR = Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()

    grid = Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    grid = Colorizers.binary(grid)
    grid = DataInterfaces.addPercentageData(grid, df, 'Survived')
    grid = Colorizers.binary(grid, highcontrast=False, apply_to_data=True, apply_to_model=False)
    fig = Graphs.plotlyGraph(grid)
    if show: # pragma: no cover
        fig.show()

print("This demo shows basic features with sklearn and plotly.")
print("To run the demo, call Demo.main()")

if __name__ == "__main__":
    main()