"""
Functions for importing S-parameter data from different file formats.
"""

import numpy as np


def import_em_spar(file_name, port_number):
    """
    Import S-parameters from EM simulation (hdfem) output file.

    Args:
        file_name (str): Path to the S-parameter file.
        port_number (int): Number of ports specified by user.

    Returns:
        dict: A dictionary containing frequency_list, mag_list and phase_list.
    """
    if not file_name:
        return {"frequency_list": np.array([]), "mag_list": np.array([]), "phase_list": np.array([])}

    # Load data from file
    data = np.genfromtxt(file_name, dtype=float)

    # Extract frequency list (first column)
    frequency_list = data[:, 0]

    # Initialize arrays to store magnitudes and phases
    mag_list = np.zeros((port_number, len(frequency_list)), dtype=float)
    phase_list = np.zeros((port_number, len(frequency_list)), dtype=float)

    # Fill the S-parameters arrays
    for i in range(port_number):
        mag_idx = 1 + i * 2
        phase_idx = 2 + i * 2

        # Store magnitude and phase directly
        mag_list[i, :] = data[:, mag_idx]
        phase_list[i, :] = data[:, phase_idx]

    return {
        "frequency_list": frequency_list,
        "mag_list": mag_list,
        "phase_list": phase_list
    }


def import_spice_spar(file_name, port_number):
    """
    Import S-parameters from Ngspice simulation output file.

    Args:
        file_name (str): Path to the S-parameter file.
        port_number (int): Number of ports specified by user.

    Returns:
        dict: A dictionary containing frequency_list, mag_list and phase_list.
    """
    if not file_name:
        return {"frequency_list": np.array([]), "mag_list": np.array([]), "phase_list": np.array([])}

    # Read the entire file content
    with open(file_name, 'r') as file:
        content = file.readlines()

    # Parse file to find data blocks
    frequency_list = []
    mag_data = {}
    phase_data = {}

    current_s_param = None
    in_data_section = False

    for line in content:
        line = line.strip()

        # Check for data section header
        if "Index" in line and "frequency" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("mag(s_"):
                    # Extract i and j from mag(s_i_j)
                    s_id = part.replace("mag(s_", "").replace(")", "")
                    current_s_param = s_id
                    # Initialize data list
                    if current_s_param not in mag_data:
                        mag_data[current_s_param] = []
                        phase_data[current_s_param] = []
            in_data_section = True
            continue

        # Skip separator lines and empty lines
        if not line or line.startswith('---') or line.startswith('*'):
            continue

        # Process data lines
        if in_data_section and current_s_param:
            parts = line.split()
            if len(parts) >= 4:  # Expecting: index, frequency, magnitude, phase
                try:
                    freq = float(parts[1])
                    mag = float(parts[2])
                    phase = float(parts[3])

                    # Only add frequency once (assuming all blocks have same frequencies)
                    if freq not in frequency_list:
                        frequency_list.append(freq)

                    mag_data[current_s_param].append(mag)
                    phase_data[current_s_param].append(phase)
                except (ValueError, IndexError):
                    continue

    # Convert frequency list to numpy array
    frequency_list = np.array(frequency_list)
    num_freqs = len(frequency_list)

    # Initialize output arrays
    mag_list = np.zeros((port_number, num_freqs), dtype=float)
    phase_list = np.zeros((port_number, num_freqs), dtype=float)

    # Fill the arrays from parsed data
    for s_id, mags in mag_data.items():
        try:
            parts = s_id.split('_')
            if len(parts) == 2:
                i, j = int(parts[0]), int(parts[1])
                if i <= port_number:
                    port_idx = i - 1
                    mag_list[port_idx, :] = mags[:num_freqs]
                    phase_list[port_idx, :] = phase_data[s_id][:num_freqs]
        except (ValueError, IndexError) as e:
            print(f"Error processing S-parameter ID {s_id}: {e}")
            continue

    return {
        "frequency_list": frequency_list,
        "mag_list": mag_list,
        "phase_list": phase_list
    }