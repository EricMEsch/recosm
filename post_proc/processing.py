
import pandas as pd
from dataclasses import dataclass
import numpy as np
import awkward as ak
from reboost.spms.pe import emitted_scintillation_photons

from weights import get_weighted_energy

@dataclass
class Event:
    event_id: int # unique identifier for the event
    il_first_us: float # integral light within the first microsecond
    il_1_10_us: float # integral light between 1 and 10 microseconds
    il_10_200_us: float # integral light between 10 and 200 microseconds
    ge77_count: int # count of Ge-77 produced in the event
    n_200ns_intervals_1_10_us: int # number of non-overlapping 200ns intervals with > 6 PE between 1 and 10 microseconds
    n_200ns_intervals_10_200_us: int # number of non-overlapping 200ns intervals with > 6 PE between 10 and 200 microseconds
    n_neutrons_in_ws: int # boolean indicating if more than 7 neutrons were captured in the water + steel
    max_10us_n_photons: float # maximum number of emitted scintillation photons in the maximum 10 microsecond window
    max_10us_n_photons_xenon: float # maximum number of emitted scintillation photons in the maximum 10 microsecond window with xenon_weights
    timestamp_brightest_60ns_window_1us: float # timestamp of the brightest 60ns window within the first microsecond
    mean_timestamp_intervals_1_10_us: float # mean timestamp of the non-overlapping 200ns intervals with > 6 PE between 1 and 10 microseconds
    mean_timestamp_intervals_10_200_us: float # mean timestamp of the non-overlapping 200ns intervals with > 6 PE between 10 and 200 microseconds
    std_timestamp_intervals_1_10_us: float # standard deviation of the timestamps of the non-overlapping 200ns intervals with > 6 PE between 1 and 10 microseconds
    std_timestamp_intervals_10_200_us: float # standard deviation of the timestamps of the non-overlapping 200ns intervals with > 6 PE between 10 and 200 microseconds
    max_10us_weighted_energy: float # weighted energy deposition in the ALAR region maximum value in a 10 microsecond window
    max_10us_weighted_energy_xenon: float # weighted energy deposition in the ALAR region maximum value in a 10 microsecond window with xenon_weights


import pandas as pd
import numpy as np
import awkward as ak

def compute_optical_features(optical_data):
    # --- Convert to DataFrame ---
    df = pd.DataFrame({
        "event_id": ak.to_numpy(optical_data.evtid),
        "time": ak.to_numpy(optical_data.time),
        "det_uid": ak.to_numpy(optical_data.det_uid),
    })
    g = df.groupby("event_id")

    # --- Basic time window hit counts ---
    n_first_us = g["time"].apply(lambda x: np.sum(x < 1e3)).reset_index(name="il_first_us")
    n_1_10_us = g["time"].apply(lambda x: np.sum((x >= 1e3) & (x < 10e3))).reset_index(name="il_1_10_us")
    n_10_200_us = g["time"].apply(lambda x: np.sum((x >= 10e3) & (x < 200e3))).reset_index(name="il_10_200_us")

    # --- Brightest 60 ns window within first 1 µs ---
    def brightest_60ns(sub):
        sub = sub[sub.time < 1e3].sort_values("time")
        times = sub["time"].values
        if len(times) == 0:
            return np.nan
        max_count = 0
        best_time = np.nan
        j = 0
        for i in range(len(times)):
            while j < len(times) and times[j] - times[i] <= 60:
                j += 1
            count = j - i
            if count > max_count:
                max_count = count
                best_time = times[i]
        return best_time

    timestamp_brightest = g.apply(brightest_60ns, include_groups=False).reset_index(name="timestamp_brightest_60ns_window_1us")

    # --- Helper for 200 ns interval stats ---
    def interval_stats(sub, tmin, tmax):
        sub = sub[(sub.time >= tmin) & (sub.time < tmax)]
        if sub.empty:
            return pd.Series([0, np.nan, np.nan])
        times = sub["time"].values
        bins = np.arange(tmin, tmax + 200, 200)
        # Assign each event to a bin
        bin_idx = np.digitize(sub.time.values, bins) - 1  # -1 because digitize is 1-based
        sub = sub.assign(bin=bin_idx)

        # Count unique detectors per bin
        det_counts = sub.groupby("bin")["det_uid"].nunique()
    
        # Select bins with >6 unique detectors
        good_bins = det_counts[det_counts >= 6].index
        if len(good_bins) == 0:
            return pd.Series([0, np.nan, np.nan])

        mids = bins[good_bins] + 100
        return pd.Series([len(mids), np.mean(mids), np.std(mids)])

    # Apply and name columns
    interval_1_10 = (
        g.apply(lambda x: interval_stats(x, 1e3, 10e3), include_groups=False)
        .reset_index()
        .rename(columns={
            0: "n_200ns_intervals_1_10_us",
            1: "mean_timestamp_intervals_1_10_us",
            2: "std_timestamp_intervals_1_10_us"
        })
    )

    interval_10_200 = (
        g.apply(lambda x: interval_stats(x, 10e3, 200e3), include_groups=False)
        .reset_index()
        .rename(columns={
            0: "n_200ns_intervals_10_200_us",
            1: "mean_timestamp_intervals_10_200_us",
            2: "std_timestamp_intervals_10_200_us"
        })
    )

    # --- Merge all results on event_id ---
    result = (
        n_first_us
        .merge(n_1_10_us, on="event_id")
        .merge(n_10_200_us, on="event_id")
        .merge(timestamp_brightest, on="event_id")
        .merge(interval_1_10, on="event_id")
        .merge(interval_10_200, on="event_id")
    )

    return result


