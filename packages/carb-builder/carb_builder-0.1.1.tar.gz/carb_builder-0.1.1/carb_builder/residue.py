"""
Defines the MonosaccharideTemplate class.
"""
from openmm import Vec3 as OpenMMVec3
class MonosaccharideTemplate:
    """Template for a monosaccharide residue with atom lists and bond definitions."""
    def __init__(self, name, atoms, bonds, special_positions=None):
        self.name = name
        self.atoms = atoms
        self.bonds = bonds
        self.special_positions = special_positions or {}