import numpy as np

from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.hyperparameters import UniformFloatHyperparameter, \
    CategoricalHyperparameter

from autosklearn.pipeline.components.algorithms import AutoSklearnClassificationAlgorithm
from autosklearn.pipeline.constants import *


class BernoulliNB(AutoSklearnClassificationAlgorithm):

    def __init__(self):
        super(BernoulliNB, self).__init__()
        self.alpha = 1
        self.fit_prior = True
        self.verbose = 0

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'BernoulliNB',
                'name': 'Bernoulli Naive Bayes classifier',
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

        # the smoothing parameter is a non-negative float
        # I will limit it to 1000 and put it on a logarithmic scale. (SF)
        # Please adjust that, if you know a proper range, this is just a guess.
        alpha = UniformFloatHyperparameter(name="alpha", lower=1e-2, upper=100,
                                           default=1, log=True)

        fit_prior = CategoricalHyperparameter(name="fit_prior",
                                              choices=["True", "False"],
                                              default="True")

        cs.add_hyperparameter(alpha)
        cs.add_hyperparameter(fit_prior)

        return cs

    def fit(self, X, y):
        while not self.configuration_fully_fitted():
            self.iterative_fit(X, y, n_iter=1)
        return self

    def iterative_fit(self, X, y, n_iter=1, refit=False):
        import sklearn.naive_bayes

        if refit:
            self.estimator = None

        if self.estimator is None:
            self.n_iter = 0
            self.fully_fit_ = False
            self.estimator = sklearn.naive_bayes.BernoulliNB(
                alpha=self.alpha, fit_prior=self.fit_prior)
            self.classes_ = np.unique(y.astype(int))

        # Fallback for multilabel classification
        if len(y.shape) > 1 and y.shape[1] > 1:
            import sklearn.multiclass
            self.estimator.n_iter = self.n_iter
            self.estimator = sklearn.multiclass.OneVsRestClassifier(
                self.estimator, n_jobs=1)
            self.estimator.fit(X, y)
            self.fully_fit_ = True
        else:
            for iter in range(n_iter):
                start = min(self.n_iter * 1000, y.shape[0])
                stop = min((self.n_iter + 1) * 1000, y.shape[0])
                # Upper limit, scipy.sparse doesn't seem to handle max > len(matrix)
                stop = min(stop, y.shape[0])
                if X[start:stop].shape[0] == 0:
                    self.fully_fit_ = True
                    break

                self.estimator.partial_fit(X[start:stop], y[start:stop], self.classes_)
                self.n_iter += 1

                if stop >= len(y):
                    self.fully_fit_ = True
                    break

        return self

    def configuration_fully_fitted(self):
        if self.estimator is None:
            return False
        elif not hasattr(self, 'fully_fit_'):
            return False
        else:
            return self.fully_fit_
