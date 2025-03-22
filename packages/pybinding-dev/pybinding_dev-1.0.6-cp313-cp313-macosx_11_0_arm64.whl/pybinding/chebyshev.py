"""Computations based on Chebyshev polynomial expansion

The kernel polynomial method (KPM) can be used to approximate various functions by expanding them
in a series of Chebyshev polynomials.
"""
import warnings

import numpy as np
from numpy.typing import ArrayLike
from scipy.sparse import csr_matrix, eye
from typing import Literal, Optional, Union, List, Tuple

from . import _cpp
from . import results
from .model import Model
from .results import SpatialLDOS
from .system import System
from .utils.time import timed
from .utils.misc import AttrDict
from .support.deprecated import LoudDeprecationWarning

__all__ = ['KPM', 'kpm', 'kpm_cuda',
           'jackson_kernel', 'lorentz_kernel', 'dirichlet_kernel']

KernelType = Union[_cpp.KPMKernel, Literal["default"]]


class KPM:
    """The common interface for various KPM implementations

    It should not be created directly but via specific functions
    like :func:`kpm` or :func:`kpm_cuda`.

    All implementations are based on: https://doi.org/10.1103/RevModPhys.78.275
    """

    def __init__(self, impl: Union[_cpp.kpm]):
        if isinstance(impl, Model):
            raise TypeError("You're probably looking for `pb.kpm()` (lowercase).")
        self.impl = impl

    @property
    def model(self) -> Model:
        """The tight-binding model holding the Hamiltonian"""
        return self.impl.model

    @model.setter
    def model(self, model: Model):
        self.impl.model = model

    @property
    def system(self) -> System:
        """The tight-binding system (shortcut for `KPM.model.system`)"""
        return System(self.impl.system, self.model.lattice)

    @property
    def scaling_factors(self) -> Tuple[float, float]:
        """A tuple of KPM scaling factors `a` and `b`"""
        return self.impl.scaling_factors

    @property
    def kernel(self) -> _cpp.KPMKernel:
        """The damping kernel"""
        return self.impl.kernel

    @property
    def block_diagonal(self) -> List[int]:
        """The first index of the reordered matrix where a block of a block-diagonal matrix ends."""
        return self.impl.optimized_hamiltonian.block_diagonal

    @property
    def zero_row(self) -> List[int]:
        """The index of a row of zeros in the reordered matrix."""
        return self.impl.optimized_hamiltonian.zero_row

    def report(self, shortform: bool = False) -> str:
        """Return a report of the last computation

        Parameters
        ----------
        shortform : bool, optional
            Return a short one line version of the report
        """
        return self.impl.report(shortform)

    def __call__(self, *args, **kwargs) -> np.ndarray:
        warnings.warn("Use .calc_greens() instead", LoudDeprecationWarning)
        return self.calc_greens(*args, **kwargs)

    def moments(self, num_moments: int, alpha: ArrayLike, beta: Optional[ArrayLike] = None,
                op: Optional[csr_matrix] = None) -> np.ndarray:
        r"""Calculate KPM moments in the form of expectation values

        The result is an array of moments where each value is equal to:

        .. math::
            \mu_n = <\beta|op \cdot T_n(H)|\alpha>

        Parameters
        ----------
        num_moments : int
            The number of moments to calculate.
        alpha : array_like
            The starting state vector of the KPM iteration.
        beta : Optional[array_like]
            If not given, defaults to :math:`\beta = \alpha`.
        op : Optional[csr_matrix]
            Operator in the form of a sparse matrix. If omitted, an identity matrix
            is assumed: :math:`\mu_n = <\beta|T_n(H)|\alpha>`.

        Returns
        -------
        ndarray
        """
        from scipy.sparse import csr_matrix

        if beta is None:
            beta = []
        if op is None:
            op = csr_matrix([])
        else:
            op = op.tocsr()
        return self.impl.moments(num_moments, alpha, beta, op)

    def calc_greens(self, i: int, j: Union[int, np.ndarray], energy: np.ndarray, broadening: float) -> np.ndarray:
        """Calculate Green's function of a single Hamiltonian element

        Parameters
        ----------
        i : int or list
            Hamiltonian index.
        j : int or np.ndarray
            Hamiltonian index or vector of Hamiltonian indices
        energy : ndarray
            Energy value array.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.

        Returns
        -------
        ndarray
            Array of the same size as the input `energy`.
        """
        return self.impl.calc_greens(i, j, energy, broadening)

    def calc_ldos(self, energy: np.ndarray, broadening: float, position: ArrayLike, sublattice: str = "",
                  reduce: bool = True) -> results.Series:
        """Calculate the local density of states as a function of energy

        Parameters
        ----------
        energy : ndarray
            Values for which the LDOS is calculated.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.
        position : array_like
            Cartesian position of the lattice site for which the LDOS is calculated.
            Doesn't need to be exact: the method will find the actual site which is
            closest to the given position.
        sublattice : str
            Only look for sites of a specific sublattice, closest to `position`.
            The default value considers any sublattice.
        reduce : bool
            This option is only relevant for multi-orbital models. If true, the
            resulting LDOS will be summed over all the orbitals at the target site
            and the result will be a 1D array. If false, the individual orbital
            results will be preserved and the result will be a 2D array with
            `shape == (energy.size, num_orbitals)`.

        Returns
        -------
        :class:`~pybinding.Series`
        """
        ldos = self.impl.calc_ldos(energy, broadening, position, sublattice, reduce)
        return results.Series(energy, ldos.squeeze(), labels=dict(variable="E (eV)", data="LDOS",
                                                                  columns="orbitals"))

    def calc_spatial_ldos(self, energy: np.ndarray, broadening: float, shape: _cpp.Shape,
                          sublattice: str = "") -> SpatialLDOS:
        """Calculate the LDOS as a function of energy and space (in the area of the given shape)

        Parameters
        ----------
        energy : ndarray
            Values for which the LDOS is calculated.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.
        shape : Shape
            Determines the site positions at which to do the calculation.
        sublattice : str
            Only look for sites of a specific sublattice, within the `shape`.
            The default value considers any sublattice.

        Returns
        -------
        :class:`SpatialLDOS`
        """
        ldos = self.impl.calc_spatial_ldos(energy, broadening, shape, sublattice)

        pos_cut = shape.contains(*self.system.positions)
        smap = self.system[pos_cut]
        if sublattice:
            sub = smap.sub == sublattice
            smap = smap[sub]
            pos_cut[pos_cut] = sub
        if self.model.is_multiorbital:
            ldos_reduced = np.zeros((ldos.shape[0], smap.num_sites))
            for e_i in range(ldos.shape[0]):
                ldos_reduced[e_i] = self.system.reduce_sliced_data(pos_cut, ldos[e_i])
            ldos = ldos_reduced
        return SpatialLDOS(ldos, energy, smap)

    def calc_dos(self, energy: np.ndarray, broadening: float, num_random: int = 1) -> results.Series:
        """Calculate the density of states as a function of energy

        Parameters
        ----------
        energy : ndarray
            Values for which the DOS is calculated.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.
        num_random : int
            The number of random vectors to use for the stochastic calculation of KPM moments.
            Larger numbers improve the quality of the result but also increase calculation time
            linearly. Fortunately, result quality also improves with system size, so the DOS of
            very large systems can be calculated accurately with only a small number of random
            vectors.

        Returns
        -------
        :class:`~pybinding.Series`
        """
        dos = self.impl.calc_dos(energy, broadening, num_random)
        return results.Series(energy, dos, labels=dict(variable="E (eV)", data="DOS"))

    def deferred_ldos(self, energy: np.ndarray, broadening: float, position: ArrayLike,
                      sublattice: str = "") -> _cpp.DeferredXd:
        """Same as :meth:`calc_ldos` but for parallel computation: see the :mod:`.parallel` module

        Parameters
        ----------
        energy : ndarray
            Values for which the LDOS is calculated.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.
        position : array_like
            Cartesian position of the lattice site for which the LDOS is calculated.
            Doesn't need to be exact: the method will find the actual site which is
            closest to the given position.
        sublattice : str
            Only look for sites of a specific sublattice, closest to `position`.
            The default value considers any sublattice.

        Returns
        -------
        """
        return self.impl.deferred_ldos(energy, broadening, position, sublattice)

    def deferred_greens(self, i: int, j: int, energy: np.ndarray,
                        broadening: float) -> Union[_cpp.Deferredd, _cpp.DeferredXXd]:
        """Same as :meth:`calc_greens` but for parallel computation: see the :mod:`.parallel` module

        Parameters
        ----------
        i : int or list
            Hamiltonian index.
        j : int
            Hamiltonian index.
        energy : ndarray
            Energy value array.
        broadening : float
            Width, in energy, of the smallest detail which can be resolved.
            Lower values result in longer calculation time.


        Returns
        -------
        """
        return self.impl.deferred_greens(i, j, energy, broadening)

    def calc_conductivity(self, chemical_potential: ArrayLike, broadening: float, temperature: float,
                          direction: Literal['xx', 'xy', 'xz', 'yx', 'yy', 'yz', 'zx', 'zy', 'zz'] = "xx",
                          volume: float = 1.0, num_random: int = 1, num_points: int = 1000) -> results.Series:
        """Calculate Kubo-Bastin electrical conductivity as a function of chemical potential

        The return value is in units of the conductance quantum (e^2 / hbar) not taking into
        account spin or any other degeneracy.

        The calculation is based on: https://doi.org/10.1103/PhysRevLett.114.116602.

        Parameters
        ----------
        chemical_potential : array_like
            Values (in eV) for which the conductivity is calculated.
        broadening : float
            Width (in eV) of the smallest detail which can be resolved in the chemical potential.
            Lower values result in longer calculation time.
        temperature : float
            Value of temperature for the Fermi-Dirac distribution.
        direction : Optional[str]
            Direction in which the conductivity is calculated. E.g., "xx", "xy", "zz", etc.
        volume : Optional[float]
            The volume of the system.
        num_random : int
            The number of random vectors to use for the stochastic calculation of KPM moments.
            Larger numbers improve the quality of the result but also increase calculation time
            linearly. Fortunately, result quality also improves with system size, so the DOS of
            very large systems can be calculated accurately with only a small number of random
            vectors.
        num_points : Optional[int]
            Number of points for integration.

        Returns
        -------
        :class:`~pybinding.Series`
        """
        data = self.impl.calc_conductivity(chemical_potential, broadening, temperature,
                                           direction, num_random, num_points)
        if volume != 1.0:
            data /= volume
        return results.Series(chemical_potential, data,
                              labels=dict(variable=r"$\mu$ (eV)", data=r"$\sigma (e^2/h)$"))


