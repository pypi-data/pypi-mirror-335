"""
Example script demonstrating the use of the carbohydrate builder package.
"""

from builder import CarbohydrateBuilder
from simulation import SimulationManager
from openmm import unit

def main():
    """
    Main function to demonstrate carbohydrate building and simulation.
    """
    # Define the output directory
    output_dir = "./output"

    # Initialize the carbohydrate builder
    builder = CarbohydrateBuilder(output_dir=output_dir)

    # Define a sample residue sequence
    residue_sequence = ["0Yn", "4Yn", "4Yn", "rYn"]

    # Define simulation parameters
    num_chains = 3
    solvent_padding = 1.0  # nm
    forcefield_files = ['amber_final.xml', 'amber14-all.xml', 'amber14/tip3pfb.xml', 'amber14/GLYCAM_06j-1.xml']
    solvate = True
    minimize = True
    equilibrate = True

    try:
        # Build the carbohydrate structure
        topology, positions = builder.build_carbohydrate(residue_sequence, num_chains=num_chains)

        # Initialize the simulation manager
        simulation_manager = SimulationManager(topology, positions,
                                                forcefield_files=forcefield_files,
                                                solvent_padding=solvent_padding,
                                                output_dir=output_dir)

        # Prepare the system
        modeller, system = simulation_manager.prepare_system(solvate=solvate, forcefield_files=forcefield_files)

        # Run the simulation
        simulation = simulation_manager.run_simulation(system, modeller,
                                                        output_prefix="example_simulation",
                                                        minimize=minimize,
                                                        equilibrate=equilibrate)

        print("Carbohydrate building and simulation complete! Check the output directory for generated files.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure that all required force field files are available.")
        sys.exit(1)  # Exit with an error code

if __name__ == "__main__":
    main()