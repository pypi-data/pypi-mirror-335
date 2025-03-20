"""
Defines the CarbohydrateBuilder class for constructing carbohydrate structures.
"""

import math
import os
from openmm.app import *
from openmm import *
from openmm.unit import *
from geometry import Vec3  # Import from within the package
from residue import MonosaccharideTemplate
#rom utils import check_dependencies  # Import utility function

class CarbohydrateBuilder:
    """Builder class for carbohydrate structures"""
    
    # Standard bond lengths in nm
    BOND_LENGTHS = {
        'C-C': 0.154,    # Carbon-carbon single bond
        'C-O': 0.143,    # Carbon-oxygen single bond
        'C-N': 0.147,    # Carbon-nitrogen single bond
        'C-H': 0.109,    # Carbon-hydrogen bond
        'O-H': 0.096,    # Oxygen-hydrogen bond 
        'N-H': 0.101,    # Nitrogen-hydrogen bond
        'C1-O4': 0.136,  # Glycosidic bond (C1-O4)
    }
    
    # Tetrahedral angle in radians
    TETRAHEDRAL_ANGLE = 109.5 * math.pi / 180
    
    # Glycosidic linkage parameters
    GLYCOSIDIC_ANGLE = 116.0 * math.pi / 180
    
    def __init__(self, output_dir="./"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.residue_templates = {}
        self.register_standard_templates()
    
    def register_standard_templates(self):
        """Register standard monosaccharide templates"""

        # Define 0Yn template (first residue in chain)
        atoms_0Yn = ['O6', 'H6O', 'C6', 'H6A', 'H6B', 'C5', 'H5', 'C4', 'O4', 'H4O', 
                     'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 'H2', 'H2A', 'H2B', 'C1', 'H1', 'O5', 'H4']
        bonds_0Yn = [
            ('O6', 'H6O'), ('O6', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'C5'),
            ('C5', 'H5'), ('C5', 'C4'), ('C5', 'O5'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'O4'),
            ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'), ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'),
            ('N2', 'H2A'), ('N2', 'H2B'), ('O3', 'H3O'), ('O4', 'H4O'),
            ('O5', 'C1'), ('C1', 'H1')
        ]
        atoms_0YB = ['O6', 'H6O', 'C6', 'H6A', 'H6B', 'C5', 'H5', 'C4', 'O4', 'H4O', 
                 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 'H2', 'H2A', 'C2N', 'O2N', 'CME', 'H1M', 'H2M', 'H3M', 'C1', 'H1', 'O5', 'H4']
        bonds_0YB = [
            ('O6', 'H6O'), ('O6', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'C5'),
            ('C5', 'H5'), ('C5', 'C4'), ('C5', 'O5'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'O4'),
            ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'), ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'),
            ('N2', 'H2A'), ('N2', 'C2N'), ('C2N', 'O2N'), ('C2N', 'CME'), ('CME', 'H1M'), ('CME', 'H2M'), ('CME', 'H3M'), 
            ('O3', 'H3O'), ('O4', 'H4O'), ('O5', 'C1'), ('C1', 'H1')
        ]

        atoms_0YP = ['O6', 'H6O', 'C6', 'H6A', 'H6B', 'C5', 'H5', 'C4', 'O4', 'H4O', 
                     'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 'H2', 'H2A', 'H2B','H2C', 'C1', 'H1', 'O5', 'H4']
        bonds_0YP = [
            ('O6', 'H6O'), ('O6', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'C5'),
            ('C5', 'H5'), ('C5', 'C4'), ('C5', 'O5'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'O4'),
            ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'), ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'),
            ('N2', 'H2A'), ('N2', 'H2B'),('N2', 'H2C'), ('O3', 'H3O'), ('O4', 'H4O'),
            ('O5', 'C1'), ('C1', 'H1')
        ]
        # Define 4Yn template (middle residues)
        atoms_4Yn = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 
                     'H2', 'H2A', 'H2B', 'C1', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O', 'O5']
        bonds_4Yn = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'), ('N2', 'H2A'), ('N2', 'H2B'), ('O3', 'H3O'),
            ('C5', 'C6'), ('C5', 'H5'), ('C5', 'O5'), ('C6', 'O6'), ('C6', 'H6A'), ('C6', 'H6B'),
            ('O6', 'H6O'), ('O5', 'C1'), ('C1', 'H1')
        ]

        # Define 4Yn template (middle residues)
        atoms_4YP = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 
                     'H2', 'H2A', 'H2B','H2C', 'C1', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O', 'O5']
        bonds_4YP = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'), ('N2', 'H2A'), ('N2', 'H2B'),('N2', 'H2C'), ('O3', 'H3O'),
            ('C5', 'C6'), ('C5', 'H5'), ('C5', 'O5'), ('C6', 'O6'), ('C6', 'H6A'), ('C6', 'H6B'),
            ('O6', 'H6O'), ('O5', 'C1'), ('C1', 'H1')
        ]

        atoms_4YB = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 
                     'H2', 'H2A', 'C2N','O2N','CME','H1M','H2M','H3M', 'C1', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O', 'O5']
        bonds_4YB = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'N2'), ('C2', 'H2'), ('C2', 'C1'), ('N2', 'H2A'), ('N2', 'C2N'),('C2N', 'O2N'),('C2N', 'CME'),('CME', 'H1M'),
            ('CME', 'H2M'),('CME', 'H3M'),('O3', 'H3O'),('C5', 'C6'), ('C5', 'H5'), ('C5', 'O5'), ('C6', 'O6'), ('C6', 'H6A'), ('C6', 'H6B'),
            ('O6', 'H6O'), ('O5', 'C1'), ('C1', 'H1')
        ]
        
        # Define rYn template (final residue)
        atoms_rYn = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 'H2', 
                     'H2A', 'H2B', 'C1', 'O5', 'O1', 'H1O', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O']
        bonds_rYn = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'C1'), ('C2', 'N2'), ('C2', 'H2'), ('C1', 'O5'), ('C1', 'O1'), ('C1', 'H1'),
            ('O5', 'C5'), ('O1', 'H1O'), ('N2', 'H2A'), ('N2', 'H2B'), ('O3', 'H3O'),
            ('C5', 'H5'), ('C5', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'O6'), ('O6', 'H6O')
        ]

        atoms_rYP = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 'H2', 
                     'H2A', 'H2B','H2C', 'C1', 'O5', 'O1', 'H1O', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O']
        bonds_rYP = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'C1'), ('C2', 'N2'), ('C2', 'H2'), ('C1', 'O5'), ('C1', 'O1'), ('C1', 'H1'),
            ('O5', 'C5'), ('O1', 'H1O'), ('N2', 'H2A'), ('N2', 'H2B'),('N2', 'H2C'), ('O3', 'H3O'),
            ('C5', 'H5'), ('C5', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'O6'), ('O6', 'H6O')
        ]

        atoms_rYB = ['O4', 'C4', 'H4', 'C5', 'H5', 'C3', 'O3', 'H3O', 'H3', 'C2', 'N2', 
                 'H2', 'H2A', 'C2N', 'O2N', 'CME', 'H1M', 'H2M', 'H3M', 'C1', 'O5', 'O1', 'H1O', 'H1', 'C6', 'H6A', 'H6B', 'O6', 'H6O']
        bonds_rYB = [
            ('O4', 'C4'), ('C4', 'C3'), ('C4', 'H4'), ('C4', 'C5'), ('C3', 'C2'), ('C3', 'O3'), ('C3', 'H3'),
            ('C2', 'C1'), ('C2', 'N2'), ('C2', 'H2'), ('N2', 'H2A'), ('N2', 'C2N'), ('C2N', 'O2N'), ('C2N', 'CME'),
            ('CME', 'H1M'), ('CME', 'H2M'), ('CME', 'H3M'), ('C1', 'O5'), ('C1', 'O1'), ('C1', 'H1'),
            ('O5', 'C5'), ('O1', 'H1O'), ('O3', 'H3O'), ('C5', 'H5'), ('C5', 'C6'), ('C6', 'H6A'), ('C6', 'H6B'), ('C6', 'O6'), ('O6', 'H6O')
        ]
        atoms_ROH = ['HO1', 'O1']
        bonds_ROH = [('O1', 'HO1')]

        # Register the templates
        self.register_template(MonosaccharideTemplate("0Yn", atoms_0Yn, bonds_0Yn))
        self.register_template(MonosaccharideTemplate("0YP", atoms_0YP, bonds_0YP))
        self.register_template(MonosaccharideTemplate("4Yn", atoms_4Yn, bonds_4Yn))
        self.register_template(MonosaccharideTemplate("4YP", atoms_4YP, bonds_4YP))
        self.register_template(MonosaccharideTemplate("rYn", atoms_rYn, bonds_rYn))
        self.register_template(MonosaccharideTemplate("rYP", atoms_rYP, bonds_rYP))
        self.register_template(MonosaccharideTemplate("4YB", atoms_4YB, bonds_4YB))
        self.register_template(MonosaccharideTemplate("0YB", atoms_0YB, bonds_0YB))
        self.register_template(MonosaccharideTemplate("rYB", atoms_rYB, bonds_rYB))
        self.register_template(MonosaccharideTemplate("ROH", atoms_ROH, bonds_ROH))

    def register_template(self, template):
        """Register a new monosaccharide template"""
        self.residue_templates[template.name] = template
    
    def generate_ring_positions(self):
        """Generate a pyranose ring in chair conformation"""
        positions = {}
        r = self.BOND_LENGTHS['C-C']  # Use C-C bond length for ring size calculation
        
        # Define basic positions for a typical chair conformation
        positions['C1'] = Vec3(0.0, 0.0, 0.05)
        positions['C2'] = Vec3(r * math.cos(0), r * math.sin(0), -0.05)
        positions['C3'] = Vec3(r * math.cos(self.TETRAHEDRAL_ANGLE), r * math.sin(self.TETRAHEDRAL_ANGLE), 0.05)
        positions['C4'] = Vec3(2*r * math.cos(self.TETRAHEDRAL_ANGLE/2),
                                2*r * math.sin(self.TETRAHEDRAL_ANGLE/2), -0.05) 
        positions['C5'] = Vec3(r * math.cos(self.TETRAHEDRAL_ANGLE/2),
                                r * math.sin(self.TETRAHEDRAL_ANGLE/2), 0.05)
        positions['O5'] = Vec3(-r * math.cos(self.TETRAHEDRAL_ANGLE/2),
                                -r * math.sin(self.TETRAHEDRAL_ANGLE/2), -0.05)
        return positions
    
    def tetrahedral_vector(self, base_pos, ref_pos, direction_index):
        """Create a tetrahedral direction vector"""
        base_direction = Vec3(base_pos.x - ref_pos.x, 
                              base_pos.y - ref_pos.y, 
                              base_pos.z - ref_pos.z).normalize()
        
        # Create an orthogonal vector
        if abs(base_direction.x) < abs(base_direction.y):
            ortho1 = Vec3(0, -base_direction.z, base_direction.y)
        else:
            ortho1 = Vec3(-base_direction.z, 0, base_direction.x)
        ortho1 = ortho1.normalize()
        ortho2 = base_direction.cross(ortho1)
        
        if direction_index == 0:
            return base_direction
        elif direction_index == 1:
            angle = self.TETRAHEDRAL_ANGLE / 2
            return Vec3(
                base_direction.x * math.cos(angle) + ortho1.x * math.sin(angle),
                base_direction.y * math.cos(angle) + ortho1.y * math.sin(angle),
                base_direction.z * math.cos(angle) + ortho1.z * math.sin(angle)
            )
        elif direction_index == 2:
            angle = self.TETRAHEDRAL_ANGLE / 2
            return Vec3(
                base_direction.x * math.cos(angle) + ortho2.x * math.sin(angle),
                base_direction.y * math.cos(angle) + ortho2.y * math.sin(angle),
                base_direction.z * math.cos(angle) + ortho2.z * math.sin(angle)
            )
        else:
            angle = self.TETRAHEDRAL_ANGLE / 2
            combined = (ortho1 + ortho2).normalize()
            return Vec3(
                base_direction.x * math.cos(angle) + combined.x * math.sin(angle),
                base_direction.y * math.cos(angle) + combined.y * math.sin(angle),
                base_direction.z * math.cos(angle) + combined.z * math.sin(angle)
            )
    
    def get_position(self, positions, base_atom, direction_vector, bond_length):
        """Get position based on base atom and direction vector"""
        return positions[base_atom] + direction_vector * bond_length
    
    def generate_residue_positions(self, residue_type, flip_nitro=False):
        """Generate positions for all atoms in a residue based on its type"""
        positions = self.generate_ring_positions()
        template = self.residue_templates.get(residue_type)
        if not template:
            raise ValueError(f"Unknown residue type: {residue_type}")
        
        # Use accurate bond lengths
        c_h = self.BOND_LENGTHS['C-H']
        c_o = self.BOND_LENGTHS['C-O']
        o_h = self.BOND_LENGTHS['O-H'] 
        c_n = self.BOND_LENGTHS['C-N']
        n_h = self.BOND_LENGTHS['N-H']
        c_c = self.BOND_LENGTHS['C-C']
        
        # C1 substituents
        c1_h_dir = self.tetrahedral_vector(positions['C1'], positions['C2'], 0)
        positions['H1'] = self.get_position(positions, 'C1', c1_h_dir, c_h)
        if residue_type == 'rYn' or 'rYB' or 'rYP' or 'ROH':
            c1_o1_dir = self.tetrahedral_vector(positions['C1'], positions['C2'], 1)
            positions['O1'] = self.get_position(positions, 'C1', c1_o1_dir, c_o)
            o1_h_dir = self.tetrahedral_vector(positions['O1'], positions['C1'], 0)
            positions['H1O'] = self.get_position(positions, 'O1', o1_h_dir, o_h)
        
        # C2 substituents with nitro group orientation control
        c2_h_dir = self.tetrahedral_vector(positions['C2'], positions['C3'], 0)
        positions['H2'] = self.get_position(positions, 'C2', c2_h_dir, c_h)
        if flip_nitro:
            c2_n_dir = self.tetrahedral_vector(positions['C2'], positions['C3'], 1)
            c2_n_dir = Vec3(c2_n_dir.x, c2_n_dir.y, -abs(c2_n_dir.z))
        else:
            c2_n_dir = self.tetrahedral_vector(positions['C2'], positions['C3'], 1)
            c2_n_dir = Vec3(c2_n_dir.x, c2_n_dir.y, abs(c2_n_dir.z))
        positions['N2'] = self.get_position(positions, 'C2', c2_n_dir, c_n)
        if residue_type in ['4YP', '0YP','rYP']:
            n2_h1_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 0)
            n2_h2_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 1)
            n2_h3_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 2)
            positions['H2A'] = self.get_position(positions, 'N2', n2_h1_dir, n_h)
            positions['H2B'] = self.get_position(positions, 'N2', n2_h2_dir, n_h)
            positions['H2C'] = self.get_position(positions, 'N2', n2_h3_dir, n_h)
        elif residue_type in ['4Yn', 'rYn','0Yn']:
            n2_h1_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 0)
            n2_h2_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 1)
            positions['H2A'] = self.get_position(positions, 'N2', n2_h1_dir, n_h)
            positions['H2B'] = self.get_position(positions, 'N2', n2_h2_dir, n_h)

            # Acetylated substituents
        elif residue_type in ['4YB', 'rYB','0YB']:
            n2_h1_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 0)
            positions['H2A'] = self.get_position(positions, 'N2', n2_h1_dir, n_h)

            n2_c2n_dir = self.tetrahedral_vector(positions['N2'], positions['C2'], 1) # Corrected reference atom
            positions['C2N'] = self.get_position(positions, 'N2', n2_c2n_dir, c_n) # Corrected bond length

            c2n_o2n_dir = self.tetrahedral_vector(positions['C2N'], positions['N2'], 0) # Corrected reference atom
            positions['O2N'] = self.get_position(positions, 'C2N', c2n_o2n_dir, c_o)

            c2n_cme_dir = self.tetrahedral_vector(positions['C2N'], positions['O2N'], 1) # Corrected reference atom
            positions['CME'] = self.get_position(positions, 'C2N', c2n_cme_dir, c_c) # Corrected bond length

            # Corrected: Calculate a unique direction vector for each methyl hydrogen
            cme_h1m_dir = self.tetrahedral_vector(positions['CME'], positions['O2N'], 0)
            positions['H1M'] = self.get_position(positions, 'CME', cme_h1m_dir, c_h)

            cme_h2m_dir = self.tetrahedral_vector(positions['CME'], positions['O2N'], 1)
            positions['H2M'] = self.get_position(positions, 'CME', cme_h2m_dir, c_h)

            cme_h3m_dir = self.tetrahedral_vector(positions['CME'], positions['O2N'], 2)
            positions['H3M'] = self.get_position(positions, 'CME', cme_h3m_dir, c_h)
            
        # C3 substituents
        c3_h_dir = self.tetrahedral_vector(positions['C3'], positions['C4'], 0)
        positions['H3'] = self.get_position(positions, 'C3', c3_h_dir, c_h)
        c3_o_dir = self.tetrahedral_vector(positions['C3'], positions['C4'], 1)
        positions['O3'] = self.get_position(positions, 'C3', c3_o_dir, c_o)
        o3_h_dir = self.tetrahedral_vector(positions['O3'], positions['C3'], 0)
        positions['H3O'] = self.get_position(positions, 'O3', o3_h_dir, o_h)
        
        # C4 substituents
        c4_h_dir = self.tetrahedral_vector(positions['C4'], positions['C5'], 0)
        positions['H4'] = self.get_position(positions, 'C4', c4_h_dir, c_h)
        c4_o_dir = self.tetrahedral_vector(positions['C4'], positions['C5'], 1)
        positions['O4'] = self.get_position(positions, 'C4', c4_o_dir, c_o)
        if residue_type == '0Yn' or '0YP' or '0YB':
            o4_h_dir = self.tetrahedral_vector(positions['O4'], positions['C4'], 0)
            positions['H4O'] = self.get_position(positions, 'O4', o4_h_dir, o_h)
        
        # C5 substituents
        c5_h_dir = self.tetrahedral_vector(positions['C5'], positions['C4'], 0)
        positions['H5'] = self.get_position(positions, 'C5', c5_h_dir, c_h)
        c5_c6_dir = self.tetrahedral_vector(positions['C5'], positions['C4'], 1)
        positions['C6'] = self.get_position(positions, 'C5', c5_c6_dir, c_c)
        
        # C6 substituents
        c6_h1_dir = self.tetrahedral_vector(positions['C6'], positions['C5'], 0)
        c6_h2_dir = self.tetrahedral_vector(positions['C6'], positions['C5'], 1)
        c6_o_dir = self.tetrahedral_vector(positions['C6'], positions['C5'], 2)
        positions['H6A'] = self.get_position(positions, 'C6', c6_h1_dir, c_h)
        positions['H6B'] = self.get_position(positions, 'C6', c6_h2_dir, c_h)
        positions['O6'] = self.get_position(positions, 'C6', c6_o_dir, c_o)
        o6_h_dir = self.tetrahedral_vector(positions['O6'], positions['C6'], 0)
        positions['H6O'] = self.get_position(positions, 'O6', o6_h_dir, o_h)
        
        return positions
    
    def rotate_around_axis(self, positions, axis, angle):
        """Rotate positions around an axis"""
        rotated_positions = {}
        axis = axis.normalize()
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1.0 - c
        r11 = t * axis.x * axis.x + c
        r12 = t * axis.x * axis.y - s * axis.z
        r13 = t * axis.x * axis.z + s * axis.y
        r21 = t * axis.x * axis.y + s * axis.z
        r22 = t * axis.y * axis.y + c
        r23 = t * axis.y * axis.z - s * axis.x
        r31 = t * axis.x * axis.z - s * axis.y
        r32 = t * axis.y * axis.z + s * axis.x
        r33 = t * axis.z * axis.z + c
        
        for atom, pos in positions.items():
            rotated_positions[atom] = Vec3(
                r11 * pos.x + r12 * pos.y + r13 * pos.z,
                r21 * pos.x + r22 * pos.y + r23 * pos.z,
                r31 * pos.x + r32 * pos.y + r33 * pos.z
            )
        return rotated_positions
    
    def translate_positions(self, positions, translation_vector):
        """Translate positions by a vector"""
        translated_positions = {}
        for atom, pos in positions.items():
            translated_positions[atom] = pos + translation_vector
        return translated_positions
    
    def distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = pos1.z - pos2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def check_clashes(self, positions, clash_threshold=0.15):
        """Check for steric clashes between atoms"""
        clashes = False
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                # Skip atoms from the same or adjacent residues
                atom_i_res_idx = i // 20  # Approximate atoms per residue
                atom_j_res_idx = j // 20
                if abs(atom_i_res_idx - atom_j_res_idx) <= 1:
                    continue
                dist = self.distance(positions[i], positions[j])
                if dist < clash_threshold:
                    clashes = True
                    print(f"Clash detected between atoms {i} and {j}: distance = {dist:.3f} nm")
        return clashes
    
    def build_topology(self, residue_sequence, num_chains = int):
        """Build a topology from a sequence of residue types"""
        topology = Topology()
        chains = []
        for i in range(num_chains):
            chain = topology.addChain()
            chains.append(chain)
        #chain = topology.addChain()
        # Add residues and atoms
        for chain in chains:
            for residue_type in residue_sequence:
                if residue_type not in self.residue_templates:
                    raise ValueError(f"Unknown residue type: {residue_type}")
                template = self.residue_templates[residue_type]
                residue = topology.addResidue(residue_type, chain)
                for atom_name in template.atoms:
                    element = Element.getBySymbol(atom_name[0]) if atom_name[0] in ['C', 'O', 'N', 'H'] else Element.getBySymbol('H')
                    topology.addAtom(atom_name, element, residue)
        # Add intra-residue bonds
        for i, residue in enumerate(topology.residues()):
            template = self.residue_templates[residue.name]
            atoms = {atom.name: atom for atom in residue.atoms()}
            for atom1, atom2 in template.bonds:
                topology.addBond(atoms[atom1], atoms[atom2])
        # Add inter-residue glycosidic bonds (C1 of residue i to O4 of residue i+1)
        for chain in chains:
            residues = [r for r in topology.residues() if r.chain == chain]
            for i in range(len(residues) - 1):
                residue1 = residues[i]
                residue2 = residues[i + 1]
                try:
                    c1 = next(atom for atom in residue1.atoms() if atom.name == 'C1')
                    o4 = next(atom for atom in residue2.atoms() if atom.name == 'O4')
                    topology.addBond(c1, o4)
                except StopIteration:
                    print(f"Warning: Could not create glycosidic bond between residue {i} and {i+1}.  Atom 'O4' is missing in residue {residue2.name}.")
                    pass  # Skip adding the bond
        return topology
    
    def build_carbowhydrate(self, residue_sequence, z_offset=0.35, num_chains=2):
        """Build multiple carbohydrate chains from a sequence of residue types"""
        topology = self.build_topology(residue_sequence, num_chains)
        positions = []
        residues = list(topology.residues())
        
        for chain_idx in range(num_chains):
            chain_residues = [r for r in residues if r.chain.index == chain_idx]
            n = len(chain_residues)
            prev_c1_pos = None
            prev_o5_pos = None
            
            for i in range(n):
                residue = chain_residues[i]
                flip_nitro = (i % 2 == 1)
                
                if i == 0:
                    base_positions = self.generate_residue_positions(residue.name, flip_nitro)
                    for atom in residue.atoms():
                        positions.append(base_positions[atom.name])
                    prev_c1_pos = base_positions['C1']
                    prev_o5_pos = base_positions['O5']
                else:
                    base_positions = self.generate_residue_positions(residue.name, flip_nitro)
                    rotation_axis = Vec3(
                        prev_o5_pos.y - prev_c1_pos.y,
                        prev_c1_pos.x - prev_o5_pos.x,
                        0.0
                    )
                    angle = self.GLYCOSIDIC_ANGLE if i % 2 == 1 else -self.GLYCOSIDIC_ANGLE
                    rotated_positions = self.rotate_around_axis(base_positions, rotation_axis, angle)
                    o4_current_pos = rotated_positions['O4']
                    c1_prev_to_o4 = (prev_c1_pos - o4_current_pos).normalize()
                    glycosidic_distance = self.BOND_LENGTHS['C1-O4']
                    translation_vector = prev_c1_pos + c1_prev_to_o4 * glycosidic_distance - o4_current_pos
                    final_positions = self.translate_positions(rotated_positions, translation_vector)
                    for atom in residue.atoms():
                        pos = final_positions[atom.name]
                        adjusted_pos = Vec3(pos.x, pos.y, pos.z + z_offset * i)
                        positions.append(adjusted_pos)
                    prev_c1_pos = final_positions['C1'] + Vec3(0, 0, z_offset * i)
                    prev_o5_pos = final_positions['O5'] + Vec3(0, 0, z_offset * i)
        return topology, positions

    def build_carbohydrate(self, residue_sequence, z_offset=0.35, num_chains=int):
        """Build a carbohydrate structure from a sequence of residue types"""
        topology = self.build_topology(residue_sequence, num_chains)
        positions = []
        residues = list(topology.residues())
        n = len(residues)
        for i in range(n):
            residue = residues[i]
            flip_nitro = (i % 2 == 1)
            if i == 0:
                base_positions = self.generate_residue_positions(residue.name, flip_nitro)
                for atom in residue.atoms():
                    positions.append(base_positions[atom.name])
                prev_c1_pos = base_positions['C1']
                prev_o5_pos = base_positions['O5']
            else:
                base_positions = self.generate_residue_positions(residue.name, flip_nitro)
                rotation_axis = Vec3(
                    prev_o5_pos.y - prev_c1_pos.y,
                    prev_c1_pos.x - prev_o5_pos.x,
                    0.0
                )
                angle = self.GLYCOSIDIC_ANGLE if i % 2 == 1 else -self.GLYCOSIDIC_ANGLE
                rotated_positions = self.rotate_around_axis(base_positions, rotation_axis, angle)
                o4_current_pos = rotated_positions['O4']
                c1_prev_to_o4 = (prev_c1_pos - o4_current_pos).normalize()
                glycosidic_distance = self.BOND_LENGTHS['C1-O4']
                translation_vector = prev_c1_pos + c1_prev_to_o4 * glycosidic_distance - o4_current_pos
                final_positions = self.translate_positions(rotated_positions, translation_vector)
                for atom in residue.atoms():
                    pos = final_positions[atom.name]
                    adjusted_pos = Vec3(pos.x, pos.y, pos.z + z_offset * i)
                    positions.append(adjusted_pos)
                prev_c1_pos = final_positions['C1'] + Vec3(0, 0, z_offset * i)
                prev_o5_pos = final_positions['O5'] + Vec3(0, 0, z_offset * i)
        return topology, positions