import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def readData(filename):
    data = pd.read_excel(filename)
    dimensions = data.iloc[3:7,3]

    print(dimensions)
    
    
    
    
    
    
#Unit Conversion
lbs_kg = 0.453592
ft_m = 0.3048
kts_ms = 0.514444444 
rad_alpha = 180/np.pi
alpha_rad = np.pi/180


#constants
Ws = 60500#N
g0 = 9.80665
T0 = 288.15 #K
rho0 = 1.225 #kg/m^3
p0 = 101325 #Pa
aT = -0.0065 #K/m
R = 287
gamma = 1.4

refdata = 'ReferenceAircraftDataSheet.xlsx'
#Read Data
if __name__ == "__main__":
    #test = elevator_trim_curve(data)
    readData(refdata)

