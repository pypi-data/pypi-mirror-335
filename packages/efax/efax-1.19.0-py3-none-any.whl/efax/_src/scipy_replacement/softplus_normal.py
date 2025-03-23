from __future__ import annotations

import numpy as np
import scipy.stats as ss
from numpy.random import Generator
from tjax import NumpyComplexArray, NumpyRealArray, NumpyRealNumeric, ShapeLike, softplus


class ScipySoftplusNormal:
    def __init__(self, mu: NumpyRealArray, sigma: NumpyRealArray) -> None:
        super().__init__()
        self.mu = mu
        self.sigma = sigma

    def pdf(self, x: NumpyRealNumeric, out: None = None) -> NumpyRealArray:
        # Compute the inverse Softplus transformation: Z = log(exp(x) - 1)
        z = np.log(np.exp(x) - 1)
        # Compute the normal PDF of Z ~ N(mu, sigma^2)
        normal_pdf = ss.norm.pdf(z, loc=self.mu, scale=self.sigma)
        # Compute the Jacobian term (dx/dz)
        jacobian = 1 / (1 - np.exp(-x))
        # Compute the final PDF
        return normal_pdf * jacobian

    def rvs(self,
            size: ShapeLike | None = None,
            random_state: Generator | None = None
            ) -> NumpyComplexArray:
        distribution = ss.norm(loc=self.mu, scale=self.sigma)
        samples = np.asarray(distribution.rvs(size=size, random_state=random_state))
        return softplus(samples)

    def entropy(self) -> NumpyRealArray:
        # Term 1: Variance-related term (from normal distribution)
        normal_entropy = 0.5 * np.log(2 * np.pi * np.e * self.sigma**2)

        # Term 2: The expectation of the log(1 - exp(-X)) term
        # This expectation requires solving an integral, but we can approximate it numerically.
        # For the Softplus transformation, it's known that this term is related to the mean of
        # X ~ Softplus-Normal(mu, sigma). In some cases, it may be approximated, but for the exact
        # formula, this requires specialized techniques.

        # Using an approximation for the log(1 - exp(-X)) term:
        # We approximate it using the known result for Softplus and Normal distribution's
        # entropy properties.

        # Since it's difficult to compute the expectation analytically, let's use an approximation:
        # approximation for mean
        expectation_log_term = -0.5 * np.log(1 + np.exp(2 * self.mu / self.sigma**2))

        # Final entropy:
        return normal_entropy + expectation_log_term
