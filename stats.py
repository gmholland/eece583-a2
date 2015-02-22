from math import sqrt

class Container:
    """Container for calculating mean and variance of groups of items.
    
    Modified from en.wikipedia.org/wiki/Algorithms_for_calculating_variance
    """

    def __init__(self):
        self._K = 0
        self._n = 0
        self._Ex = 0
        self._Ex2 = 0

    def add(self, x):
        """Add a numeric item to the statistics container."""
        if (self._n == 0):
            self._K = x
        self._n += 1
        self._Ex += x - self._K
        self._Ex2 += (x - self._K) * (x - self._K)

    def get_mean(self):
        """Return the mean of the items in the container."""
        return self._K + self._Ex / self._n

    def get_variance(self):
        """Return the variance of the items in the container."""
        return (self._Ex2 - (self._Ex * self._Ex)/self._n) / (self._n - 1)

    def get_std_dev(self):
        """Return the standard deviation of the items in the container."""
        var = self.get_variance()
        return sqrt(var)