def is_element(pid, Z):
    return (pid // 10_000) == (100000 + Z) # Returns true if the Z of the given pdg code is correct

def compute_scintillator_features(scintillator_data, window_us=10):
    window_ns = window_us * 1e3  # convert µs → ns

    # Convert awkward arrays → flat arrays
    evtid = ak.to_numpy(scintillator_data.evtid)
    particle_id = ak.to_numpy(scintillator_data.particle)
    x = ak.to_numpy(scintillator_data.xloc) * 1000  # mm
    y = ak.to_numpy(scintillator_data.yloc) * 1000
    z = ak.to_numpy(scintillator_data.zloc) * 1000
    edep = ak.to_numpy(scintillator_data.edep)
    time = ak.to_numpy(scintillator_data.time)  # ns

    # Build DataFrame
    df = pd.DataFrame({
        "evtid": evtid,
        "particle_id": particle_id,
        "x": x,
        "y": y,
        "z": z,
        "edep": edep,
        "time": time,
    })

    # Compute radius and weight
    df["radius"] = np.sqrt(df["x"]**2 + df["y"]**2)
    w0, w1 = np.vectorize(get_weighted_energy)(
        df["radius"].values,
        df["z"].values,
    )

    df["weight"] = w0 / 100.0 # convert percentage to fraction
    df["weight_xenon"] = w1 / 100.0 # convert percentage to fraction
    df["weighted_edep"] = df["edep"] * df["weight"]
    df["weighted_edep_xenon"] = df["edep"] * df["weight_xenon"]

    # --- Group once ---
    grouped = list(df.groupby("evtid", sort=False))
    evt_ids = [evtid for evtid, _ in grouped]
    weighted_edep_by_event = [sub["weighted_edep"].values for _, sub in grouped]
    weighted_edep_xenon_by_event = [sub["weighted_edep_xenon"].values for _, sub in grouped]
    particle_id_by_event = [sub["particle_id"].values for _, sub in grouped]
    time_by_event = [sub["time"].values for _, sub in grouped]

    # --- Compute photons once, event-wise ---
    n_photons_by_event = emitted_scintillation_photons(weighted_edep_by_event,
                                                       particle_id_by_event,
                                                       "lar")
    n_photons_xenon_by_event = emitted_scintillation_photons(weighted_edep_xenon_by_event,
                                                             particle_id_by_event,
                                                             "lar")

    # --- Now process events in one loop ---
    results = []
    for evtid, e, e_xenon, t, n_photons, n_photons_xenon in zip(evt_ids, weighted_edep_by_event, weighted_edep_xenon_by_event, time_by_event, n_photons_by_event, n_photons_xenon_by_event):
        # Sort by time
        order = np.argsort(t)
        t = t[order]
        e = e[order]
        e_xenon = e_xenon[order]
        n_photons = np.asarray(n_photons)[order]
        n_photons_xenon = np.asarray(n_photons_xenon)[order]

        # Sliding window
        max_sum = 0.0
        max_sum_xenon = 0.0
        max_n_photons = 0
        max_n_photons_xenon = 0
        n = len(t)
        start = 0
        current_sum = 0.0
        current_sum_xenon = 0.0
        current_n_photons = 0
        current_n_photons_xenon = 0

        for end in range(n):
            current_sum += e[end]
            current_sum_xenon += e_xenon[end]
            current_n_photons += n_photons[end]
            current_n_photons_xenon += n_photons_xenon[end]
            while t[end] - t[start] > window_ns:
                current_sum -= e[start]
                current_sum_xenon -= e_xenon[start]
                current_n_photons -= n_photons[start]
                current_n_photons_xenon -= n_photons_xenon[start]
                start += 1
            if current_sum > max_sum:
                max_sum = current_sum
                max_n_photons = current_n_photons
            if current_sum_xenon > max_sum_xenon:
                max_sum_xenon = current_sum_xenon
                max_n_photons_xenon = current_n_photons_xenon

        # According to CDR, this is the chance a photon hitting the PMMA being detected
        sipm_det_efficiency = 1.2e-3
        results.append((evtid, max_sum, max_sum_xenon, max_n_photons * sipm_det_efficiency, max_n_photons_xenon * sipm_det_efficiency))


    return pd.DataFrame(results, columns=["event_id", "max_10us_weighted_energy", "max_10us_weighted_energy_xenon", "max_10us_n_photons", "max_10us_n_photons_xenon"])

def compute_track_features(tracks_data):
    evtid = ak.to_numpy(tracks_data.evtid)
    particle_id = ak.to_numpy(tracks_data.particle)
    x = ak.to_numpy(tracks_data.xloc) * 1000  # mm
    y = ak.to_numpy(tracks_data.yloc) * 1000
    z = ak.to_numpy(tracks_data.zloc) * 1000

    # These values are only to identify captures on the neutron moderator and very deep inside the cryo
    # This is not an exact boundary check to identify captures within the cryo.
    cryo_inner_radius = 3200 # mm
    z_lower_straight_part = -2280 # mm
    z_upper_straight_part = 1720 # mm

    #
    water_tank_radius = 6000 # mm

    ge77_Z = 32
    ge77_A = 77
    ge77_target_id = 100000000 + ge77_Z*1000 + ge77_A

    # Define all the z-values to be counted in the water neutron capture count
    def is_capture_nucleus(pid):
        return (is_element(pid, 1) | is_element(pid, 24) | is_element(pid, 25) | is_element(pid, 26) |
                is_element(pid, 27) | is_element(pid, 28) | is_element(pid, 42))

    df = pd.DataFrame({
        "event_id": evtid,
        "particle_id": particle_id,
        "x": x,
        "y": y,
        "z": z,
    })

    df["radius"] = np.sqrt(df["x"]**2 + df["y"]**2)
    grouped = df.groupby("event_id")

    def check_ge77_and_neutrons(sub):
        ge77_count = np.sum((sub["particle_id"] // 10) == ge77_target_id)

        n_neutrons = np.sum(sub["particle_id"].apply(is_capture_nucleus) &
                            ((sub["radius"] > cryo_inner_radius) |
                             (sub["z"] < z_lower_straight_part) |
                             (sub["z"] > z_upper_straight_part))
                             & (sub["radius"] <= water_tank_radius))
        
        return pd.Series([ge77_count, n_neutrons])
    result = (
        grouped.apply(check_ge77_and_neutrons, include_groups=False)
        .reset_index()
        .rename(columns={0: "ge77_count", 1: "n_neutrons_in_ws"})
    )

    return result

def convert_to_event_structure(scintillator_data, optical_data, germanium_data=None, tracks_data=None):
    df_optical = compute_optical_features(optical_data)
    #df_germanium = compute_germanium_features(germanium_data)
    df_scint = compute_scintillator_features(scintillator_data)
    
    # Start with optical and scintillator data
    merged = (
        df_optical
        #.merge(df_germanium, on="event_id", how="outer")
        .merge(df_scint, on="event_id", how="outer")
    )
    
    # Add tracks data if available
    if tracks_data is not None:
        df_tracks = compute_track_features(tracks_data)
        merged = merged.merge(df_tracks, on="event_id", how="outer")
    else:
        # explicitly create the missing columns
        merged["ge77_count"] = np.nan
        merged["n_neutrons_in_ws"] = np.nan
    
    # Fill NaN values with defaults
    merged = merged.fillna({
        "il_first_us": np.nan,
        "il_1_10_us": np.nan,
        "il_10_200_us": np.nan,
        "n_200ns_intervals_1_10_us": np.nan,
        "n_200ns_intervals_10_200_us": np.nan,
        "max_10us_n_photons": np.nan,
        "max_10us_n_photons_xenon": np.nan,
        "timestamp_brightest_60ns_window_1us": np.nan,
        "mean_timestamp_intervals_1_10_us": np.nan,
        "mean_timestamp_intervals_10_200_us": np.nan,
        "std_timestamp_intervals_1_10_us": np.nan,
        "std_timestamp_intervals_10_200_us": np.nan,
        "max_10us_weighted_energy": np.nan,
        "max_10us_weighted_energy_xenon": np.nan,
        "ge77_count": np.nan,
        "n_neutrons_in_ws": np.nan,
    })

    # Convert to dataclass list
    events = [Event(**row) for row in merged.to_dict(orient="records")]
    return events