class _ComputeProgressReporter:
    def __init__(self):
        from .utils.progressbar import ProgressBar
        self.pbar = ProgressBar(0)

    def __call__(self, delta: float, total: float) -> None:
        if total == 1:
            return  # Skip reporting for short jobs

        if delta < 0:
            print("Computing KPM moments...")
            self.pbar.size = total
            self.pbar.start()
        elif delta == total:
            self.pbar.finish()
        else:
            self.pbar += delta


def kpm(model: Model, energy_range: Optional[Tuple[float, float]] = None,
        kernel: KernelType = "default",
        num_threads: Union[int, Literal["auto"]] = "auto", silent: bool = False, **kwargs) -> KPM:
    """The default CPU implementation of the Kernel Polynomial Method

    This implementation works on any system and is well optimized.

    Parameters
    ----------
    model : Model
        Model which will provide the Hamiltonian matrix.
    energy_range : Optional[Tuple[float, float]]
        KPM needs to know the lowest and highest eigenvalue of the Hamiltonian, before
        computing the expansion moments. By default, this is determined automatically
        using a quick Lanczos procedure. To override the automatic boundaries pass a
        `(min_value, max_value)` tuple here. The values can be overestimated, but note
        that performance drops as the energy range becomes wider. On the other hand,
        underestimating the range will produce `NaN` values in the results.
    kernel : Kernel
        The kernel in the *Kernel* Polynomial Method. Used to improve the quality of
        the function reconstructed from the Chebyshev series. Possible values are
        :func:`jackson_kernel` or :func:`lorentz_kernel`. The Jackson kernel is used
        by default.
    num_threads : int
        The number of CPU threads to use for calculations. This is automatically set
        to the number of logical cores available on the current machine.
    silent : bool
        Don't show any progress messages.

    Returns
    -------
    :class:`~pybinding.chebyshev.KPM`
    """
    if kernel != "default":
        kwargs["kernel"] = kernel
    if num_threads != "auto":
        kwargs["num_threads"] = num_threads
    if "progress_callback" not in kwargs:
        kwargs["progress_callback"] = _ComputeProgressReporter()
    if silent:
        del kwargs["progress_callback"]
    return KPM(_cpp.kpm(model, energy_range or (0, 0), **kwargs))


