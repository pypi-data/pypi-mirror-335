# Copyright (c) [2024-2025] [Laszlo Oroszlany, Daniel Pozsar]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Visualization functions
=======================

.. currentmodule:: grogupy.io.io

.. autosummary::
   :toctree: _generated/

   load_DefaultTimer
   load_Contour
   load_Kspace
   load_MagneticEntity
   load_Pair
   load_Hamiltonian
   load_Builder
   load
   save
   save_magnopy
   read_magnopy
   read_grogupy_fdf

"""
import argparse
import importlib.util
import pickle
from types import ModuleType
from typing import Union

import numpy as np
import sisl

from ..batch.timing import DefaultTimer
from ..physics.builder import Builder
from ..physics.contour import Contour
from ..physics.hamiltonian import Hamiltonian
from ..physics.kspace import Kspace
from ..physics.magnetic_entity import MagneticEntity
from ..physics.pair import Pair
from .utilities import strip_dict_structure


def load_DefaultTimer(infile: Union[str, dict]) -> DefaultTimer:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    DefaultTimer
        The DefaultTimer instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(DefaultTimer)
    out.__setstate__(infile)

    return out


def load_Contour(infile: Union[str, dict]) -> Contour:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Contour
        The Contour instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(Contour)
    out.__setstate__(infile)

    return out


def load_Kspace(infile: Union[str, dict]) -> Kspace:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Kspace
        The Kspace instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(Kspace)
    out.__setstate__(infile)

    return out


def load_MagneticEntity(infile: Union[str, dict]) -> MagneticEntity:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    MagneticEntity
        The MagneticEntity instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(MagneticEntity)
    out.__setstate__(infile)

    return out


def load_Pair(infile: Union[str, dict]) -> Pair:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Pair
        The Pair instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(Pair)
    out.__setstate__(infile)

    return out


def load_Hamiltonian(infile: Union[str, dict]) -> Hamiltonian:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Hamiltonian
        The Hamiltonian instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(Hamiltonian)
    out.__setstate__(infile)

    return out


def load_Builder(infile: Union[str, dict]) -> Builder:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Builder
        The Builder instance that was loaded
    """

    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    # build instance
    out = object.__new__(Builder)
    out.__setstate__(infile)

    return out


def load(
    infile: Union[str, dict]
) -> Union[DefaultTimer, Contour, Kspace, MagneticEntity, Pair, Hamiltonian, Builder]:
    """Recreates the instance from a pickled state.

    Parameters
    ----------
    infile : Union[str, dict]
        Either the path to the file or the appropriate
        dictionary for the setup

    Returns
    -------
    Union[DefaultTimer, Contour, Kspace, MagneticEntity, Pair, Hamiltonian, Builder]
        The instance that was loaded
    """
    # load pickled file
    if isinstance(infile, str):
        try:
            with open(infile, "rb") as file:
                infile = pickle.load(file)
        except:
            with open(infile + ".pkl", "rb") as file:
                infile = pickle.load(file)

    if list(infile.keys()) == [
        "times",
        "kspace",
        "contour",
        "hamiltonian",
        "magnetic_entities",
        "pairs",
        "_Builder__greens_function_solver",
        "_Builder__parallel_mode",
        "_Builder__architecture",
        "_Builder__matlabmode",
        "_Builder__exchange_solver",
        "_Builder__anisotropy_solver",
        "ref_xcf_orientations",
        "_rotated_hamiltonians",
        "SLURM_ID",
    ]:
        return load_Builder(infile)

    elif list(infile.keys()) == [
        "times",
        "_dh",
        "_ds",
        "infile",
        "H",
        "S",
        "scf_xcf_orientation",
        "orientation",
        "hTRS",
        "hTRB",
        "XCF",
        "H_XCF",
    ]:
        return load_Hamiltonian(infile)
    elif list(infile.keys()) == [
        "_dh",
        "M1",
        "M2",
        "supercell_shift",
        "Gij",
        "Gji",
        "_Gij_tmp",
        "_Gji_tmp",
        "energies",
        "J_iso",
        "J",
        "J_S",
        "D",
    ]:
        return load_Pair(infile)
    elif list(infile.keys()) == [
        "_dh",
        "_ds",
        "infile",
        "atom",
        "l",
        "orbital_box_indices",
        "_tags",
        "mulliken",
        "spin_box_indices",
        "xyz",
        "Vu1",
        "Vu2",
        "Gii",
        "_Gii_tmp",
        "energies",
        "K",
        "K_consistency",
    ]:
        return load_MagneticEntity(infile)
    elif list(infile.keys()) == ["times", "_Kspace__kset", "kpoints", "weights"]:
        return load_Kspace(infile)
    elif list(infile.keys()) == [
        "times",
        "_Contour__automatic_emin",
        "_eigfile",
        "_emin",
        "_emax",
        "_eset",
        "_esetp",
        "samples",
        "weights",
    ]:
        return load_Contour(infile)
    elif list(infile.keys()) == ["_DefaultTimer__start_measure", "_times"]:
        return load_DefaultTimer(infile)
    else:
        raise Exception("Unknown pickle format!")


