import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Predetermined values for the aircraft / constants
BEM = 9165  # [lbs]
BEM_moment = 2672953.5  # [lbs-inch]
x_mac = 261.45  # [inch]
g0 = 9.80665  # [m/s**2]

# Convert to imperial units
lbs_to_kg = 0.45359237  # [-]
inch_to_m = 0.0254  # [-]

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

def loaddiagram():
    #Constants
    xcg_datum = 3.6576 #m
    x_LEMAC = 22.866 #m
    MAC = 3.48 #m
    
    #Cargo Compartments
    aft_bagg_comp = 14.41 #m3
    forward_underfloor_baggage = 5.26 #m3
    under_seat_storage = 4.16 #m3
    overhead_bins = 5.08 #m3
    cargo_not_in_cabin = 19.67 #m3
    
    #Weights
    MTOW = 41640 * g0
    OEW = 23188 * g0 
    MaxPayload = 10605 * g0               #N 
    fuel_weight = MTOW - OEW - MaxPayload            #N 
    pass_weight = 8800 * g0            #N
    no_pass = 100
    no_chairsprow = 4
    no_rows = int(no_pass / no_chairsprow)
    front_cargo_weight = (forward_underfloor_baggage/cargo_not_in_cabin)*(MaxPayload-pass_weight)
    aft_cargo_weight = (aft_bagg_comp/cargo_not_in_cabin)*(MaxPayload-pass_weight)     #N
    #locations
    pass_part_start = 11.6846 #m
    pass_part_end = 35.2796 #m
    
    
    #cg_locations
    xcg_oew = (24.258 - x_LEMAC) / MAC
    xcg_cargo_front = (15.5026 -  x_LEMAC) / MAC
    xcg_cargo_aft = (26.10587 -  x_LEMAC) / MAC
    xcg_fuel = (24.6575 -  x_LEMAC) / MAC
    chair_pitch = (pass_part_end - pass_part_start) / (no_rows*MAC)
    xcg_seats_btf = [(pass_part_end - x_LEMAC)/MAC - 0.5 * chair_pitch]
    xcg_seats_ftb = [(pass_part_start - x_LEMAC)/MAC + 0.5 * chair_pitch]
    for i in range(no_rows-1):
        xcg_seats_btf.append(xcg_seats_btf[-1]-chair_pitch)
        xcg_seats_ftb.append(xcg_seats_ftb[-1]+chair_pitch)
    
    print('oew:  '+ str(xcg_oew))
    print('xcg_cargo_front:  '+str(xcg_cargo_front))
    print('xcg_cargo_aft:  '+str(xcg_cargo_aft))
    print('xcg_fuel:  '+str(xcg_fuel))
    
    #Loading functions
    OEW_point = [xcg_oew,OEW]
    #add cargo
    only_aft_point = (xcg_cargo_aft*aft_cargo_weight + xcg_oew*OEW)/(OEW + aft_cargo_weight)
    only_front_point = (xcg_cargo_front*front_cargo_weight +xcg_oew*OEW)/(OEW + front_cargo_weight)
    both_cargo_point = (xcg_cargo_aft*aft_cargo_weight + xcg_oew*OEW + xcg_cargo_front*front_cargo_weight)/(OEW + front_cargo_weight + aft_cargo_weight)
    cargo_points = [[OEW_point[0], only_aft_point, both_cargo_point, only_front_point, OEW_point[0]],[OEW, OEW + front_cargo_weight, OEW + front_cargo_weight + aft_cargo_weight, OEW + aft_cargo_weight,OEW]]
    
    #Add passengers
    #Window
    two_pass_weight = (pass_weight/no_pass)*2
    
    window_pointsbtf = [[both_cargo_point],[OEW + front_cargo_weight + aft_cargo_weight]]
    window_pointsftb = [[both_cargo_point],[OEW + front_cargo_weight + aft_cargo_weight]]
    for i in range(no_rows):
        new_weight = window_pointsbtf[1][-1] + two_pass_weight
        window_pointsbtf[0].append((window_pointsbtf[0][-1]*window_pointsbtf[1][-1] + xcg_seats_btf[i]*two_pass_weight)/new_weight)
        window_pointsbtf[1].append(new_weight)
        window_pointsftb[0].append((window_pointsftb[0][-1]*window_pointsftb[1][-1] + xcg_seats_ftb[i]*two_pass_weight)/new_weight)
        window_pointsftb[1].append(new_weight)
    #Aisle
    aisle_pointsbtf = [[window_pointsbtf[0][-1]],[window_pointsbtf[1][-1]]]
    aisle_pointsftb = [[window_pointsftb[0][-1]],[window_pointsbtf[1][-1]]]
    for i in range(no_rows):
        new_weight = aisle_pointsbtf[1][-1] + two_pass_weight
        aisle_pointsbtf[0].append((aisle_pointsbtf[0][-1]*aisle_pointsbtf[1][-1] + xcg_seats_btf[i]*two_pass_weight)/new_weight)
        aisle_pointsbtf[1].append(new_weight)
        aisle_pointsftb[0].append((aisle_pointsftb[0][-1]*aisle_pointsftb[1][-1] + xcg_seats_ftb[i]*two_pass_weight)/new_weight)
        aisle_pointsftb[1].append(new_weight)
    
    #Fuel
    fuel_point = [[aisle_pointsftb[0][-1]],[aisle_pointsftb[1][-1]]]
    fuel_point[0].append((fuel_point[0][0]*fuel_point[1][0] + xcg_fuel*fuel_weight)/(fuel_weight + fuel_point[1][0]))
    fuel_point[1].append(fuel_weight + fuel_point[1][0])

    #max values
    allcg = [OEW_point[0], only_aft_point,only_front_point, both_cargo_point, fuel_point[0][-1]]
    name_lst = window_pointsbtf[0], window_pointsftb[0], aisle_pointsbtf[0], aisle_pointsftb[0], 
    for name in name_lst:
        allcg.append(max(name))
        allcg.append(min(name))
    max_cg = max(allcg)
    min_cg = min(allcg)
    margin = 0.02
    max_margin_cg = max_cg + margin*MAC
    min_margin_cg = min_cg - margin*MAC
    max_weight = fuel_point[1][-1]
    min_weight = OEW

    
    #PLOTS

    fig = plt.figure(figsize=(9, 7))
    plt.scatter(xcg_oew, OEW, zorder = 6, label='OEW')
    plt.xlabel('x_cg/MAC [-]')
    plt.ylabel('Weight [N]')
    plt.title('Load diagram CRJ1000')
    plt.plot(cargo_points[0],cargo_points[1], 'r', marker = 'x', zorder = 5, label = 'Cargo')
    plt.plot(window_pointsbtf[0],window_pointsbtf[1], 'g', marker = 'o', zorder = 4, label = 'Window passengers btf')
    plt.plot(window_pointsftb[0],window_pointsftb[1], 'c', marker = 'D', zorder = 3, label = 'Window passengers ftb')
    plt.plot(aisle_pointsbtf[0],aisle_pointsbtf[1], 'k', marker = 'o', zorder = 2, label = 'Aisle passengers btf')
    plt.plot(aisle_pointsftb[0],aisle_pointsftb[1], 'm', marker = 'D', zorder = 1, label = 'Aisle passengers ftb')
    plt.plot(fuel_point[0],fuel_point[1], 'b', marker = 'D', zorder = 0, label = 'Fuel')
    plt.vlines(x = max_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder =0, label = 'Margin = '+ str(round((margin)*100,2))+'% or '+str(round(margin*MAC*100,4))+' [cm]\nMaxCG = '+str(round(max_margin_cg,4))+'\nMinCG = '+str(round(min_margin_cg,4)))
    plt.vlines(x = min_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder=0)
    plt.vlines(x = max_margin_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder= 0)
    plt.vlines(x = min_margin_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder = 0)
    plt.xlim(min_margin_cg*0.7, max_margin_cg*1.05)
    plt.ylim(min_weight/1.02, max_weight*1.02)
    plt.legend(loc='upper right')
    plt.grid()
    plt.savefig('LoaddiagramCRJ1000.png')
    plt.show()
    
