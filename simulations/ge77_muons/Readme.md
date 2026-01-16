# Ge77 producing muon simulation

This simulation is used to simulate a higher statistic of muons and only output events in which Ge77 was produced. This is the heart of the cosmogenic analysis.

## Requirements

There are things missing in this repository that you require to run this simulation.

- The musun input file expected under `musun/combined_file.dat` which should contain at least as many muon primaries as you want to simulate
- The geometry `.gdml` file. It should be placed in this folder and the name "new_baseline.gdml" is expected.
- A remage installation with v.0.19 or newer is recommended (older versions should work, I am not sure what is the oldest version until it breaks)

## Notes

This builds against remage directly. The installation is pretty simple once within the official remage container:
```bash
mkdir build
cd build
cmake .. -DCMAKE_PREFIX_PATH=/opt/remage
make
cd ..
python3 run_optical.py
```

- you might be noticing that this does not use a `water_cascades.txt` file. So do not run it using Geant4v11.3. Otherwise your water nCaptures will be horribly wrong.
- The output will be produced in the `/build` directory and an `/out` directory like in the all_muons simulation.