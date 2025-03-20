"""
Utility functions for the carbohydrate builder package.
"""

import os
import sys
import math
from openmm import unit
from openmm import Vec3 as OpenMMVec3
def tetrahedral_vector(center, ref1, direction_index):
    """
    Calculates a tetrahedral vector.

    Args:
        center (Vec3): The position of the central atom.
        ref1 (Vec3): The position of a reference atom bonded to the central atom.
        direction_index (int): An index (0, 1, or 2) to select one of three
                              tetrahedral directions relative to the ref1-center bond.

    Returns:
        Vec3: A vector representing the tetrahedral direction.
    """
    v1 = (ref1 - center).normalize()
    if direction_index == 0:
        v2 = Vec3(1, 0, 0)
    elif direction_index == 1:
        v2 = Vec3(0, 1, 0)
    else:  # direction_index == 2
        v2 = Vec3(0, 0, 1)

    v3 = (v1.cross(v2)).normalize()
    v4 = (v1.cross(v3)).normalize()

    angle = math.acos(-1 / 3)  # Tetrahedral angle
    rotation_axis = v1
    rotated_vector = rotate_vector(v3, rotation_axis, angle)
    return rotated_vector

def rotate_vector(vector, axis, angle):
    """
    Rotates a vector around an axis by a given angle.

    Args:
        vector (Vec3): The vector to rotate.
        axis (Vec3): The axis around which to rotate.
        angle (float): The angle of rotation in radians.

    Returns:
        Vec3: The rotated vector.
    """
    x, y, z = vector.x, vector.y, vector.z
    u, v, w = axis.x, axis.y, axis.z
    a = math.cos(angle)
    b = math.sin(angle)
    rotated_x = (a + (1 - a) * u * u) * x + ((1 - a) * u * v - b * w) * y + ((1 - a) * u * w + b * v) * z
    rotated_y = ((1 - a) * u * v + b * w) * x + (a + (1 - a) * v * v) * y + ((1 - a) * v * w - b * u) * z
    rotated_z = ((1 - a) * u * w - b * v) * x + ((1 - a) * v * w + b * u) * y + (a + (1 - a) * w * w) * z
    return Vec3(rotated_x, rotated_y, rotated_z)

def get_position(positions, atom1_name, direction_vector, bond_length):
    """
    Calculates the position of an atom based on a direction vector and bond length.

    Args:
        positions (dict): A dictionary of existing atom positions.
        atom1_name (str): The name of the atom from which the new atom is bonded.
        direction_vector (Vec3): The direction vector from atom1 to the new atom.
        bond_length (float): The bond length between atom1 and the new atom (in nm).

    Returns:
        Vec3: The calculated position of the new atom.
    """
    atom1_pos = positions[atom1_name]
    new_position = atom1_pos + direction_vector * bond_length
    return new_position