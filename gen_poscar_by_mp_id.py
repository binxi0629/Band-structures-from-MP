from pymatgen.io.vasp.inputs import Incar, Poscar, Potcar, Kpoints, VaspInput
from pymatgen.ext.matproj import MPRester
import numpy as np
from pymatgen.electronic_structure.core import Spin
import json
import os
import re
from _ctypes import PyObj_FromPtr
from pymatgen.io.vasp.sets import MPRelaxSet


m = MPRester("DAS4pqHGNa5gdoRb")


def gen_poscar_by_mp_id(mp_id):
    data = m.get_data(mp_id)
    structure = m.get_structure_by_material_id(mp_id)
    poscar=Poscar(structure)

    poscar.write_file(f"{mp_id}.vasp")

    return poscar


def test():
    gen_poscar_by_mp_id("mp-2534")

test()


def main():

    save_dir = "./mp_poscars/"