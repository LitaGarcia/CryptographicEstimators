from ...SDFqEstimator.sdfq_algorithm import SDFqAlgorithm
from ...SDFqEstimator.sdfq_problem import SDFqProblem
from ...SDFqEstimator.sdfq_helper import binom, log2, min_max, inf
from ...base_algorithm import optimal_parameter
from ..sdfq_constants import *
from types import SimpleNamespace


class LeeBrickell(SDFqAlgorithm):
    def __init__(self, problem: SDFqProblem, **kwargs):
        """
        Construct an instance of Lee-Brickells's estimator [TODO]_
        expected weight distribution::
            +--------------------------------+-------------------------------+
            | <----------+ n - k +---------> | <----------+ k +------------> |
            |               w-p              |              p                |
            +--------------------------------+-------------------------------+
        INPUT:
        - ``problem`` -- SDProblem object including all necessary parameters

        TESTS::
            sage: from cryptographic_estimators.SDFqEstimator.SDFqAlgorithms import LeeBrickell
            sage: from cryptographic_estimators.SDFqEstimator import SDFqProblem
            sage: LeeBrickell(SDFqProblem(n=961,k=771,w=48,q=31)).time_complexity()
            140.31928490910389

        EXAMPLES::
            sage: from cryptographic_estimators.SDFqEstimator.SDFqAlgorithms import LeeBrickell
            sage: from cryptographic_estimators.SDFqEstimator import SDFqProblem
            sage: LeeBrickell(SDFqProblem(n=100,k=50,w=10,q=5))
            Lee-Brickell estimator for syndrome decoding problem with (n,k,w) = (100,50,10) over Finite Field of size 5
        """
        self._name = "LeeBrickell"
        super(LeeBrickell, self).__init__(problem, **kwargs)
        self.initialize_parameter_ranges()
        self.is_syndrome_zero = int(problem.is_syndrome_zero)

    def initialize_parameter_ranges(self):
        """
        initialize the parameter ranges for p, l to start the optimisation 
        process.
        """
        _, _, w, _ = self.problem.get_parameters()
        s = self.full_domain
        self.set_parameter_ranges("p", 0, min_max(w // 2, 20, s))
    
    @optimal_parameter
    def p(self):
        """
        Return the optimal parameter $p$ used in the algorithm optimization

        EXAMPLES::
            sage: from cryptographic_estimators.SDFqEstimator.SDFqAlgorithms import LeeBrickell
            sage: from cryptographic_estimators.SDFqEstimator import SDFqProblem
            sage: A = LeeBrickell(SDFqProblem(n=100,k=50,w=10,q=5))
            sage: A.p()
            2

        """
        return self._get_optimal_parameter("p")

    def _are_parameters_invalid(self, parameters: dict):
        """
        return if the parameter set `parameters` is invalid
        """
        n, k, w, _ = self.problem.get_parameters()
        par = SimpleNamespace(**parameters)
        if par.p > w or k < par.p or n - k < w - par.p:
            return True
        return False

    def _time_and_memory_complexity(self, parameters: dict, verbose_information=None):
        """
        Return time complexity of Lee-Brickell's algorithm over Fq, q > 2 for
        given set of parameters
        NOTE: this optimization assumes that the algorithm is executed on the generator matrix

        INPUT:
        -  ``parameters`` -- dictionary including parameters
        -  ``verbose_information`` -- if set to a dictionary `permutations`,
                                      `gauß` and `list` will be returned.
        EXAMPLES::
            sage: from cryptographic_estimators.SDFqEstimator.SDFqAlgorithms import LeeBrickell
            sage: from cryptographic_estimators.SDFqEstimator import SDFqProblem
            sage: A = LeeBrickell(SDFqProblem(n=100,k=50,q=3,w=10))
            sage: A.p()
            2

        """
        n, k, w, q = self.problem.get_parameters()
        par = SimpleNamespace(**parameters)
        if self._are_parameters_invalid(parameters):
            return inf, inf

        solutions = self.problem.nsolutions
        enum = binom(k, par.p) * (q-1)**(max(0, par.p-self.is_syndrome_zero))
        # Beullens code uses (contrary to his paper)
        #enum = k**par.p * q**(max(0, par.p-self.is_syndrome_zero))
        memory = log2(k * n)

        Tp = max(log2(binom(n, w)) - log2(binom(n - k, w - par.p)) - log2(binom(k, par.p)) - solutions, 0)
        Tg = k*k
        time = Tp + log2(Tg + enum) + log2(n)
        if verbose_information is not None:
            verbose_information[VerboseInformation.PERMUTATIONS.value] = Tp
            verbose_information[VerboseInformation.GAUSS.value] = Tg
            verbose_information[VerboseInformation.LISTS.value] = [enum]

        return time, memory

    def __repr__(self):
        """
        """
        rep = "Lee-Brickell estimator for " + str(self.problem)
        return rep
