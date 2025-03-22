""" Parsers for different file formats """
from .pickle import normalize
from ..constants import bohr

from pathlib import Path
from typing import Union, Dict
import warnings

import numpy as np
import re

__all__ = ["win", "hr_dat", "xyz"]


def win(file: Union[str, Path]) -> Dict:
    """ Parse a win-file from a Wannier90 calculation.

    Parameters
    ----------
    file : str or Path
        The filename of the file to parse, i.e. "wannier90.win"

    Returns
    -------
    Dict
    """
    file = normalize(file)
    keys, values, tmp_value = ["filename"], [file], []
    tmp_key = ""

    for line in open(file):
        if line.strip()[:5] == "begin":
            tmp_key = line.split("begin")[1].split("#")[0].split("!")[0].strip().lower()
            tmp_value = []
        elif line.strip()[:3] == "end":
            end_key = line.split("end")[1].split("#")[0].split("!")[0].strip().lower()
            assert tmp_key == end_key, "The segment didn't close properly, {0} != {1}".format(tmp_key, end_key)
            if tmp_key in ["unit_cell_cart", "atoms_cart", "atoms_frac", "kpoints"]:
                tmp_scale = 1 if tmp_key in ["atoms_frac", "kpoints"] else .1
                if tmp_value[0].lower() == "bohr":
                    tmp_scale /= bohr
                    tmp_value = tmp_value[1:]
                elif tmp_value[0].lower() in ["ang", "angstrom"]:
                    tmp_value = tmp_value[1:]
                if tmp_key in ["atoms_cart", "atoms_frac"]:
                    tmp_names = [lat_line.split(" ", 1)[0] for lat_line in tmp_value]
                    tmp_value = [lat_line.split(" ", 1)[1] for lat_line in tmp_value]
                tmp_value = tmp_scale * np.array([np.fromstring(lat_line, sep=" ") for lat_line in tmp_value])
                if tmp_key in ["atoms_cart", "atoms_frac"]:
                    tmp_value = dict(zip(["names", "positions"], [tmp_names, tmp_value]))
            if tmp_key == "kpoint_path":
                tmp_names_from = [lat_line.split()[0] for lat_line in tmp_value]
                tmp_value_from = [" ".join(lat_line.split(maxsplit=1)[1].split(maxsplit=3)[:3])
                                  for lat_line in tmp_value]
                tmp_names_to = [lat_line.split()[4] for lat_line in tmp_value]
                tmp_value_to = ["".join(lat_line.split(maxsplit=5)[5]) for lat_line in tmp_value]
                tmp_value_from = np.array([np.fromstring(lat_line, sep=" ") for lat_line in tmp_value_from])
                tmp_value_to = np.array([np.fromstring(lat_line, sep=" ") for lat_line in tmp_value_to])
                tmp_value = dict(zip(["names_from", "kpoints_from", "names_to", "kpoints_to"],
                                     [tmp_names_from, tmp_value_from, tmp_names_to, tmp_value_to]))
            keys.append(tmp_key)
            values.append(tmp_value)
            tmp_key = ""
        else:
            if not tmp_key == "":
                tmp_value.append(line.strip())
            else:
                line_uncomment = line.split("#")[0].split("!")[0].strip()
                split_symb = " "
                if "=" in line_uncomment:
                    split_symb = "="
                elif ":" in line_uncomment:
                    split_symb = ":"
                line_split = line_uncomment.split(split_symb)
                assert len(line_split) in (1, 2), "Encountered an unreadable line: \n----\n{0}----".format(line)
                if len(line_split) == 2:
                    key, value = line_split
                    key = key.strip().lower()
                    keys.append(key)
                    value = value.strip().lower()
                    if value in ["true", "t", ".true.."]:
                        value = True
                    elif value in ["false", "f", ".false.."]:
                        value = False
                    elif _to_int(value) is not None:
                        value = _to_int(value)
                    elif _to_float(value) is not None:
                        value = _to_float(value)
                    if key in ["mp_grid"]:
                        value = np.fromstring(value, sep=" ", dtype=int).tolist()
                    values.append(value)
                elif not line_split[0].strip() == "":
                    assert False, "Encountered an unreadable line: \n----\n{0}----".format(line)
    return dict(zip(keys, values))


