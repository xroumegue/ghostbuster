#! /usr/bin/env python3
"""
    Implements ProtonPack: The ghostbuster favourite weapon
"""
from logging import getLogger
from abc import ABC, abstractmethod
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

class ProtonPack(ABC):
    """
        The ghostbuster gun ! Destroy a ghost !
    """

    def __init__(self):
        super().__init__()
        self.log = getLogger()
        self.x = None
        self.y = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.x_raw_train = None
        self.x_raw_test = None
        self.scaler = None
        self.clf = None

    def get_nsamples(self):
        """
            Return the number of samples in the dataset
        """
        if self.x is not None:
            return self.x.shape[0]
        return 0

    def get_nfeatures(self):
        """
            Return the number of features in the dataset
        """
        if self.x is not None:
            return self.x.shape[1]
        return 0


    def get_n_test(self):
        """
            Return the number of samples in the validation dataset
        """
        if self.x_test is not None:
            return self.x_test.shape[0]
        return 0


    def load(self, dataset):
        """
        Load the dataset, and define the training and validation set after normalization
        """
        self.x = dataset.drop('attack', axis=1)
        self.y = dataset['attack']
        assert self.x.shape[0] == self.y.shape[0]

        self.log.info("Dataset loaded: {:d} samples, {:d} features".format(
            self.get_nsamples(),
            self.get_nfeatures())
                     )

        # Determine training and testing sets
        self.x_raw_train, self.x_raw_test, self.y_train, self.y_test = train_test_split(self.x, self.y)

        # Scale the dataset
        self.scaler = StandardScaler()
        self.scaler.fit(self.x_raw_train)
        self.x_train = self.scaler.transform(self.x_raw_train)
        self.x_test = self.scaler.transform(self.x_raw_test)

        self.log.info(
            "Using {} samples as test set".format(
                self.get_n_test(),
            )
        )

    @abstractmethod
    def train(self):
        """
            Train the model
        """
        pass

    @abstractmethod
    def classify(self, x, scale=True):
        """
            Predict a class from a x vector
        """
        pass

    def validate(self):
        """
            Validate the model against the validation set
        """
        self.log.debug("x test set:\n{0!s}".format(self.x_test))
        self.log.debug("y test set:\n{!s}".format(self.y_test))
        y_computed = self.classify(self.x_test, scale=False)
        y_expected = self.y_test
        self.test_predictions = confusion_matrix(y_expected, y_computed)
        self.log.info("Confusion matrix:\n{}".format(self.test_predictions))
#        tn, fp, fn, tp = self.test_predictions
        self.log.info("Classification report:\n{}".format(
                classification_report(y_expected, y_computed, digits=3)
            )
        )


class ProtonPackSvm(ProtonPack):
    def train(self):

        self.log.debug("x training set:\n{}".format(self.x_train))
        self.log.debug("y training set:\n{}".format(self.y_train))
        self.clf = svm.SVC()
        self.clf.fit(self.x_train, self.y_train)
        self.log.debug(self.clf)

    def classify(self, x, scale=True):
        if isinstance(x, list):
            x = np.asarray(x)
        x_scale = x
        if scale:
            x_scale = self.scaler.transform(x)
        y_predicted = self.clf.predict(x_scale)
        self.log.debug("Prediction: x - {}:({}) y - {}".format(x, x.shape, y_predicted))
        return y_predicted

