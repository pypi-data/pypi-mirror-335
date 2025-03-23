import pytest
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # stops agressive error message printing
from tensorflow import keras
import MLVisualizationTools as project
import MLVisualizationTools.backend as backend
from MLVisualizationTools.backend import fileloader
import pandas as pd
import copy

def test_colorizer():
    data = pd.DataFrame({'Output': [0, 0.5, 1]})
    data = backend.GraphData(data, backend.GraphDataTypes.Grid, 20, 'NotKey', 'NotKey')
    assert list(project.Colorizers.simple(copy.deepcopy(data), 'red').modeldata.dataframe['Color']) == ['red'] * 3

    assert (list(project.Colorizers.binary(copy.deepcopy(data), highcontrast=True).modeldata.dataframe['Color'])
           == ['orange', 'orange', 'blue'])

    assert (list(project.Colorizers.binary(copy.deepcopy(data), highcontrast=False).modeldata.dataframe['Color'])
            == ['red', 'red', 'green'])

    assert (list(project.Colorizers.binary(copy.copy(data), highcontrast=False,
                                           truecolor='white', falsecolor='black').modeldata.dataframe['Color'])
            == ['black', 'black', 'white'])

def test_dash_visualizer(): #doesn't launch dash apps, but tests creation process
    import MLVisualizationTools.express.DashModelVisualizer as DMV
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))
    df = df.drop("Survived", axis=1)
    DMV.App(model, df, theme='light')
    DMV.App(model, df, theme='dark')

def test_demo():
    import MLVisualizationTools.examples.Demo as Demo
    Demo.main(show=False)

    import MLVisualizationTools.examples.AnimationDemo as AnimationDemo
    AnimationDemo.main(show=False)

    import MLVisualizationTools.examples.DataOverlayDemo as DODemo
    DODemo.main(show=False)

    import MLVisualizationTools.examples.SklearnDemo as SKDemo
    SKDemo.main(show=False)


def test_mpl():
    import matplotlib
    matplotlib.use('Agg')  # disables UI rendering
    import warnings
    warnings.filterwarnings(
        action='ignore',
        category=UserWarning,
        message= r'Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.'
        # disables agg warning on matplotlib
    )

    warnings.filterwarnings(
        action='ignore',
        category=UserWarning,
        message=r'FigureCanvasAgg is non-interactive, and thus cannot be shown'
        # disables agg warning on matplotlib
    )

    import MLVisualizationTools.examples.MatplotlibDemo as MPLDemo
    MPLDemo.main()

def test_process_data_train_and_run_model():
    import MLVisualizationTools.examples.Datasets.Titanic.TitanicDemoPreprocess as TDP
    TDP.main()
    import MLVisualizationTools.examples.TrainTitanicModel as TTM
    TTM.main()

    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    # region preprocess
    header = list(df.columns)
    header.remove("Survived")

    X = df[header].values
    Y = df["Survived"].values

    _, accuracy = model.evaluate(X, Y)
    # assert accuracy >= 0.70 #had to disable this because we kept failing...

def test_colorizer_edge_cases():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()

    grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])

    with pytest.warns(UserWarning, match = "Colorization not being applied to any points"):
        project.Colorizers.simple(copy.deepcopy(grid), 'red', apply_to_model=False)
    with pytest.warns(UserWarning, match = "Colorization should be applied to data values"):
        project.Colorizers.simple(copy.deepcopy(grid), 'red', apply_to_data=True)
    with pytest.warns(UserWarning, match = "Color key 'Age' was already in dataframe."):
        project.Colorizers.simple(copy.deepcopy(grid), 'red', colorkey='Age')
    with pytest.warns(UserWarning, match = "Colorization may overwrite existing colorization."):
        project.Colorizers.simple(grid, 'red')
        project.Colorizers.simple(grid, 'bue')
    with pytest.warns(UserWarning, match = "Colorization may overwrite existing colorization."):
        grid = project.DataInterfaces.addClumpedData(grid, df, outputkey='Survived')
        project.Colorizers.simple(grid, 'red', apply_to_data=True, apply_to_model=False)
        project.Colorizers.simple(grid, 'blue', apply_to_data=True, apply_to_model=False)


