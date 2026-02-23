import json
import os
import numpy as np

# These functions can be improved a lot. First make them read in the files once
# Secondly this can probably be done in 1 or 2 functions instead of many similar ones.

MODERATOR_ACTUAL_R = 1650 # mm this is the inner radius
MODERATOR_ACTUAL_Z_TOP = 703 # mm this is the lower edge of the top Plate
MODERATOR_ACTUAL_Z_BOT = -2297 # mm this is the upper edge of the bottom Plate
THICKNESS_ACTUAL_TOP = 100 # mm
THICKNESS_ACTUAL_BOT = 100 # mm
THICKNESS_R = 100 # mm

MODERATOR_MAP_R = 1720 # mm
MODERATOR_MAP_Z_TOP = 920 # mm this is the lower edge of the top Plate
MODERATOR_MAP_Z_BOT = -2080 # mm this is the upper edge of the bottom Plate

SHIFT_Z = MODERATOR_MAP_Z_TOP - MODERATOR_ACTUAL_Z_TOP # We shift us into the map coordinates. So our data + shift = map coords
SHIFT_R = MODERATOR_MAP_R - MODERATOR_ACTUAL_R

def get_weighted_energy(radius: float, z: float) -> tuple[float, float]:
    """Get the weighted energy deposition for a given radius, z-coordinate, and xenon flag.
       Expects the radius and z in mm.
       """

    # We compare against our position, so no shift is needed here. The shift is only for the map lookup.
    if z > (MODERATOR_ACTUAL_Z_TOP) or radius > (MODERATOR_ACTUAL_R) or z < (MODERATOR_ACTUAL_Z_BOT):
        # outside zones
        if radius <= (MODERATOR_ACTUAL_R + THICKNESS_R):
            # Use the outside_close zone in z-direction
            return weight_edep_close_outside_z(z)
        else:
            # use the different outside r zones
            if z > (MODERATOR_ACTUAL_Z_TOP + THICKNESS_ACTUAL_TOP + 30):
                # This is completly top zone
                return weight_edep_top_outside_r(radius)
            elif z > (MODERATOR_ACTUAL_Z_TOP - 100):
                # This is a 120 mm + plate thick zone around the top plate
                return weight_edep_top_inside_r(radius)
            elif z > (MODERATOR_ACTUAL_Z_BOT + 100):
                # This is the middle zone
                return weight_edep_middle_r(radius)
            elif z > (MODERATOR_ACTUAL_Z_BOT - THICKNESS_ACTUAL_BOT - 30):
                # This is a 120 mm + plate thick zone around the bottom plate
                return weight_edep_bot_inside_r(radius)
            else:
                # This is the far bottom zone
                return weight_edep_bot_outside_r(radius)
    else:
        # inside zones
        if (z >= ((radius - MODERATOR_ACTUAL_R) + MODERATOR_ACTUAL_Z_TOP)) or (z <= ((MODERATOR_ACTUAL_R - radius) + MODERATOR_ACTUAL_Z_BOT)):
            # use the inside z-direction zones
            if (MODERATOR_ACTUAL_R - radius) < 200:
                # In the first 200 mm use the close z zone
                return weight_edep_close_inside_z(z)
            elif (MODERATOR_ACTUAL_R - radius) < 500:
                # In the next 300 mm use the middle z zone
                return weight_edep_middle_inside_z(z)
            else:
                # For everything farther inside use the far inside z zone
                return weight_edep_far_inside_z(z)
        else: 
            # use the r-zones
            if z > (MODERATOR_ACTUAL_Z_TOP - 250):
                # Use top zone for first 250 mm
                return weight_edep_top_inside_r(radius)
            elif z > (MODERATOR_ACTUAL_Z_BOT + 250):
                # Use bottom zone for last 250 mm
                return weight_edep_middle_r(radius)
            else:
                return weight_edep_bot_inside_r(radius)


def weight_edep_top_outside_r(radius: float) -> tuple[float, float]:
    if radius < MODERATOR_ACTUAL_R:
        raise ValueError(f"Radius must be >= {MODERATOR_ACTUAL_R} mm for top_outside_r zone.")

    path_normal = "./1d_map/top_outside_r.json"
    path_xenon = "./1d_map/top_outside_r_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    R = data_normal["R"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    R_xenon = data_xenon["R"]
    prob_xenon = data_xenon["prob"]

    adjusted_radius  = (radius + SHIFT_R) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_radius, R, prob),
        np.interp(adjusted_radius, R_xenon, prob_xenon),
    )

def weight_edep_top_inside_r(radius: float) -> tuple[float, float]:

    path_normal = "./1d_map/top_inside_r.json"
    path_xenon = "./1d_map/top_inside_r_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    R = data_normal["R"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    R_xenon = data_xenon["R"]
    prob_xenon = data_xenon["prob"]

    adjusted_radius  = (radius + SHIFT_R) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_radius, R, prob),
        np.interp(adjusted_radius, R_xenon, prob_xenon),
    )

def weight_edep_middle_r(radius: float) -> tuple[float, float]:

    path_normal = "./1d_map/middle_r.json"
    path_xenon = "./1d_map/middle_r_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    R = data_normal["R"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    R_xenon = data_xenon["R"]
    prob_xenon = data_xenon["prob"]

    adjusted_radius  = (radius + SHIFT_R) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_radius, R, prob),
        np.interp(adjusted_radius, R_xenon, prob_xenon),
    )

