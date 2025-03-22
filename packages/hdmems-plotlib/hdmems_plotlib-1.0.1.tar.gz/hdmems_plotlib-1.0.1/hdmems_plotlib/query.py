"""
Functions for querying S-parameter data.
"""

import numpy as np


def get_spar_at_freq(data, target_freq):
    """
    Get S-parameters at the specified frequency. Returns error if the exact frequency doesn't exist.

    Args:
        data (dict): Dictionary containing frequency_list, mag_list and phase_list.
        target_freq (float): Target frequency to query the S-parameters.

    Returns:
        dict: Dictionary containing:
            - 'frequency': The frequency used
            - 'mag': Magnitude values of S-parameters at the frequency
            - 'phase': Phase values of S-parameters at the frequency
        OR
        None: If the frequency doesn't exist, with error message printed
    """
    # Check if data is valid
    if not data or "frequency_list" not in data or len(data["frequency_list"]) == 0:
        print(f"Error: Invalid data provided")
        return None

    # Check if the exact target frequency exists
    frequency_list = data["frequency_list"]
    exact_match = np.where(frequency_list == target_freq)[0]

    if len(exact_match) == 0:
        print(f"Error: Frequency {target_freq} does not exist in the data")
        return None

    # Get index of the exact frequency
    idx = exact_match[0]
    actual_freq = frequency_list[idx]

    # Get magnitude and phase at that frequency
    mag = data["mag_list"][:, idx] if "mag_list" in data else None
    phase = data["phase_list"][:, idx] if "phase_list" in data else None

    return {
        "frequency": actual_freq,
        "mag": mag,
        "phase": phase
    }