def hr_dat(file: Union[str, Path]) -> Dict:
    """ Parse a hr.dat-file from a Wannier90 calculation.

    Parameters
    ----------
    file : str or Path
        The filename of the file to parse, i.e. "wannier90_hr.dat"

    Returns
    -------
    Dict
    """
    file = normalize(file)
    keys, values = ["filename"], [file]
    num_wann, nrpts, line_i = 0, 0, 0
    ws_deg_points = np.array([], dtype=int)

    for line_i, line in enumerate(open(file)):
        value = line.strip()
        if line_i == 0:
            keys.append("comment")
            values.append(value)
        elif line_i == 1:
            assert len(value.split()) == 1 or str(int(value)) == value, \
                "The number of Wannier orbitals should be a single number, got this: \n----\n{0}----".format(value)
            keys.append("num_wann")
            num_wann = int(value)
            values.append(num_wann)
        elif line_i == 2:
            assert len(value.split()) == 1 or str(int(value)) == value, \
                "The number of Wigner-Seitz grid-points nrpts should be a single number, got this:" \
                "\n----\n{0}----".format(value)
            keys.append("nrpts")
            nrpts = int(value)
            values.append(nrpts)
        elif line_i == 3 or ws_deg_points.shape[0] < nrpts:
            value = np.fromstring(value, sep=" ", dtype=int)
            ws_deg_points = np.hstack((ws_deg_points, value))
            if (not value.shape[0] == 15) and (not ws_deg_points.shape[0] == nrpts):
                warnings.warn("There were more enetries on the WS-degs. Should be 15 (except last),"
                              "but {0} were passed".format(value.shape[0]), UserWarning)
        elif ws_deg_points.shape[0] == nrpts:
            keys.append("ws_deg")
            values.append(ws_deg_points.tolist())
            break
        else:
            assert False, "Apperently, the loop didn't stop. Maybe too many Wigner-Seitz degenerate points? " \
                          "({0}), {1}!={2}".format(ws_deg_points, ws_deg_points.shape[0], nrpts)
    keys.append("hr_columns")
    ham_elements = np.loadtxt(file, skiprows=line_i)
    assert ham_elements.shape[0] == num_wann ** 2 * nrpts, \
        "The number of matrix elements has not the expected length: {0} != {1}".format(
            ham_elements.shape[0], num_wann ** 2 * nrpts
        )
    values.append(ham_elements)
    return dict(zip(keys, values))


def xyz(file: Union[str, Path]) -> Dict:
    """ Parse a xyz-file from a Wannier90, MD or Ovito calculation.

    Parameters
    ----------
    file : str or Path
        The filename of the file to parse, i.e. "wannier90_centres.xyz"

    Returns
    -------
    Dict
    """
    file = normalize(file)
    keys, values = ["filename"], [file]
    n_atoms, line_i = 0, 0
    atoms, xyz = [], []

    for line_i, line in enumerate(open(file)):
        if line_i == 0:
            n_atoms = int(line.strip())
            keys.append("n_atoms")
            values.append(n_atoms)
        elif line_i == 1:
            keys.append("comment")
            values.append(line.strip())
            com = [p for p in re.split("(=| |\\\".*?\\\"|'.*?')", line.strip()) if p.strip()]
            if np.all([eq == "=" for eq in com[1::3]]):
                extended_keys = []
                extended_vals = []
                for key, val in zip(com[0::3], com[2::3]):
                    extended_keys.append(key)
                    if key == "Lattice":
                        val = val.split("#")[0].replace('"', "").strip()
                        vecs = np.fromstring(val.strip(), sep=" ")
                        if vecs.shape[0] in [1, 4, 9]:
                            n_dims = int(np.sqrt(vecs.shape[0]))
                            extended_vals.append(vecs.reshape((n_dims, n_dims)) / 10)
                            extended_keys.append("n_dims")
                            extended_vals.append(n_dims)
                        else:
                            extended_vals.append(val)
                    else:
                        extended_vals.append(val)
                keys.append("extended")
                values.append(dict(zip(extended_keys, extended_vals)))
        else:
            atom, coords = line.strip().split(maxsplit=1)
            atoms.append(atom)
            xyz.append(np.fromstring(coords, sep=" "))
    if line_i - 2 > n_atoms:
        warnings.warn("There are more lines in the xyz file than than given in the header, {0} != {1}".format(
                line_i - 1, n_atoms))
    keys.append("xyz")
    values.append(np.array(xyz, dtype=float) / 10)
    keys.append("atoms")
    values.append(atoms)
    return dict(zip(keys, values))


def _to_int(int_str):
    try:
        return int(int_str)
    except ValueError:
        return None


def _to_float(float_str):
    try:
        float_str = float_str[0] + float_str[1:].replace("-", "e-").replace("+", "e+")
        return float(float_str)
    except ValueError:
        return None
