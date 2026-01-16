from lgdo import lh5
import awkward as ak
import csv
from dataclasses import asdict
import os
import h5py
import numpy as np

def strip_unit(field_name):
    """Strip unit suffix of the form *_in_<unit>"""
    if "_in_" in field_name:
        return field_name.split("_in_")[0]
    return field_name


def read_lgdo_hdf5_table(file_path, table_path):
    """Read an LGDO table from HDF5 file and return as awkward array"""
    with h5py.File(file_path, 'r') as f:
        if table_path not in f:
            print(f"Warning. Table path {table_path} not found in file {file_path}.")
            return None
        
        table_group = f[table_path]
        data_dict = {}
        
        for field_name in table_group.keys():
            field_group = table_group[field_name]
            
            # Skip metadata fields
            if field_name in ['entries', 'columns', 'forms', 'names']:
                continue
            
            # Strip unit suffix if present
            clean_name = strip_unit(field_name)
            
            if isinstance(field_group, h5py.Group) and 'pages' in field_group:
                pages = field_group['pages'][:]
                
                # Handle object dtype (strings/bytes) by converting to string
                if pages.dtype == object or pages.dtype.kind in ('O', 'S', 'U'):
                    # Convert bytes to strings
                    if len(pages) > 0 and isinstance(pages[0], bytes):
                        pages = np.array([p.decode('utf-8') if isinstance(p, bytes) else str(p) for p in pages])
                    else:
                        pages = pages.astype(str)
                data_dict[clean_name] = pages
            
            elif isinstance(field_group, h5py.Dataset):
                # Direct dataset
                data = field_group[:]
                if data.dtype == object or data.dtype.kind in ('O', 'S', 'U'):
                    if len(data) > 0 and isinstance(data[0], bytes):
                        data = np.array([d.decode('utf-8') if isinstance(d, bytes) else str(d) for d in data])
                    else:
                        data = data.astype(str)
                data_dict[clean_name] = data
        
        if not data_dict:
            print(f"Warning. No data found at table path {table_path} in file {file_path}.")
            return None
        
        return ak.zip(data_dict)


def read_data(output_directory, file_extension = "lh5", nr_of_threads = 16):
    """
    Takes the path of where the files should be.

    nr_of_threads: number of threads used for the sim. Expects files according to "out_t{i}.lh5"

    Returns:
    The stp/scintillator data, the stp/optical data concatenated for all files, 
    the stp/germanium data concatenated for all files, and the tracks data concatenated for all files.
    """

    all_data = []  # list to collect the filtered arrays
    time_min = 10.0 * 1e3  # 10 microseconds
    time_max = 1.0 * 1e6  # 1 millisecond
    
    for i in range(nr_of_threads):
        file_path = f"{output_directory}/out_t{i}.{file_extension}"

        # read file
        if file_extension == "hdf5":
            data = read_lgdo_hdf5_table(file_path, "stp/scintillator")
        else:
            data = lh5.read_as("stp/scintillator", file_path, "ak")

        # apply time cut
        if data is not None:
            mask = (data.time >= time_min) & (data.time <= time_max)
            filtered_data = data[mask]

            # collect
            all_data.append(filtered_data)
        else:
            print(f"No scintillator data found in file {file_path}.")
    concatenated_scint_data = ak.concatenate(all_data)

    all_data.clear()

    for i in range(nr_of_threads):
        file_path = f"{output_directory}/out_t{i}.{file_extension}"

        # read file
        if file_extension == "hdf5":
            data = read_lgdo_hdf5_table(file_path, "stp/optical")
        else:
            data = lh5.read_as("stp/optical", file_path, "ak")

        # collect
        if data is not None:
            all_data.append(data)
        else:
            print(f"No optical data found in file {file_path}.")

    concatenated_optical_data = ak.concatenate(all_data)

    all_data.clear()
    
    for i in range(nr_of_threads):
        file_path = f"{output_directory}/out_t{i}.{file_extension}"

        # read file
        if file_extension == "hdf5":
            data = read_lgdo_hdf5_table(file_path, "stp/germanium")
        else:
            data = lh5.read_as("stp/germanium", file_path, "ak")

        # collect
        if data is not None:
            all_data.append(data)
        else:
            print(f"No germanium data found in file {file_path}.")

    concatenated_germanium_data = ak.concatenate(all_data)

    all_data.clear()
    
    for i in range(nr_of_threads):
        file_path = f"{output_directory}/out_t{i}.{file_extension}"

        # read file
        try:
            if file_extension == "hdf5":
                data = read_lgdo_hdf5_table(file_path, "stp/tracks")
                processes = read_lgdo_hdf5_table(file_path, "stp/processes")
            else:
                data = lh5.read_as("tracks", file_path, "ak")
                processes = lh5.read_as("processes", file_path, "ak")

            allowed_processes = (processes.name == "nCapture") | (processes.name == "RMGnCapture")
            proc_id = processes.procid[allowed_processes]
            track_mask = data.procid == proc_id
            data = data[track_mask]
        except Exception as e:
            print(f"Error reading tracks from {file_path}: {e}")
            

        # collect
        if data is not None:
            all_data.append(data)
        else:
            print(f"No tracks data found in file {file_path}.")

    concatenated_tracks_data = ak.concatenate(all_data)

    return concatenated_scint_data, concatenated_optical_data, concatenated_germanium_data, concatenated_tracks_data

def write_events_to_csv(events, filename):
    if not events:
        print("No events to write.")
        return
    
    # Use the dataclass fields as column names
    fieldnames = list(asdict(events[0]).keys())

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ev in events:
            writer.writerow(asdict(ev))