def weight_edep_bot_inside_r(radius: float) -> tuple[float, float]:

    path_normal = "./1d_map/bottom_inside_r.json"
    path_xenon = "./1d_map/bottom_inside_r_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    R = data_normal["R"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    R_xenon = data_xenon["R"]
    prob_xenon = data_xenon["prob"]

    adjusted_radius  = (radius + SHIFT_R) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_radius, R, prob),
        np.interp(adjusted_radius, R_xenon, prob_xenon),
    )

def weight_edep_bot_outside_r(radius: float) -> tuple[float, float]:

    if radius < MODERATOR_ACTUAL_R:
        raise ValueError(f"Radius must be >= {MODERATOR_ACTUAL_R} mm for bottom_outside_r zone.")

    path_normal = "./1d_map/bottom_outside_r.json"
    path_xenon = "./1d_map/bottom_outside_r_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    R = data_normal["R"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    R_xenon = data_xenon["R"]
    prob_xenon = data_xenon["prob"]

    adjusted_radius  = (radius + SHIFT_R) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_radius, R, prob),
        np.interp(adjusted_radius, R_xenon, prob_xenon),
    )

def weight_edep_close_outside_z(z: float) -> tuple[float, float]:

    if not (z >= MODERATOR_ACTUAL_Z_TOP or z <= -MODERATOR_ACTUAL_Z_BOT):
        raise ValueError(f"Z must be >= {MODERATOR_ACTUAL_Z_TOP} mm or <= -{MODERATOR_ACTUAL_Z_BOT} mm for close_outside_z zone.")

    path_normal = "./1d_map/close_outside_z.json"
    path_xenon = "./1d_map/close_outside_z_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    z_values = data_normal["z"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    z_values_xenon = data_xenon["z"]
    prob_xenon = data_xenon["prob"]

    adjusted_z  = (z + SHIFT_Z) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_z, z_values, prob),
        np.interp(adjusted_z, z_values_xenon, prob_xenon),
    )

def weight_edep_close_inside_z(z: float) -> tuple[float, float]:

    if not (MODERATOR_ACTUAL_Z_BOT < z < MODERATOR_ACTUAL_Z_TOP):
        raise ValueError(f"Z must be < {MODERATOR_ACTUAL_Z_TOP} mm or > -{MODERATOR_ACTUAL_Z_BOT} mm for close_inside_z zone.")

    path_normal = "./1d_map/close_inside_z.json"
    path_xenon = "./1d_map/close_inside_z_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    z_values = data_normal["z"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    z_values_xenon = data_xenon["z"]
    prob_xenon = data_xenon["prob"]

    adjusted_z  = (z + SHIFT_Z) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_z, z_values, prob),
        np.interp(adjusted_z, z_values_xenon, prob_xenon),
    )

def weight_edep_middle_inside_z(z: float) -> tuple[float, float]:

    if not (MODERATOR_ACTUAL_Z_BOT < z < MODERATOR_ACTUAL_Z_TOP):
        raise ValueError(f"Z must be < {MODERATOR_ACTUAL_Z_TOP} mm or > {MODERATOR_ACTUAL_Z_BOT} mm for middle_inside_z zone.")

    path_normal = "./1d_map/middle_inside_z.json"
    path_xenon = "./1d_map/middle_inside_z_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    z_values = data_normal["z"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    z_values_xenon = data_xenon["z"]
    prob_xenon = data_xenon["prob"]

    adjusted_z  = (z + SHIFT_Z) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_z, z_values, prob),
        np.interp(adjusted_z, z_values_xenon, prob_xenon),
    )

def weight_edep_far_inside_z(z: float) -> tuple[float, float]:

    if not (MODERATOR_ACTUAL_Z_BOT < z < MODERATOR_ACTUAL_Z_TOP):
        raise ValueError(f"Z must be < {MODERATOR_ACTUAL_Z_TOP} mm or > {MODERATOR_ACTUAL_Z_BOT} mm for far_inside_z zone. Z is {z} mm.")

    path_normal = "./1d_map/far_inside_z.json"
    path_xenon = "./1d_map/far_inside_z_xenon.json"

    # Check existence
    if not os.path.exists(path_normal):
        raise FileNotFoundError(f"Required optical map file not found: {path_normal}")
    if not os.path.exists(path_xenon):
        raise FileNotFoundError(f"Required optical map file not found: {path_xenon}")

    # Load normal
    with open(path_normal, "r") as f:
        data_normal = json.load(f)

    z_values = data_normal["z"]
    prob = data_normal["prob"]

    # Load xenon
    with open(path_xenon, "r") as f:
        data_xenon = json.load(f)

    z_values_xenon = data_xenon["z"]
    prob_xenon = data_xenon["prob"]

    adjusted_z  = (z + SHIFT_Z) / 10 # convert mm to cm for map lookup and shift to map coords
    
    return (
        np.interp(adjusted_z, z_values, prob),
        np.interp(adjusted_z, z_values_xenon, prob_xenon),
    )