def save(
    object: Union[
        DefaultTimer, Contour, Kspace, MagneticEntity, Pair, Hamiltonian, Builder
    ],
    path: str,
    save_memory: bool = True,
) -> None:
    """Saves the instance from a pickled state.

    Parameters
    ----------
    object : Union[DefaultTimer, Contour, Kspace, MagneticEntity, Pair, Hamiltonian, Builder]
        Object from the grogupy library
    path: str
        The path to the output file
    save_memory: bool, optional
        Wether to delete the Gij, Gji, Gij_temp, Gji_temp
        from the pairs and the Vu1, Vu2, Gii, Gii_temp from
        the magnetic entities, by default True
    """

    # check if the object is ours
    if object.__module__.split(".")[0] == "grogupy":
        # add pkl so we know it is pickled
        if not path.endswith(".pkl"):
            path += ".pkl"

        # the dictionary to be saved
        out_dict = object.__getstate__()

        # remove large objects to save memory
        if save_memory:
            out_dict = strip_dict_structure(out_dict)

        # write to file
        with open(path, "wb") as f:
            pickle.dump(out_dict, f)

    else:
        raise Exception(
            f"The object is from package {object.__module__.split('.')[0]} instead of grogupy!"
        )


def save_magnopy(
    builder: Builder,
    path: str,
    precision: Union[None, int] = None,
    comments: bool = True,
) -> None:
    """Creates a magnopy input file based on a path.

    It does not create the folder structure if the path is invalid.
    It saves to the outfile.

    Parameters
    ----------
    builder: Builder
        The system that we want to save
    path: str
        Output path
    precision: Union[None, int], optional
        The precision of the magnetic parameters in the output, if None
        everything is written, by default None
    comments: bool
        Wether to add comments in the beginning of file, by default True
    """

    if not path.endswith(".magnopy.txt"):
        path += ".magnopy.txt"

    data = builder.to_magnopy(precision=precision, comments=comments)
    with open(path, "w") as file:
        file.write(data)


