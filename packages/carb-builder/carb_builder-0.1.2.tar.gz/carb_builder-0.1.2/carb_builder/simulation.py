"""
Defines methods for setting up and running OpenMM simulations.
"""

from openmm.app import *
from openmm import *
from openmm.unit import *
from geometry import Vec3 
from openmm import Vec3 as OpenMMVec3 

class SimulationManager: 
    """Manages OpenMM simulations for carbohydrate structures."""

    def __init__(self, topology, positions, forcefield_files=None, solvent_padding=1.2, output_dir="./output"):
        """
        Initializes the SimulationManager.

        Args:
            topology (openmm.Topology): The topology of the system.
            positions (list of Vec3): The atomic positions.
            forcefield_files (list of str): List of force field XML files.
            solvent_padding (float): Padding around the solute for solvation (nm).
            output_dir (str): Directory to save output files.
        """
        self.topology = topology
        self.positions = positions
        self.forcefield_files = forcefield_files
        self.solvent_padding = solvent_padding
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def prepare_system(self, solvate=False, forcefield_files=None):
        """Prepare a simulation system from topology and positions"""
        # Use OpenMMVec3 to get proper Quantity objects
        omm_positions = [OpenMMVec3(pos.x, pos.y, pos.z) for pos in self.positions]
        forcefield = ForceField(*self.forcefield_files)
        modeller = Modeller(self.topology, omm_positions)
    
        # Calculate box dimensions
        min_x = min(pos.x for pos in self.positions)
        max_x = max(pos.x for pos in self.positions)
        min_y = min(pos.y for pos in self.positions)
        max_y = max(pos.y for pos in self.positions)
        min_z = min(pos.z for pos in self.positions)
        max_z = max(pos.z for pos in self.positions)
        
        # Create box vectors in reduced form
        box_size_x = (max_x - min_x + 2 * self.solvent_padding) * nanometers
        box_size_y = (max_y - min_y + 2 * self.solvent_padding) * nanometers
        box_size_z = (max_z - min_z + 2 * self.solvent_padding) * nanometers
        
        # Create properly aligned periodic box vectors with pure float components
        a = OpenMMVec3(float(box_size_x.value_in_unit(nanometers)), 0.0, 0.0)*nanometers
        b = OpenMMVec3(0.0, float(box_size_y.value_in_unit(nanometers)), 0.0)*nanometers
        c = OpenMMVec3(0.0, 0.0, float(box_size_z.value_in_unit(nanometers)))*nanometers

        # Set periodic box vectors
        modeller.topology.setPeriodicBoxVectors((a, b, c))
        topology = modeller.getTopology()
        if topology.getPeriodicBoxVectors() is not None:
            box_vectors = [v.value_in_unit(openmm.unit.nanometers) for v in topology.getPeriodicBoxVectors()]
            topology.setPeriodicBoxVectors(box_vectors)

        if solvate is True:
            modeller.addSolvent(forcefield)
        system = forcefield.createSystem(modeller.getTopology(), 
                                         nonbondedMethod=PME, 
                                         nonbondedCutoff=1.0*nanometers, 
                                         constraints=HBonds)
        # Add custom external force
        force = CustomExternalForce("k*((x-x0)^2+(y-y0)^2+(z-z0)^2)")
        force.addGlobalParameter("k", 5.0)  # kJ/mol/nm^2
        force.addPerParticleParameter("x0")
        force.addPerParticleParameter("y0")
        force.addPerParticleParameter("z0")
        for i, pos in enumerate(modeller.getPositions()):
            force.addParticle(i, [pos.value_in_unit(nanometers)[0], 
                                  pos.value_in_unit(nanometers)[1], 
                                  pos.value_in_unit(nanometers)[2]])
        system.addForce(force)
        return modeller, system
    
    def minimize_energy(self, simulation, max_iterations=50000):
        """Minimizes the potential energy of the system."""
        print("Performing energy minimization...")
        simulation.minimizeEnergy(maxIterations=max_iterations)
        state = simulation.context.getState(getPositions=True, getEnergy=True)
        energy = state.getPotentialEnergy()
        print(f"Potential energy after minimization: {energy}")
        return state.getPositions()

    def equilibrate(self, simulation, steps=50000, report_interval=1000):
        """Equilibrates the system."""
        print("Performing equilibration...")
        simulation.reporters.append(StateDataReporter(
            os.path.join(self.output_dir, "equilibration.log"), report_interval,
            step=True, time=True, potentialEnergy=True, temperature=True))
        simulation.reporters.append(PDBReporter(
            os.path.join(self.output_dir, "equilibration.pdb"), report_interval))
        simulation.step(steps)
        return simulation.context.getState(getPositions=True).getPositions()

    def run_simulation(self, system, modeller, output_prefix="simulation", minimize=True, equilibrate=True):
        """Runs the simulation."""
        integrator = LangevinMiddleIntegrator(300 * kelvin, 1 / picosecond, 0.001 * picoseconds)
        simulation = Simulation(modeller.getTopology(), system, integrator)
        
        # Convert positions to OpenMM-compatible format if needed
        positions = modeller.getPositions()
        if not isinstance(positions, Quantity):
            positions = positions * nanometer
            
        simulation.context.setPositions(positions)

        if minimize:
            minimized_positions = self.minimize_energy(simulation)
            with open(os.path.join(self.output_dir, f"{output_prefix}_minimized.pdb"), 'w') as f:
                PDBFile.writeFile(modeller.getTopology(), minimized_positions, f)

        if equilibrate:
            equilibrated_positions = self.equilibrate(simulation)
            with open(os.path.join(self.output_dir, f"{output_prefix}_equilibrated.pdb"), 'w') as f:
                PDBFile.writeFile(modeller.getTopology(), equilibrated_positions, f)

        return simulation