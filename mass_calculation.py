import numpy as np
import pandas as pd

def calculate_cg(fuel_used, fuel_start, masses, data):
    """
    Calculate the center of gravity of the aircraft based on the fuel and payload carried.

    :param fuel_used: weight of fuel that has been used up during flight, 0 at take-off [N]
    :param fuel_start: total fuel weight carried at take-off [N]
    :param masses: list of payload masses [kg]
    :param data: list of xcg_datum of the payload masses [inch]
    :return: xcg, aircraft's center of gravity with respect to the MAC [m]
    """
    # Check for incorrect input types. Fuel should be int or float
    if (not isinstance(fuel_used, (int, np.integer, float, np.floating))) or (
    not isinstance(fuel_start, (int, np.integer, float, np.floating))):
        raise TypeError("Input is of wrong type")

    # Masses and data should be lists, arrays or Pandas series
    if (not isinstance(masses, (list, np.ndarray, pd.Series))) or (not isinstance(data, (list, np.ndarray, pd.Series))):
        raise TypeError("Input is of wrong type")

    # Check for incorrect lists (wrong length/containing non-numbers)
    if len(masses) != len(data):
        raise ValueError("Input lists have different lengths")
    elif any((not isinstance(x, (int, np.integer, float, np.floating))) or (
    not isinstance(y, (int, np.integer, float, np.floating))) for x, y in zip(masses, data)):
        raise ValueError("Lists must contain numbers")

    # Check for negative values
    if fuel_used < 0 or fuel_start < 0 or any(x < 0 or y < 0 for x, y in zip(masses, data)):
        raise ValueError("Input must be positive")

    # Predetermined values for the aircraft / constants
    BEM = 9165  # [lbs]
    BEM_moment = 2672953.5  # [lbs-inch]
    x_mac = 261.45  # [inch]
    g0 = 9.80665  # [m/s**2]

    # Convert to imperial units
    lbs_to_kg = 0.45359237  # [-]
    inch_to_m = 0.0254  # [-]
    fuel_used = fuel_used / g0 * 1 / lbs_to_kg  # [lbs]
    fuel_start = fuel_start / g0 * 1 / lbs_to_kg  # [lbs]
    masses = [m * 1 / lbs_to_kg for m in masses]  # [lbs]

    # Calculate payload mass[lbs] and moment[lbs-inch]
    payload_moment = 0
    payload = 0
    for i in range(len(masses)):
        payload += masses[i]
        payload_moment = payload_moment + (masses[i] * data[i])

    # Determine zero fuel mass and moment and moments
    ZFM = BEM + payload  # [lbs]
    ZFM_moment = BEM_moment + payload_moment  # [lbs-inch]

    # Calculate remaining fuel and retrieve moment from linear lookup table relation
    # for fuel load below 100 lbs no change in the xcg_datum is assumed
    fuel_load = fuel_start - fuel_used  # [lbs]
    if fuel_load < 100:
        fuel_moment = fuel_load * 298.16
    else:
        fuel_moment = 100 * (2.8526 * fuel_load + 9.8957)  # [lbs-inch]
    # Fuel moment lookup table
    xp = np.append(np.arange(0, 5000, 100), 5008)
    fp = np.array(
        [0,298.16, 591.18, 879.08, 1165.42, 1448.4, 1732.53, 2014.8, 2298.84, 2581.92, 2866.3, 3150.18, 3434.52, 3718.52,
         4003.23, 4287.76,
         4572.24, 4856.56, 5141.16, 5425.64, 5709.9, 5994.04, 6278.47, 6562.82, 6846.96, 7131, 7415.33, 7699.6, 7984.34,
         8269.06, 8554.05,
         8839.04, 9124.8, 9410.62, 9696.97, 9983.4, 10270.08, 10556.84, 10843.87, 11131, 11418.2, 11705.5, 11993.31,
         12281.18, 12569.04,
         12856.86, 13144.73, 13432.48, 13720.56, 14008.46, 14320.34])

    fuel_moment = np.interp(fuel_load, xp, fp)*100

    # Determine ramp mass
    total_mass = ZFM + fuel_load  # [lbs]
    total_moment = ZFM_moment + fuel_moment  # [lbs-inch]

    # Find xcg_datum and xcg
    xcg_datum = total_moment / total_mass  # [inch]
    xcg = (xcg_datum - x_mac) * inch_to_m  # [m]

    return xcg


if __name__ == "__main__":
    # Input list of payload mass and known xcg_datum (default values are our experiment)
    payload_masses = [104, 93, 63, 82, 76, 83, 83, 89, 85]  # [kg]
    payload_masses2 = [0 for x in payload_masses]
    payload_data = [131, 131, 214, 214, 251, 251, 288, 288, 170]  # [inch]

    # Example calculation:
    # Measurement 1, Elevator Trim Curve
    #   fuel_used = 541     # [lbs]
    #   fuel_start = 4050   # [lbs]
    fuel_used = 2406.487894  # [N]
    fuel_start = 18015.29754  # [N]

    xcg_measurement1 = calculate_cg(fuel_used, fuel_start, payload_masses, payload_data)
    print(f"\nElevator Trim Curve: Measurement 1 \nx_cg is {round(xcg_measurement1, 3)} m.")

    # Delta xcg calculation, Steven moves between the pilots at 131:
    #   fuel_used1 = 768    # [lbs]
    #   fuel_used2 = 801    # [lbs]
    fuel_used1 = 3416.234201  # [N]
    fuel_used2 = 3563.025514  # [N]
    payload_data2 = [131, 131, 214, 214, 251, 251, 288, 131, 170]  # [inch]
    xcg1 = calculate_cg(fuel_used1, fuel_start, payload_masses, payload_data)
    xcg2 = calculate_cg(fuel_used2, fuel_start, payload_masses, payload_data2)
    delta_xcg = xcg1 - xcg2

    print(f"\nSteven delta xcg calculation \nThe CG has shifted {round(delta_xcg, 3)} m to the fore of the aircraft.")
