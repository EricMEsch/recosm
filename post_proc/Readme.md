# Post-Processing

This contains all of the post-processing required to get all of the event-level information i deemed necessary.
The notebook `post_proc.ipynb` does this processing for two example runs (the data is expected to be under `/data` but is obviously not here as i can not upload gigabytes of data on github).
Run008 would consist of a `ge77_muons` run according to the simulation here and Run007 is a `all_muons` run according to the simulation in this repository.

The input is expected to be under `data/run008` for example and in this file we expect `out_t{i}.hdf5` or `out_t{i}.lh5` files. This is because the remage-python-post-processing which does file merging is skipped. The number of expected threads can be specified as argument, default is 16.

The final product of the post-processing is a vector of a simple dataclass I called `Event`. It will also be written to a `.csv` file and can easily be checked in excel. This means all of the gigabytes of data is reduced to a few numbers per event.

## The python files

The different python files contains the real post-processing code.
- `read_and_write.py` obviously contains I/O functions that handle reading only data we are interested in and also merging all of the different threads into one awkward array.
- `processing.py` does the processing, duh
- `weights.py` contains probably the most inefficient way to apply an optical map.

## Requirements

- First this requires you to generate the actual data with the two simulations within this repository.
- Second you need the actual 1-dimensional optical map data from Michele. Because this is an offical repository i did not add it. The optical map data is expected in a certain `.json` format under `1d_map/` (ask me and i can send the folder)