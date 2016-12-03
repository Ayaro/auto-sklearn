from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.hyperparameters import CategoricalHyperparameter, \
    Constant, UniformIntegerHyperparameter

from autosklearn.pipeline.components.algorithms import AutoSklearnClassificationAlgorithm
from autosklearn.pipeline.constants import *


class KNearestNeighborsClassifier(AutoSklearnClassificationAlgorithm):

    def __init__(self):
        super(KNearestNeighborsClassifier, self).__init__()
        self.n_neighbors = 1
        self.weights = "uniform"
        self.p = 2

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'KNN',
                'name': 'K-Nearest Neighbor Classification',
                'handles_regression': False,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': True,
                'is_deterministic': True,
                'input': (DENSE, SPARSE, SIGNED_DATA),
                'output': (PREDICTIONS,)}

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties=None):
        cs = ConfigurationSpace()

        n_neighbors = cs.add_hyperparameter(UniformIntegerHyperparameter(
            name="n_neighbors", lower=1, upper=100, log=True, default=1))
        weights = cs.add_hyperparameter(CategoricalHyperparameter(
            name="weights", choices=["uniform", "distance"], default="uniform"))
        p = cs.add_hyperparameter(CategoricalHyperparameter(
            name="p", choices=[1, 2], default=2))

        return cs

    def fit(self, X, Y):
        import sklearn.neighbors
        import sklearn.multiclass

        estimator = \
            sklearn.neighbors.KNeighborsClassifier(n_neighbors=self.n_neighbors,
                                                   weights=self.weights,
                                                   p=self.p)

        if len(Y.shape) == 2 and Y.shape[1] > 1:
            self.estimator = sklearn.multiclass.OneVsRestClassifier(estimator, n_jobs=1)
        else:
            self.estimator = estimator

        self.estimator.fit(X, Y)
        return self