def kpm_cuda(model: Model, energy_range: Optional[Tuple[float, float]] = None,
             kernel: KernelType = "default", **kwargs) -> KPM:
    """Same as :func:`kpm` except that it's executed on the GPU using CUDA (if supported)

    See :func:`kpm` for detailed parameter documentation.
    This method is only available if the C++ extension module was compiled with CUDA.

    Parameters
    ----------
    model : Model
    energy_range : Optional[Tuple[float, float]]
    kernel : Kernel

    Returns
    -------
    :class:`~pybinding.chebyshev.KPM`
    """
    try:
        if kernel != "default":
            kwargs["kernel"] = kernel
        # noinspection PyUnresolvedReferences
        return KPM(_cpp.kpm_cuda(model, energy_range or (0, 0), **kwargs))
    except AttributeError:
        raise Exception("The module was compiled without CUDA support.\n"
                        "Use a different KPM implementation or recompile the module with CUDA.")


def jackson_kernel() -> _cpp.KPMKernel:
    """The Jackson kernel -- a good general-purpose kernel, appropriate for most applications

    Imposes Gaussian broadening `sigma = pi / N` where `N` is the number of moments. The
    broadening value is user-defined for each function calculation (LDOS, Green's, etc.).
    The number of moments is then determined based on the broadening -- it's not directly
    set by the user.
    """
    return _cpp.jackson_kernel()


