#!/usr/bin/env python
import argparse
import os

import numpy as np
from Align_two_3D_object import Structure1_translate, Structure2_add_rotate

parser = argparse.ArgumentParser(
    description="""
    Creates an *.xyz files made up of two structures (s1, s2). Automatically rotate and translate objects to each other (`rotation matrix` from 
    quaternions script). Program can be use with flag -all then you direct list with structures 1 (s1) and structure 2 (s2 dipole.xyz) - automatically 
    create main directories -> sub_directories (by structures 1) ->  *.xyz files with dipole (4 configurations: vertical, horizontal, vertical2, 
    horizontal2). Additionally creates file with informations about atoms range in new `*.xyz` structure (`atom_info` file).
    """,
    epilog="""Example: --> ./make_charge.py -s1 dir1/*.xyz -s2 dipole_name.xyz -all,  
    --> ./make_charge.py -s1 s1.xyz -s2 dipole_name.xyz""",
)
parser.add_argument(
    "-s1",
    nargs="+",
    help="structures 1 - can be either only one specific structures or path to *.xyz structures",
)
parser.add_argument(
    "-s2",
    nargs="+",
    help="structures 2 - dipole *.xyz structure",
)
parser.add_argument(
    "-all",
    action="store_true",
    help="""if active; it works on lists of structures and automatically create directories with sub_directories if not; 
    it based on one structers 1 and one structures 2 then print""",
)

options = parser.parse_args()


def to_xyz(data):
    data = np.array(["{:.5f}".format(line) for line in data.flatten()]).reshape(
        data.shape
    )
    return data


if options.all:

    def save(xyz, path):
        with open(os.path.join(dir, sub_dir1, path), "w") as f:
            f.write(str(len(xyz)) + "\n")
            f.write("XYZ file generated by Script\n")
            for coor, n in zip(xyz, name):
                f.write("{}{:>20}{:>13}{:>13}\n".format(n, coor[0], coor[1], coor[2]))
        return 1

    def atom_info(xyz1, xyz2):
        with open(os.path.join(dir, sub_dir1, f"atom_info"), "w") as f:
            f.write(
                """### Informations about range of atoms in *xyz file
### First line  - structer's 1
### Second line - structer's 2\n"""
            )
            f.write(sub_dir1 + f"=1-{len(xyz1)}\n")
            f.write(sub_dir2 + f"={1+len(xyz1)}-{len(xyz2)}\n")
        return 1

    def dft_info(nProc=8, memory=16, charge=1, multiplicity=0, base="4-31G*"):
        with open(os.path.join(dir, sub_dir1, f"dft_info"), "w") as f:
            f.write(
                f"""%NProcShared={nProc}
%mem={memory}gb
%chk=
#p b3lyp gen SCF=(xqc,Tight,intrep,NoVarAcc,Maxcycle=512) GFInput
     IOp(6/7=3) charge   iop(1/6=100)  symm=loose  int=(grid=ultrafine) scrf=(solvent=water)

test

{charge} {multiplicity}
---------------------------
{base}
****
"""
            )
        return 1

    dft_chek = False
    dft_def = input("Default DFT method [y/N]: ").lower()
    nProc = 0
    if dft_def == "" or dft_info == "y":
        dft_chek = True
    else:
        nProc = int(input("set nProc = "))

    dir = input("Type the directory name or press Enter: ")
    if dir == "":
        dir = "xyz_files"

    path = str()

    if not os.path.isdir(dir):
        os.mkdir(dir)

    for i in options.s1:
        for j in options.s2:
            obj1 = Structure1_translate(i)
            xyz_obj1 = obj1.translate_center_to_zero

            obj2 = Structure2_add_rotate(i, j)
            xyz_obj2 = obj2.rotate_2D_object
            name = np.append(obj1.get_name, obj2.get_name)

            xyz_rotated = np.append(xyz_obj1, xyz_obj2[0], axis=0).round(decimals=4)
            xyz_horizontal = np.append(xyz_obj1, xyz_obj2[1], axis=0).round(decimals=4)
            xyz_vertical = np.append(xyz_obj1, xyz_obj2[2], axis=0).round(decimals=4)
            xyz_horizontal2 = np.append(xyz_obj1, xyz_obj2[3], axis=0).round(decimals=4)

            xyz_rotated = to_xyz(xyz_rotated)
            xyz_horizontal = to_xyz(xyz_horizontal)
            xyz_vertical = to_xyz(xyz_vertical)
            xyz_horizontal2 = to_xyz(xyz_horizontal2)

            sub_dir1 = i.split("/")[-1].replace(".xyz", "")
            if not os.path.isdir(os.path.join(dir, sub_dir1)):
                os.mkdir(os.path.join(dir, sub_dir1))
            sub_dir2 = j.split("/")[-1].replace(".xyz", "")

            if "/" in i or j:
                path = i.split("/")[-1].replace(".xyz", "") + "_" + j.split("/")[-1]

            path_rotated = path.replace(".xyz", "_vertical.xyz")
            path_horizontal = path.replace(".xyz", "_horizontal.xyz")
            path_vertcial = path.replace(".xyz", "_vertical2.xyz")
            path_horizontal2 = path.replace(".xyz", "_horizontal2.xyz")

            save(xyz_rotated, path_rotated)
            save(xyz_horizontal, path_horizontal)
            save(xyz_vertical, path_vertcial)
            save(xyz_horizontal2, path_horizontal2)

            atom_info(xyz_obj1, xyz_rotated)
            if dft_chek:
                dft_info()
            else:
                dft_info(nProc=nProc)

else:
    try:
        fname1 = options.s1[0]
        fname2 = options.s2[0]
    except:
        print("Can't find arguments -s1 -s2 (*xyz files).")
    else:
        obj1 = Structure1_translate(fname1)
        xyz_obj1 = obj1.translate_center_to_zero

        obj2 = Structure2_add_rotate(fname1, fname2)
        xyz_obj2 = obj2.rotate_2D_object
        name = np.append(obj1.get_name, obj2.get_name)

        def show_xyz(structure: str):
            def printXYZ(xyz):
                print(str(len(xyz)))
                print("XYZ file generated by Script")
                for coor, n in zip(xyz, name):
                    print("{}{:>20}{:>13}{:>13}".format(n, coor[0], coor[1], coor[2]))
                return 0

            match structure:
                case "1":
                    _xyz = np.append(xyz_obj1, xyz_obj2[0], axis=0).round(decimals=4)
                    _xyz = to_xyz(_xyz)
                    return printXYZ(_xyz)
                case "2":
                    _xyz = np.append(xyz_obj1, xyz_obj2[1], axis=0).round(decimals=4)
                    _xyz = to_xyz(_xyz)
                    return printXYZ(_xyz)
                case "3":
                    _xyz = np.append(xyz_obj1, xyz_obj2[2], axis=0).round(decimals=4)
                    _xyz = to_xyz(_xyz)
                    return printXYZ(_xyz)
                case "4":
                    _xyz = np.append(xyz_obj1, xyz_obj2[3], axis=0).round(decimals=4)
                    _xyz = to_xyz(_xyz)
                    return printXYZ(_xyz)

                case _:
                    _xyz = np.append(xyz_obj1, xyz_obj2[0], axis=0).round(decimals=4)
                    _xyz = to_xyz(_xyz)
                    return printXYZ(_xyz)

        print(
            """\nSelect Rotation:
--------------------------------------------------------
    1) Vertical
    2) Horizontal
    3) Vertical2
    4) Horizontal2
    
    ENTER - DEFAULT
--------------------------------------------------------"""
        )
        show_xyz(input(""))
