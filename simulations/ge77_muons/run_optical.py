import subprocess
from pathlib import Path

macro_file = Path("optical.mac")
macro_content = """\
/RMG/Manager/Logging/LogLevel summary

/RMG/Processes/HadronicPhysics Shielding
/RMG/Processes/OpticalPhysics true

/RMG/Output/ActivateOutputScheme CustomStackingFilter

/RMG/Geometry/RegisterDetectorsFromGDML Germanium
/RMG/Geometry/RegisterDetectorsFromGDML Optical
/RMG/Geometry/RegisterDetector Scintillator atmosphericlar 12000

/RMG/Output/ActivateOutputScheme Track

/RMG/Processes/DefaultProductionCut 1 mm
/RMG/Processes/SensitiveProductionCut 1 mm

/run/initialize

/RMG/Output/IsotopeFilter/AddIsotope 77 32
/RMG/Output/IsotopeFilter/DiscardPhotonsIfIsotopeNotProduced true
/RMG/Output/NtuplePerDetector false

/RMG/Output/Track/AddProcessFilter nCapture

/RMG/Processes/Stepping/DaughterNucleusMaxLifetime 1 hour

/RMG/Generator/Confine UnConfined

/RMG/Generator/Select MUSUNCosmicMuons
/RMG/Generator/MUSUNCosmicMuons/MUSUNFile musun/combined_file.dat

/run/beamOn 1000000
"""

macro_file.write_text(macro_content)

try:
    # Run Geant4 simulation
    result = subprocess.run(
        [
            "./build/FullCosmogenics",
            "-m", str(macro_file),
            "-g", "new_baseline.gdml",
            "-o", "build/out.hdf5",
            "-t", "16"
        ],
        check=True,          # Raises CalledProcessError if nonzero exit
        capture_output=False # Ensures live forwarding to terminal
    )
except subprocess.CalledProcessError as e:
    print(f"❌ Simulation failed with exit code {e.returncode}")
    # Optionally, you can also print stderr if you used capture_output=True
#finally:
    # Cleanup: delete macro file
    #if macro_file.exists():
    #    macro_file.unlink()

