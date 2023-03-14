# ****************************************************************************
# Copyright 2023 Technology Innovation Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ****************************************************************************


from ...MQEstimator.mq_algorithm import MQAlgorithm
from ...MQEstimator.mq_problem import MQProblem
from ...helper import ComplexityType
from math import log2
from sage.all import Integer
from sage.arith.misc import is_power_of_two


class KPG(MQAlgorithm):
    r"""
    Construct an instance of KPG estimator

    The KPG is an algorithm to solve a quadratic systems of equations over fields of even characteristic [KPG99]_.

    INPUT:

    - ``problem`` -- MQProblem object including all necessary parameters
    - ``w`` -- linear algebra constant (2 <= w <= 3) (default: 2)
    - ``memory_access`` -- specifies the memory access cost model (default: 0, choices: 0 - constant, 1 - logarithmic, 2 - square-root, 3 - cube-root or deploy custom function which takes as input the logarithm of the total memory usage)
    - ``complexity_type`` -- complexity type to consider (0: estimate, 1: tilde O comp

    EXAMPLES::

        sage: from cryptographic_estimators.MQEstimator.MQAlgorithms.kpg import KPG
        sage: from cryptographic_estimators.MQEstimator.mq_problem import MQProblem
        sage: E = KPG(MQProblem(n=183, m=12, q=4), w=2.8)
        sage: E
        KPG estimator for the MQ problem with 183 variables and 12 polynomials

    TESTS::

        sage: E.problem.nvariables() == E.nvariables_reduced()
        True
    """

    def __init__(self, problem: MQProblem, **kwargs):
        n, m, q = problem.get_problem_parameters()
        if not isinstance(q, (int, Integer)):
            raise TypeError("q must be an integer")

        if not is_power_of_two(q):
            raise ValueError(
                "the order of finite field q must be a power of 2")

        if m * (m + 1) >= n:
            raise ValueError(f'The condition m(m + 1) < n must be satisfied')

        super().__init__(problem, **kwargs)
        self._name = "KPG"
        self._n_reduced = n
        self._m_reduced = m

    def time_complexity(self):
        """
        Return the time complexity of kpg algorithm

        EXAMPLES::

            sage: from cryptographic_estimators.MQEstimator.MQAlgorithms.kpg import KPG
            sage: from cryptographic_estimators.MQEstimator.mq_problem import MQProblem
            sage: E = KPG(MQProblem(n=183, m=12, q=4), w=2.8)
            sage: E.time_complexity()
            24.628922047916475
        """
        n, m, _ = self.problem.get_problem_parameters()
        w = self.linear_algebra_constant()
        if self.complexity_type == ComplexityType.ESTIMATE.value:
            time = log2(m * n ** w)
        else:
            time = 0
        return time

    def memory_complexity(self):
        """
        Return the memory complexity of kpg algorithm

        EXAMPLES::

            sage: from cryptographic_estimators.MQEstimator.MQAlgorithms.kpg import KPG
            sage: from cryptographic_estimators.MQEstimator.mq_problem import MQProblem
            sage: E = KPG(MQProblem(n=183, m=12, q=4), w=2.8)
            sage: E.memory_complexity()
            18.61636217728924
        """
        n, m, _ = self.problem.get_problem_parameters()
        if self.complexity_type == ComplexityType.ESTIMATE.value:
            memory = log2(m * n ** 2)
        else:
            memory = 0
        return memory
