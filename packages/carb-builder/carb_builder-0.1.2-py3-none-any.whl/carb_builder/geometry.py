"""
Defines the Vec3 class for 3D vector operations.
"""

import numpy as np
from openmm import Vec3 as OpenMMVec3
class Vec3:
    """Simple 3D vector class to handle positions."""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("Index out of range for Vec3")

    def length(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        length = self.length()
        if length == 0:
            return Vec3(0, 0, 0)  # Avoid division by zero
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(self.y * other.z - self.z * other.y,
                    self.z * other.x - self.x * other.z,
                    self.x * other.y - self.y * other.x)

    def to_numpy(self):
        return np.array([self.x, self.y, self.z])

    @staticmethod
    def from_numpy(array):
        return Vec3(array[0], array[1], array[2])