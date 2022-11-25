from FitLineMulticore import getVminPredict
import pytest


class TestingFitLines:
    def test_distribution_statistic(self):
        assert False


def test_get_vmin_predict():

    popstat = [0.98,1]

    res = getVminPredict(popstat)
    assert 0.01 == res
