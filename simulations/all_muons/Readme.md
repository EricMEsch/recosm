# All muons simulation

This simulation is used to simulate an output consisting of all muons crossing the experiment. No filter on certain isotope production is applied. This is relevant to calculate false triggers and deadtime for the cosmogenic veto systems.

## Requirements

There are things missing in this repository that you require to run this simulation.

- The musun input file expected under `musun/combined_file.dat` which should contain at least as many muon primaries as you want to simulate
- The geometry `.gdml` file. It should be placed in this folder and the name "new_baseline.gdml" is expected.
- A remage installation with v.0.19 or newer is recommended (older versions should work, I am not sure what is the oldest version until it breaks)

## Notes

- This uses the remage-cpp file directly and skips the remage python-post-processing. This ensures that the data of this simulation has the same shape as the data of the Ge77 only simulation, which uses a custom c++ extension.
- You can see the `water_cascades.txt` file used. This replaces Geant4s water neutron capture deexcitation with the correct line. This is due to a bug in Geant4v.11.3 and should be fixed (and therefore not necessary anymore) in Geant4v.11.4. But i will leave it here until we verified the fix.