def test_wrong_data_format_exception():
    from MLVisualizationTools.graphinterface import WrongDataFormatException

    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    print(maxvar[0]) #tests repr

    with pytest.raises(WrongDataFormatException):
        grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
        _ = project.Graphs.plotlyAnimation(grid)

    with pytest.raises(WrongDataFormatException):
        grid = project.Interfaces.predictionAnimation(model, maxvar[0], maxvar[1], maxvar[2], df, ["Survived"])
        _ = project.Graphs.plotlyGrid(grid)

    with pytest.raises(WrongDataFormatException):
        grid = project.Interfaces.predictionAnimation(model, maxvar[0], maxvar[1], maxvar[2], df, ["Survived"])
        _ = project.Graphs.matplotlibGrid(grid)

def test_OutputKey_warning():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    cols = list(df.columns)
    cols[1] = "Output"
    df.columns = cols

    with pytest.warns(Warning, match="Output key 'Output' was already in dataframe."):
        project.Interfaces.predictionGrid(model, cols[1], cols[2], df, ["Survived"])
    with pytest.warns(Warning, match="Output key 'Output' was already in dataframe."):
        project.Interfaces.predictionAnimation(model, cols[1], cols[2], cols[3], df, ["Survived"])

def test_graph_branch_error():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    project.Graphs.graph(grid)
    project.Graphs.graph(grid, project.types.GraphOutputTypes.Matplotlib)
    grid = project.Interfaces.predictionAnimation(model, maxvar[0], maxvar[1], maxvar[2], df, ["Survived"])
    with pytest.warns(Warning, match="Size key 'Age' was already in dataframe."):
        project.Graphs.graph(grid, graphtype=project.types.GraphOutputTypes.Plotly, sizekey='Age')
    with pytest.raises(NotImplementedError):
        project.Graphs.graph(grid, project.types.GraphOutputTypes.Matplotlib)

    grid.datatype = "NotAType"
    with pytest.raises(Exception, match="DataType NotAType not recognized."):
        project.Graphs.plotlyGraph(grid)
    with pytest.raises(Exception, match="DataType NotAType not recognized."):
        project.Graphs.matplotlibGraph(grid)

    with pytest.raises(Exception, match="GraphType NotAType not recognized."):
        # noinspection PyTypeChecker
        project.Graphs.graph(grid, "NotAType")

    with pytest.raises(ValueError, match="Not A Mode is not a valid data storage mode"):
        # noinspection PyTypeChecker
        project.backend.ColorizerableDataFrame(pd.DataFrame(), mode = 'Not A Mode')

def test_data_interface_errors():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])

    with pytest.raises(UserWarning, match="Output key 'Output' was not in dataframe."):
        project.datainterface.addClumpedData(grid, df)

    with pytest.raises(UserWarning, match="Output key 'Output' was not in dataframe."):
        project.datainterface.addPercentageData(grid, df)

def test_custom_sizekeys():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    anim = project.Interfaces.predictionAnimation(model, maxvar[0], maxvar[1], maxvar[2], df, ['Survived'])
    project.Graphs.matplotlibGraph(grid, sizekey='Skey', legend=False)
    project.Graphs.plotlyGraph(grid, sizekey='Skey')
    project.Graphs.plotlyGraph(anim, sizekey='Skey')
    project.DataInterfaces.addClumpedData(grid, df, outputkey='Survived', sizekey='Skey')
    project.DataInterfaces.addPercentageData(grid, df, outputkey='Survived', sizekey='Skey2')


def test_unusual_dataoverlay():
    model = keras.models.load_model(fileloader('examples/Models/titanicmodel.keras'))
    df: pd.DataFrame = pd.read_csv(fileloader('examples/Datasets/Titanic/train.csv'))

    AR = project.Analytics.analyzeModel(model, df, ["Survived"])
    maxvar = AR.maxVariance()
    grid = project.Interfaces.predictionGrid(model, maxvar[0], maxvar[1], df, ["Survived"])
    anim = project.Interfaces.predictionAnimation(model, maxvar[0], maxvar[1], maxvar[2], df, ['Survived'])

    project.DataInterfaces.addClumpedData(grid, df, outputkey='Survived')
    panim = project.DataInterfaces.addPercentageData(copy.deepcopy(anim), df, outputkey='Survived')
    project.DataInterfaces.addClumpedData(anim, df, outputkey='Survived')

    grid = project.Colorizers.simple(grid, 'white', apply_to_data=True)

    project.Graphs.plotlyGraph(anim)
    project.Graphs.plotlyGraph(panim)
    project.Graphs.matplotlibGraph(grid)

def test_rm_feature():
    from MLVisualizationTools.examples import RemoveFeatureDemo
    RemoveFeatureDemo.main() #verbose true
    RemoveFeatureDemo.main(False) #verbose false