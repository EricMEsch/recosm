import json
import os
import numpy as np

# These functions can be improved a lot. First make them read in the files once
# Secondly this can probably be done in 1 or 2 functions instead of many similar ones.

MODERATOR_ACTUAL_R = 1720 # mm
MODERATOR_ACTUAL_Z_TOP = 200 # mm this is the lower edge of the top Plate
MODERATOR_ACTUAL_Z_BOT = -2800 # mm this is the upper edge of the bottom Plate

MODERATOR_MAP_R = 1720 # mm
MODERATOR_MAP_Z_TOP = 920 # mm this is the lower edge of the top Plate
MODERATOR_MAP_Z_BOT = -2080 # mm this is the upper edge of the bottom

SHIFT_Z = MODERATOR_MAP_Z_TOP - MODERATOR_ACTUAL_Z_TOP
SHIFT_R = MODERATOR_MAP_R - MODERATOR_ACTUAL_R

def get_weighted_energy(radius: float, z: float) -> tuple[float, float]:
    """Get the weighted energy deposition for a given radius, z-coordinate, and xenon flag.
       Expects the radius and z in mm.
       """
    if z > 300 or radius > 1820 or z < -2900:
        # outside zones
        if radius <= 1820:
            # Use the outside_close zone in z-direction
            return weight_edep_close_outside_z(z)
        else:
            # use the different outside r zones
            if z > 400:
                return weight_edep_top_outside_r(radius)
            elif z > 0:
                return weight_edep_top_inside_r(radius)
            elif z > -2600:
                return weight_edep_middle_r(radius)
            elif z > -3000:
                return weight_edep_bot_inside_r(radius)
            else:
                return weight_edep_bot_outside_r(radius)
    else:
        # inside zones
        if (z >= ((radius - 1720) + 200)) or (z <= ((1720 - radius) - 2800)):
            # use the inside z-direction zones
            if radius < 1281:
                return weight_edep_far_inside_z(z)
            elif radius <= 1520:
                return weight_edep_middle_inside_z(z)
            else:
                return weight_edep_close_inside_z(z)
        else: 
            # use the r-zones
            if z > 0:
                return weight_edep_top_inside_r(radius)
            elif z > -2600:
                return weight_edep_middle_r(radius)
            else:
                return weight_edep_bot_inside_r(radius)


def weight_edep_top_outside_r(radius: float) -> tuple[float, float]:
    if radius < 1820:
        raise ValueError("Radius must be >= 1820 mm for top_outside_r zone.")

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

    if radius < 1820:
        raise ValueError("Radius must be >= 1820 mm for bottom_outside_r zone.")

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

    if not (z >= 300 or z <= -2900):
        raise ValueError("Z must be >= 300 mm or <= -2900 mm for close_outside_z zone.")

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

    if not (-2900 < z < 300):
        raise ValueError("Z must be < 300 mm or > -2900 mm for close_inside_z zone.")

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

    if not (-2900 < z < 300):
        raise ValueError("Z must be < 300 mm or > -2900 mm for middle_inside_z zone.")

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

    if not (-2900 < z < 300):
        raise ValueError("Z must be < 300 mm or > -2900 mm for far_inside_z zone.")

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