# License: BSD 3 clause

import numpy as np

from .base import ModelHawkes, ModelFirstOrder, ModelSelfConcordant, \
    LOSS_AND_GRAD
from .build.model import ModelHawkesFixedExpKernLogLikList as \
    _ModelHawkesFixedExpKernLogLik


from tick.optim.model.build.model import ModelHawkesCustom as _ModelHawkesCustom

def custom_loss(coeffs, *argv):
    self = argv[0]
    return self.loss(coeffs)


def custom_grad(coeffs, *argv):
    self = argv[0]
    grad_out = np.array(np.zeros(len(coeffs)))
    self.grad(coeffs, grad_out)
    return grad_out


class ModelHawkesCustom(ModelFirstOrder):

    _attrinfos = {
        "decay": {
            "cpp_setter": "set_decay"
        },
        "_end_times": {},
        "data": {}
    }

    def __init__(self, decay: float, n_threads: int = 1):
        ModelFirstOrder.__init__(self)
        self.decay = decay
        self._model = _ModelHawkesCustom(decay, n_threads)
        print(self._model)


    def fit(self, events, end_times=None):
        """Set the corresponding realization(s) of the process.

        Parameters
        ----------
        events : `list` of `list` of `np.ndarray`
            List of Hawkes processes realizations.
            Each realization of the Hawkes process is a list of n_node for
            each component of the Hawkes. Namely `events[i][j]` contains a
            one-dimensional `numpy.array` of the events' timestamps of
            component j of realization i.
            If only one realization is given, it will be wrapped into a list

        end_times : `np.ndarray` or `float`, default = None
            List of end time of all hawkes processes that will be given to the
            model. If None, it will be set to each realization's latest time.
            If only one realization is provided, then a float can be given.
        """
        self._end_times = end_times
        return ModelFirstOrder.fit(self, events)

    def _set_data(self, events):
        """Set the corresponding realization(s) of the process.

        Parameters
        ----------
        events : `list` of `list` of `np.ndarray`
            List of Hawkes processes realizations.
            Each realization of the Hawkes process is a list of n_node for
            each component of the Hawkes. Namely `events[i][j]` contains a
            one-dimensional `numpy.array` of the events' timestamps of
            component j of realization i.
            If only one realization is given, it will be wrapped into a list
        """
        self._set("data", events)

        end_times = self._end_times
        if end_times is None:
            end_times = max(map(max, events))

        self._model.set_data(events, end_times)


    def _loss(self, coeffs):
        return self._model.loss(coeffs)

    def _grad(self, coeffs: np.ndarray, out: np.ndarray) -> np.ndarray:
        self._model.grad(coeffs, out)
        return out

    def _get_n_coeffs(self):
        return self._model.get_n_coeffs()

    @property
    def decays(self):
        return self.decay

    @property
    def _epoch_size(self):
        # This gives the typical size of an epoch when using a
        # stochastic optimization algorithm
        return self.n_jumps

    @property
    def _rand_max(self):
        # This allows to obtain the range of the random sampling when
        # using a stochastic optimization algorithm
        return self.n_jumps
