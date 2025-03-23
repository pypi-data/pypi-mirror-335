"""
Remove Feature

Tests if a feature significantly effects evaluation results in a model - useful for limiting size of a neural network.
"""

def testFeatureRemoval(model, X, Y, thresh=0.99, verbose=True):
    """
    Tests if removing a feature effects evaluation results.
    Returns a list of features to remove

    :param model: A ML model, must support .evaluate() calls
    :param X: A pandas dataframe with X features - each column should have a name
    :param Y: A pandas dataframe with Y features
    :param thresh: is accuracy >= baseline * thresh , suggest removing feature
    :param verbose: print info during test
    """

    baseline_accuracy = model.evaluate(X.values, Y.values)[1]
    if verbose:
        print("Model baseline accuracy:", baseline_accuracy)

    rm_list = []

    header = list(X.columns)
    for c in header:
        t_X = X.copy(deep=True)
        t_X[c] = t_X[c].mean()
        accuracy = model.evaluate(t_X.values, Y.values)[1]

        if accuracy >= baseline_accuracy * thresh:
            print("Without", c, "accuracy:", accuracy)
            rm_list.append(c)

        elif verbose:
            print("Without", c, "accuracy:", accuracy)

    print("Suggest removing:", rm_list)

    return rm_list