def lorentz_kernel(lambda_value: float = 4.0) -> _cpp.KPMKernel:
    """The Lorentz kernel -- best for Green's function

    This kernel is most appropriate for the expansion of the Green’s function because it most
    closely mimics the divergences near the true eigenvalues of the Hamiltonian. The Lorentzian
    broadening is given by `epsilon = lambda / N` where `N` is the number of moments.

    Parameters
    ----------
    lambda_value : float
        May be used to fine-tune the smoothness of the convergence. Usual values are
        between 3 and 5. Lower values will speed up the calculation at the cost of
        accuracy. If in doubt, leave it at the default value of 4.
    """
    return _cpp.lorentz_kernel(lambda_value)


def dirichlet_kernel() -> _cpp.KPMKernel:
    """The Dirichlet kernel -- returns raw moments, least favorable choice

    This kernel doesn't modify the moments at all. The resulting moments represent just
    a truncated series which results in lots of oscillation in the reconstructed function.
    Therefore, this kernel should almost never be used. It's only here in case the raw
    moment values are needed for some other purpose. Note that `required_num_moments()`
    returns `N = pi / sigma` for compatibility with the Jackson kernel, but there is
    no actual broadening associated with the Dirichlet kernel.
    """
    return _cpp.dirichlet_kernel()