def read_magnopy(file: str):
    """This function reads the magnopy input file and return a dictionary

    The dictionary contains sub-dictionaries with the section names and
    all of those sections contains a unit. Furthermore, because the main
    use of this function is to parse for magnetic entities and pair
    information it does that in the appropriate sections under the
    ``magnetic_entity`` and ``pairs`` keywords.

    Parameters
    ----------
    file: str
        Path to the ``magnopy`` input file

    Returns
    -------
    dict
        The dictionary containing all the information from the ``magnopy`` file

    Raises
    ------
    Exception
        If the unit for cell is not recognized
    Exception
        If the unit for atom is not recognized
    Exception
        If the unit for exchange is not recognized
    Exception
        If the unit for on-site is not recognized
    """

    with open(file, "r") as file:
        # select which sections and lines to parse
        lines = file.readlines()

    out: dict = dict()
    section = None
    pair = None
    full_matrix = 0
    for line in lines:
        # remove comments from line
        comment = line.find("#")
        line = line[:comment]
        # check for empty line
        if len(line.split()) == 0:
            continue

        # if we are in the matrix of a pair we have to read the next couple of lines
        if full_matrix > 0:
            if full_matrix == 3:
                pair["J"] = np.empty((3, 3))
                pair["J"][0] = np.array(line.split(), dtype=float)
            elif full_matrix == 2:
                pair["J"][1] = np.array(line.split(), dtype=float)
            elif full_matrix == 1:
                pair["J"][2] = np.array(line.split(), dtype=float)
            # the row is read, continue
            full_matrix -= 1
            continue

        # if section is not set, look for sections
        elif section is None:
            unit = None
            if line.split()[0].lower() == "cell":
                section = "cell"
                # unit is given
                if len(line.split()) > 1:
                    # only the first letter is checked and it is case-insensitive
                    unit = line.split()[1][0].lower()
                    if unit not in {"a", "b"}:
                        raise Exception("Unknown unit for cell")
                else:
                    unit = "a"

                # create cell part in the dictionary
                out["cell"] = dict()
                out["cell"]["unit"] = unit

            elif line.split()[0].lower() == "atoms":
                section = "atoms"
                # unit is given
                if len(line.split()) > 1:
                    # only the first letter is checked and it is case-insensitive
                    unit = line.split()[1][0].lower()
                    if unit not in {"a", "b"}:
                        raise Exception("Unknown unit for atoms")
                else:
                    unit = "a"

                # create cell part in the dictionary
                out["atoms"] = dict()
                out["atoms"]["unit"] = unit
                out["atoms"]["magnetic_entities"] = []

            elif line.split()[0].lower() == "notation":
                section = "notation"
                unit = None

            elif line.split()[0].lower() == "exchange":
                section = "exchange"
                # unit is given
                if len(line.split()) > 1:
                    # only the first letter is checked and it is case-insensitive
                    unit = line.split()[1][0].lower()
                    if unit not in {"m", "e", "j", "k", "r"}:
                        raise Exception("Unknown unit for exchange")
                else:
                    unit = "m"

                # create cell part in the dictionary
                out["exchange"] = dict()
                out["exchange"]["unit"] = unit
                out["exchange"]["pairs"] = []

            elif line.split()[0].lower() == "on-site":
                section = "on-site"
                # unit is given
                if len(line.split()) > 1:
                    # only the first letter is checked and it is case-insensitive
                    unit = line.split()[1][0].lower()
                    if unit not in {"m", "e", "j", "k", "r"}:
                        raise Exception("Unknown unit for on-site")
                else:
                    unit = "m"

                # create cell part in the dictionary
                out["on-site"] = dict()
                out["on-site"]["unit"] = unit
                out["on-site"]["magnetic_entities"] = []

            # we parsed the line
            continue

        # if section separator found set section for None
        if line[:10] == "==========":
            section = None
            atom = None
            pair = None
            continue

        # these are not needed for pair information
        if section == "cell":
            continue
        elif section == "notation":
            continue
        elif section == "on-site":
            if line[:10] == "----------":
                if atom is None:
                    continue
                else:
                    out["on-site"]["magnetic_entities"].append(atom)
                    atom = None

            elif len(line.split()) == 1:
                atom = dict(tag=line.split()[0])

            elif len(line.split()) == 6:
                atom["K"] = np.array([float(i) for i in line.split()])

        # these are needed for pair information
        # magnetic entities
        elif section == "atoms":
            # the name line
            if line.split()[0].lower() == "name":
                x_pos = np.where([word == "x" for word in line.split()])
                y_pos = np.where([word == "y" for word in line.split()])
                z_pos = np.where([word == "z" for word in line.split()])
            # magnetic entity line
            else:
                tag = line.split()[0]
                x = float(np.array(line.split())[x_pos])
                y = float(np.array(line.split())[y_pos])
                z = float(np.array(line.split())[z_pos])

                atom = dict(tag=tag, xyz=np.array([x, y, z]))
                out["atoms"]["magnetic_entities"].append(atom)

        elif section == "exchange":
            if line[:10] == "----------":
                if pair is None:
                    continue
                else:
                    out["exchange"]["pairs"].append(pair)
                    pair = None

            # isotropic keyword
            elif line.split()[0][0].lower() == "i":
                pair["iso"] = float(line.split()[1])

            # Dzyaloshinskii-Morilla keyword
            elif line.split()[0][0].lower() == "d":
                dx = float(line.split()[1])
                dy = float(line.split()[2])
                dz = float(line.split()[3])
                pair["DM"] = np.array([dx, dy, dz])

            # symmetric-anisotropy keyword
            elif line.split()[0][0].lower() == "s":
                sxx = float(line.split()[1])
                syy = float(line.split()[2])
                sxy = float(line.split()[3])
                sxz = float(line.split()[4])
                syz = float(line.split()[5])
                pair["S"] = np.array([sxx, syy, sxy, sxz, syz])

            # full matrix
            elif line.split()[0][0].lower() == "m":
                # this will avoid the whole loop and force to read the next 3 rows
                full_matrix = 3

            # tags and unit cell shift
            else:
                pair = dict()
                pair["tag1"] = line.split()[0]
                pair["tag2"] = line.split()[1]
                i = int(line.split()[2])
                j = int(line.split()[3])
                k = int(line.split()[4])

                pair["Ruc"] = np.array([i, j, k])

        else:
            continue

    for pair in out["exchange"]["pairs"]:
        for i, mag_ent in enumerate(out["atoms"]["magnetic_entities"]):
            if pair["tag1"] == mag_ent["tag"]:
                pair["xyz1"] = mag_ent["xyz"]
            if pair["tag2"] == mag_ent["tag"]:
                pair["xyz2"] = mag_ent["xyz"]

    return out


