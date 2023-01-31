#!/usr/bin/env python
import argparse
import os
import re

parser = argparse.ArgumentParser(
    description="""
    Creates Gaussian input file *.com from *.xyz files. Program need indormations about atoms (atom_info file <--> generated autmatically by use
    make_XYZ.py script) and methods/basis set (dft_info <--> look at dft_info file example). If you want to freeze structure 1
    add flag -lock.
    """,
    epilog="""Example: --> ./make_gaussian_COM_charges.py Dir/Dir_with_XYZ_files/* -lock
    --> ./make_gaussian_COM_charges.py Dir/Dir_with_XYZ_files/*""",
)
parser.add_argument("filename", nargs="+")
parser.add_argument(
    "-lock",
    action="store_true",
    help="""if active; creates Gaussian input file with blocked first structure.""",
)

options = parser.parse_args()


def block(xyz_coor, atom):
    Q = []
    to_block = xyz_coor[: int(atom.split("-")[1])]
    unlock = xyz_coor[int(atom.split("-")[1]) :]
    for line in to_block:
        spl = line.split()
        Q.append(
            "{}{:>8}{:>12}{:>13}{:>13}\n".format(spl[0], "-1", spl[1], spl[2], spl[3])
        )

    return Q + unlock


def create_XYZ(lock=False):
    # only directories
    list_dir = (i for i in options.filename if not os.path.isfile(i))

    for path in list_dir:
        n1 = path.split("/")[-1]
        n2 = path.split("/")[-2]
        f_xyz = [f for f in os.listdir(path) if f.endswith("xyz")][0]

        with open(path + "/dft_info") as dft, open(path + "/atom_info") as atom, open(
            os.path.join(path, f_xyz)
        ) as xyz:
            dft_info = dft.readlines()
            atom_info = atom.readlines()
            atom_1 = atom_info[0][1 + atom_info[0].index("=") :].replace("\n", "")
            atom_2 = atom_info[1][1 + atom_info[1].index("=") :].replace("\n", "")
            xyz_coor = xyz.readlines()[2:]

            if lock:
                xyz_coor = block(xyz_coor, atom_1)

            idx = [i for i, item in enumerate(dft_info) if re.search("--", item)][0]
            up = dft_info[:idx]
            down = dft_info[1 + idx :]

            idx_chk = [i for i, item in enumerate(up) if "%chk" in item][0]
            up[idx_chk] = up[idx_chk].replace("\n", f"{n1}_{n2}\n")
            charge = up[-1][0]

            idx_dft = [i for i, item in enumerate(down) if re.search("^[***]", item)]

        with open(os.path.join(path, f_xyz.replace("xyz", "com")), "w") as com:
            com.write("".join(up))
            com.write("".join(xyz_coor))
            com.write("\n")
            com.write(atom_1 + " " + charge + "\n")
            com.write("".join(down[: idx_dft[1] - 1]))
            com.write(atom_2 + " " + charge + "\n")
            com.write("".join(down[idx_dft[1] - 1 :]))
            com.write("\n")


if options.lock:
    create_XYZ(lock=True)

else:
    create_XYZ()