class _PythonImpl:
    """Basic Python/SciPy implementation of KPM"""

    def __init__(self, model: Model, energy_range: Tuple[float, float], kernel: _cpp.KPMKernel, **_):
        self.model = model
        self.energy_range = energy_range
        self.kernel = kernel

        self._stats = {}

    @property
    def stats(self) -> AttrDict:
        s = AttrDict(self._stats)
        s.update({k: v.elapsed for k, v in s.items() if "_time" in k})
        s["eps"] = s["nnz"] / s["moments_time"]
        return s

    def _scaling_factors(self) -> Tuple[float, float]:
        """Compute the energy bounds of the model and return the appropriate KPM scaling factors"""
        def find_bounds():
            if self.energy_range[0] != self.energy_range[1]:
                return self.energy_range

            from scipy.sparse.linalg import eigsh
            h = self.model.hamiltonian
            self.energy_range = [eigsh(h, which=x, k=1, tol=2e-3, return_eigenvectors=False)[0]
                                 for x in ("SA", "LA")]
            return self.energy_range

        with timed() as self._stats["bounds_time"]:
            emin, emax = find_bounds()
        self._stats["energy_min"] = emin
        self._stats["energy_max"] = emax

        tolerance = 0.01
        a = 0.5 * (emax - emin) * (1 + tolerance)
        b = 0.5 * (emax + emin)
        return a, b

    def _rescale_hamiltonian(self, h: csr_matrix, a: float, b: float) -> csr_matrix:
        size = h.shape[0]
        with timed() as self._stats["rescale_time"]:
            return (h - b * eye(size)) * (2 / a)

    def _compute_diagonal_moments(self, num_moments: int, starter: np.ndarray, h2: csr_matrix) -> np.ndarray:
        """Procedure for computing KPM moments when the two vectors are identical"""
        r0 = starter.copy()
        r1 = h2.dot(r0) * 0.5

        moments = np.zeros(num_moments, dtype=h2.dtype)
        moments[0] = np.vdot(r0, r0) * 0.5
        moments[1] = np.vdot(r1, r0)

        for n in range(1, num_moments // 2):
            r0 = h2.dot(r1) - r0
            r0, r1 = r1, r0
            moments[2 * n] = 2 * (np.vdot(r0, r0) - moments[0])
            moments[2 * n + 1] = 2 * np.vdot(r1, r0) - moments[1]

        self._stats["num_moments"] = num_moments
        self._stats["nnz"] = h2.nnz * num_moments / 2
        self._stats["vector_memory"] = r0.nbytes + r1.nbytes
        self._stats["matrix_memory"] = (h2.data.nbytes + h2.indices.nbytes + h2.indptr.nbytes
                                        if isinstance(h2, csr_matrix) else 0)
        return moments

    @staticmethod
    def _exval_starter(h2: csr_matrix, index: int) -> np.ndarray:
        """Initial vector for the expectation value procedure"""
        r0 = np.zeros(h2.shape[0], dtype=h2.dtype)
        r0[index] = 1
        return r0

    @staticmethod
    def _reconstruct_real(moments: np.ndarray, energy: np.ndarray, a: float, b: float) -> np.ndarray:
        """Reconstruct a real function from KPM moments"""
        scaled_energy = (energy - b) / a
        ns = np.arange(moments.size)
        k = 2 / (a * np.pi)
        return np.array([k / np.sqrt(1 - w**2) * np.sum(moments.real * np.cos(ns * np.arccos(w)))
                         for w in scaled_energy])

    def _ldos(self, index: int, energy: np.ndarray, broadening: float) -> np.ndarray:
        """Calculate the LDOS at the given Hamiltonian index"""
        a, b = self._scaling_factors()
        num_moments = self.kernel.required_num_moments(broadening / a)
        h2 = self._rescale_hamiltonian(self.model.hamiltonian, a, b)

        starter = self._exval_starter(h2, index)
        with timed() as self._stats["moments_time"]:
            moments = self._compute_diagonal_moments(num_moments, starter, h2)

        with timed() as self._stats["reconstruct_time"]:
            moments *= self.kernel.damping_coefficients(num_moments)
            return self._reconstruct_real(moments, energy, a, b)

    def calc_ldos(self, energy: np.ndarray, broadening: float, position: ArrayLike, sublattice: str = "",
                  reduce: bool = True) -> np.ndarray:
        """Calculate the LDOS at the given position/sublattice"""
        with timed() as self._stats["total_time"]:
            system_index = self.model.system.find_nearest(position, sublattice)
            ham_idx = self.model.system.to_hamiltonian_indices(system_index)
            result_data = np.array([self._ldos(i, energy, broadening) for i in ham_idx]).T
            if reduce:
                return np.sum(result_data, axis=1)
            else:
                return result_data

    def report(self, *_) -> str:
        from .utils.misc import with_suffix
        from .utils.time import pretty_duration

        stats = self.stats.copy()
        stats.update({k: with_suffix(stats[k]) for k in ("num_moments", "eps")})
        stats.update({k: pretty_duration(v) for k, v in stats.items() if "_time" in k})

        fmt = " ".join([
            "{energy_min:.2f}, {energy_max:.2f} [{bounds_time}]",
            "[{rescale_time}]",
            "{num_moments} @ {eps}eps [{moments_time}]",
            "[{reconstruct_time}]",
            "| {total_time}"
        ])
        return fmt.format_map(stats)


def _kpm_python(model: Model, energy_range: Optional[np.ndarray] = None,
                kernel: KernelType = "default", **kwargs) -> KPM:
    """Basic Python/SciPy implementation of KPM"""
    if kernel == "default":
        kernel = jackson_kernel()
    return KPM(_PythonImpl(model, energy_range or (0, 0), kernel, **kwargs))
