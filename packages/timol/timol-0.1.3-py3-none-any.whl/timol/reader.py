import ase.io
import numpy as np
from ase import Atoms
from ase.data import covalent_radii
from ase.data.colors import jmol_colors as atom_colors
from numpy.typing import NDArray


class MoleculesReader:
    molecules: list[Atoms]
    scale: float
    path: str

    def __init__(self, path, index: str = ":"):
        self.path = path
        # TODO npz?
        mols = ase.io.read(path, index=index)
        if isinstance(mols, Atoms):
            mols = [mols]
        self.molecules = mols
        self.ase = True

    def get_n_molecules(self) -> int:
        return len(self.molecules)

    def get_atomic_numbers(self, index: int) -> list[int]:
        atoms = self.molecules[index]
        return atoms.get_atomic_numbers()

    def get_chemical_formula(self, index: int) -> str:
        return self.molecules[index].get_chemical_formula()

    def get_n_atoms(self, index: int) -> int:
        return len(self.molecules[index])

    def get_positions(self, index: int) -> NDArray:
        atoms = self.molecules[index]
        return atoms.get_positions()

    def get_radii(self, index: int) -> NDArray:
        z = self.get_atomic_numbers(index)
        return covalent_radii[z]

    def get_spheres(self, index: int) -> tuple[float, NDArray, NDArray]:
        z = self.get_atomic_numbers(index)

        radii = covalent_radii[z]
        # colors = [f'{c[0]};{c[1]};{c[2]}' for c in atom_colors[z]]
        colors = atom_colors[z]
        r = self.get_positions(index)
        r -= np.mean(r, axis=0)

        return r, radii, colors