def read_fdf(path: str) -> tuple[dict, list, list]:
    """It reads the simulation parameters, magnetic entities and pairs from the fdf

    Parameters
    ----------
        path: str
            The path to the .fdf file

    Returns
    -------
        fdf_arguments: dict
            The read input arguments from the fdf file
        magnetic_entities: list
            It contains the dictionaries associated with the magnetic entities
        pairs: list
            It contains the dictionaries associated with the pair information
    """

    # read fdf file
    fdf = sisl.io.fdfSileSiesta(path)
    fdf_arguments = dict()

    InputFile = fdf.get("InputFile")
    if InputFile is not None:
        fdf_arguments["infile"] = InputFile

    OutputFile = fdf.get("OutputFile")
    if OutputFile is not None:
        fdf_arguments["outfile"] = OutputFile

    ScfXcfOrientation = fdf.get("ScfXcfOrientation")
    if ScfXcfOrientation is not None:
        fdf_arguments["scf_xcf_orientation"] = np.array(
            ScfXcfOrientation.split()[:3], dtype=float
        )

    XCF_Rotation = fdf.get("XCF_Rotation")
    if XCF_Rotation is not None:
        rotations = []
        # iterate over rows
        for rot in XCF_Rotation:
            # convert row to dictionary
            dat = np.array(rot.split()[:9], dtype=float)
            o = dat[:3]
            vw = dat[3:].reshape(2, 3)
            rotations.append(dict(o=o, vw=vw))
        fdf_arguments["ref_xcf_orientations"] = rotations

    Kset = fdf.get("INTEGRAL.Kset")
    if Kset is not None:
        fdf_arguments["kset"] = int(Kset)

    Kdirs = fdf.get("INTEGRAL.Kdirs")
    if Kdirs is not None:
        fdf_arguments["kdirs"] = Kdirs

    # This is permitted because it means automatic Ebot definition
    ebot = fdf.get("INTEGRAL.Ebot")
    try:
        fdf_arguments["ebot"] = float(ebot)
    except:
        fdf_arguments["ebot"] = None

    Eset = fdf.get("INTEGRAL.Eset")
    if Eset is not None:
        fdf_arguments["eset"] = int(Eset)

    Esetp = fdf.get("INTEGRAL.Esetp")
    if Esetp is not None:
        fdf_arguments["esetp"] = float(Esetp)

    ParallelSolver = fdf.get("GREEN.ParallelSolver")
    if ParallelSolver is not None:
        fdf_arguments["parallel_solver_for_Gk"] = bool(ParallelSolver)

    PadawanMode = fdf.get("PadawanMode")
    if PadawanMode is not None:
        fdf_arguments["padawan_mode"] = bool(PadawanMode)

    Pairs = fdf.get("Pairs")
    if Pairs is not None:
        pairs = []
        # iterate over rows
        for fdf_pair in Pairs:
            # convert data
            dat = np.array(fdf_pair.split()[:5], dtype=int)
            # create pair dictionary
            my_pair = dict(ai=dat[0], aj=dat[1], Ruc=np.array(dat[2:]))
            pairs.append(my_pair)

    MagneticEntities = fdf.get("MagneticEntities")
    if MagneticEntities is not None:
        magnetic_entities = []
        # iterate over magnetic entities
        for mag_ent in MagneticEntities:
            # drop comments from data
            row = mag_ent.split()
            dat = []
            for string in row:
                if string.find("#") != -1:
                    break
                dat.append(string)
            # cluster input
            if dat[0] in {"Cluster", "cluster"}:
                magnetic_entities.append(dict(atom=[int(_) for _ in dat[1:]]))
                continue
            # atom input, same as cluster, but raises
            # error when multiple atoms are given
            if dat[0] in {"Atom", "atom"}:
                if len(dat) > 2:
                    raise Exception("Atom input must be a single integer")
                magnetic_entities.append(dict(atom=int(dat[1])))
                continue
            # atom and shell information
            elif dat[0] in {"AtomShell", "Atomshell", "atomShell", "atomshell"}:
                magnetic_entities.append(
                    dict(atom=int(dat[1]), l=[int(_) for _ in dat[2:]])
                )
                continue
            # atom and orbital information
            elif dat[0] in {"AtomOrbital", "Atomorbital", "tomOrbital", "atomorbital"}:
                magnetic_entities.append(
                    dict(atom=int(dat[1]), orb=[int(_) for _ in dat[2:]])
                )
                continue
            # orbital information
            elif dat[0] in {"Orbitals", "orbitals"}:
                magnetic_entities.append(dict(orb=[int(_) for _ in dat[1:]]))
                continue
            else:
                raise Exception("Unrecognizable magnetic entity in .fdf!")

    return fdf_arguments, magnetic_entities, pairs


def read_command_line(citation: str) -> Union[None, ModuleType]:
    """Reading command line parameters for command line tools.

    Options:
    The first argument is a .py file
    that contains the input parameters.
    --cite returns citations

    Parameters
    ----------
    citation: str
        The citation that should be printed.

    Returns
    -------
    params : Union[None, ModuleType]
        The input parameters
    """

    # setup parser
    parser = argparse.ArgumentParser(
        description="Load Python variables from a .py file."
    )
    parser.add_argument(
        "file", nargs="?", help="Path to a Python file containing variables to load"
    )
    parser.add_argument(
        "--cite",
        dest="cite",
        action="store_true",
        default=False,
        help="Print the citation of the package",
    )
    # parameters from command line
    args = parser.parse_args()

    # print citation if needed
    if args.cite:
        print(citation)
        if args.file is None:
            return

    # Create the spec
    spec = importlib.util.spec_from_file_location(
        "grogupy_command_line_input", args.file
    )

    # Create the module
    params = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(params)

    return params


if __name__ == "__main__":
    pass