def loaddiagram_crjexx():
    #Constants
    xcg_datum = 3.6576 #m
    x_LEMAC = 22.866 #m
    MAC = 3.48 #m
    
    #Cargo Compartments
    aft_bagg_comp = 14.41 #m3
    forward_underfloor_baggage = 5.26 #m3
    under_seat_storage = 4.16 #m3
    overhead_bins = 5.08 #m3
    cargo_not_in_cabin = 19.67 #m3
    
    #Weights
    MTOW = 41640 * g0
    OEW = 22028.6 * g0    
    MaxPayload = 10253 * g0           #N 
    fuel_weight = MTOW - OEW - 1350*g0 - 1650*g0 - MaxPayload #N
    print(fuel_weight/9.80665)
    pass_weight = (8800 - 88*4) * g0            #N
    no_pass = 100
    no_chairsprow = 4
    no_rows = int(no_pass / no_chairsprow)
    front_cargo_weight = (forward_underfloor_baggage/cargo_not_in_cabin)*(MaxPayload-pass_weight)
    aft_cargo_weight = (aft_bagg_comp/cargo_not_in_cabin)*(MaxPayload-pass_weight)     #N
    
    #Change 2
    forward_battery_weight = 1350 * g0    #kg
    aft_battery_weight = 1650 * g0#kg
    forward_battery_vol = 0.934 #m3
    1.142
    aft_battery_vol = 1096.08*0.0254 - 1.142/(0.0254*2) #m3
    #locations
    pass_part_start = 11.6846 #m
    pass_part_end = 35.2796 #m
    
    #Change 1
    OEW = 0.95 * OEW  
    
    #cg_locations
    xcg_oew = (24.258 - x_LEMAC) / MAC
    #Change 1
    xcg_oew = xcg_oew - 0.5/MAC
    xcg_cargo_front = (15.5026 -  x_LEMAC) / MAC
    xcg_cargo_aft = (26.10587 -  x_LEMAC) / MAC
    #Change 3 
    xcg_bat_forward = xcg_cargo_front - (forward_underfloor_baggage/4 + forward_battery_vol/4)/MAC
    xcg_bat_aft = (1096.08*0.0254 - 1.142/2 - xcg_datum)/MAC
    #Change 5
    xcg_cargo_front = xcg_cargo_front + forward_battery_vol/(2*MAC)
    xcg_cargo_aft = (1.325445554 + 959.5*0.0254 - xcg_datum)/MAC
    
    xcg_fuel = (24.6575 -  x_LEMAC) / MAC
    chair_pitch = (pass_part_end - pass_part_start) / (no_rows*MAC)
    xcg_seats_btf = [(pass_part_end - x_LEMAC)/MAC - 0.5 * chair_pitch]
    xcg_seats_ftb = [(pass_part_start - x_LEMAC)/MAC + 0.5 * chair_pitch]
    for i in range(no_rows-1):
        xcg_seats_btf.append(xcg_seats_btf[-1]-chair_pitch)
        xcg_seats_ftb.append(xcg_seats_ftb[-1]+chair_pitch)

    #Change 4
    xcg_seats_btf.remove(xcg_seats_btf[0])
    xcg_seats_ftb.remove(xcg_seats_ftb[-1])
    
    #add Batteries
    xcg_oew = (xcg_oew*OEW + xcg_bat_aft*aft_battery_weight + xcg_bat_forward*forward_battery_weight)/(OEW + aft_battery_weight + forward_battery_weight)
    OEW = OEW + aft_battery_weight + forward_battery_weight
    fuel_weight = MTOW - OEW - MaxPayload #N
    
    print('oew:  '+ str(xcg_oew))
    print('xcg_cargo_front:  '+str(xcg_cargo_front))
    print('xcg_cargo_aft:  '+str(xcg_cargo_aft))
    print('xcg_fuel:  '+str(xcg_fuel))
    
    #Loading functions
    OEW_point = [xcg_oew,OEW]
    #add cargo
    only_aft_point = (xcg_cargo_aft*aft_cargo_weight + xcg_oew*OEW)/(OEW + aft_cargo_weight)
    only_front_point = (xcg_cargo_front*front_cargo_weight +xcg_oew*OEW)/(OEW + front_cargo_weight)
    both_cargo_point = (xcg_cargo_aft*aft_cargo_weight + xcg_oew*OEW + xcg_cargo_front*front_cargo_weight)/(OEW + front_cargo_weight + aft_cargo_weight)
    cargo_points = [[OEW_point[0], only_aft_point, both_cargo_point, only_front_point, OEW_point[0]],[OEW, OEW + front_cargo_weight, OEW + front_cargo_weight + aft_cargo_weight, OEW + aft_cargo_weight,OEW]]
    
    #Add passengers
    #Window
    two_pass_weight = (pass_weight/(no_pass-4))*2 #change 5
    
    window_pointsbtf = [[both_cargo_point],[OEW + front_cargo_weight + aft_cargo_weight]]
    window_pointsftb = [[both_cargo_point],[OEW + front_cargo_weight + aft_cargo_weight]]
    for i in range(no_rows-1):
        new_weight = window_pointsbtf[1][-1] + two_pass_weight
        window_pointsbtf[0].append((window_pointsbtf[0][-1]*window_pointsbtf[1][-1] + xcg_seats_btf[i]*two_pass_weight)/new_weight)
        window_pointsbtf[1].append(new_weight)
        window_pointsftb[0].append((window_pointsftb[0][-1]*window_pointsftb[1][-1] + xcg_seats_ftb[i]*two_pass_weight)/new_weight)
        window_pointsftb[1].append(new_weight)
    #Aisle
    aisle_pointsbtf = [[window_pointsbtf[0][-1]],[window_pointsbtf[1][-1]]]
    aisle_pointsftb = [[window_pointsftb[0][-1]],[window_pointsbtf[1][-1]]]
    for i in range(no_rows-1):
        new_weight = aisle_pointsbtf[1][-1] + two_pass_weight
        aisle_pointsbtf[0].append((aisle_pointsbtf[0][-1]*aisle_pointsbtf[1][-1] + xcg_seats_btf[i]*two_pass_weight)/new_weight)
        aisle_pointsbtf[1].append(new_weight)
        aisle_pointsftb[0].append((aisle_pointsftb[0][-1]*aisle_pointsftb[1][-1] + xcg_seats_ftb[i]*two_pass_weight)/new_weight)
        aisle_pointsftb[1].append(new_weight)
    
    #Fuel
    fuel_point = [[aisle_pointsftb[0][-1]],[aisle_pointsftb[1][-1]]]
    fuel_point[0].append((fuel_point[0][0]*fuel_point[1][0] + xcg_fuel*fuel_weight)/(fuel_weight + fuel_point[1][0]))
    fuel_point[1].append(fuel_weight + fuel_point[1][0])

    #max values
    allcg = [OEW_point[0], only_aft_point,only_front_point, both_cargo_point, fuel_point[0][-1]]
    name_lst = window_pointsbtf[0], window_pointsftb[0], aisle_pointsbtf[0], aisle_pointsftb[0], 
    for name in name_lst:
        allcg.append(max(name))
        allcg.append(min(name))
    max_cg = max(allcg)
    min_cg = min(allcg)
    margin = 0.02
    max_margin_cg = max_cg + margin*MAC
    min_margin_cg = min_cg - margin*MAC
    max_weight = fuel_point[1][-1]
    min_weight = OEW
    

    #PLOTS

    fig = plt.figure(figsize=(9, 7))
    plt.scatter(xcg_oew, OEW, zorder = 6, label='OEW')
    plt.xlabel('x_cg/MAC [-]')
    plt.ylabel('Weight [N]')
    plt.title('Load diagram CRJEXX')
    plt.plot(cargo_points[0],cargo_points[1], 'r', marker = 'x', zorder = 5, label = 'Cargo')
    plt.plot(window_pointsbtf[0],window_pointsbtf[1], 'g', marker = 'o', zorder = 4, label = 'Window passengers btf')
    plt.plot(window_pointsftb[0],window_pointsftb[1], 'c', marker = 'D', zorder = 3, label = 'Window passengers ftb')
    plt.plot(aisle_pointsbtf[0],aisle_pointsbtf[1], 'k', marker = 'o', zorder = 2, label = 'Aisle passengers btf')
    plt.plot(aisle_pointsftb[0],aisle_pointsftb[1], 'm', marker = 'D', zorder = 1, label = 'Aisle passengers ftb')
    plt.plot(fuel_point[0],fuel_point[1], 'b', marker = 'D', zorder = 0, label = 'Fuel')
    plt.vlines(x = max_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder =0, label = 'Margin = '+ str(round((margin)*100,2))+'% or '+str(round(margin*MAC*100,4))+' [cm]\nMaxCG = '+str(round(max_margin_cg,4))+'\nMinCG = '+str(round(min_margin_cg,4)))
    plt.vlines(x = min_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder=0)
    plt.vlines(x = max_margin_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder= 0)
    plt.vlines(x = min_margin_cg, ymin = min_weight/1.02, ymax = max_weight*1.02, zorder = 0)
    plt.xlim(min_margin_cg*0.5, max_margin_cg*1.05)
    plt.ylim(min_weight/1.02, max_weight*1.02)
    plt.legend(loc='upper right')
    plt.grid()
    plt.savefig('LoaddiagramCRJEXX.png')
    plt.show()






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

    #xcg_measurement1 = calculate_cg(fuel_used, fuel_start, payload_masses, payload_data)
    #print(f"\nElevator Trim Curve: Measurement 1 \nx_cg is {round(xcg_measurement1, 3)} m.")
    test = loaddiagram()
    test2 = loaddiagram_crjexx()
    # Delta xcg calculation, Steven moves between the pilots at 131:
    #   fuel_used1 = 768    # [lbs]
    #   fuel_used2 = 801    # [lbs]
    fuel_used1 = 3416.234201  # [N]
    fuel_used2 = 3563.025514  # [N]
    payload_data2 = [131, 131, 214, 214, 251, 251, 288, 131, 170]  # [inch]
    xcg1 = calculate_cg(fuel_used1, fuel_start, payload_masses, payload_data)
    xcg2 = calculate_cg(fuel_used2, fuel_start, payload_masses, payload_data2)
    delta_xcg = xcg1 - xcg2
    #

    print(f"\nSteven delta xcg calculation \nThe CG has shifted {round(delta_xcg, 3)} m to the fore of the aircraft.")
