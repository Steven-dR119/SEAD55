import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def read_data(refdata):
    data = pd.read_excel(refdata)
    dimensions = data.iloc[25:32, 11]
    return dimensions


def plot_scissor(x_ac, CL_ah, CL_a, de_da, l_h, MAC, Vh_V, SM):
    Sh_S = np.linspace(0, 0.8, 1000)
    x_np = CL_ah / CL_a * (1-de_da) * l_h/MAC * Vh_V**2 * Sh_S + x_ac
    print(x_np)
    x_cg = x_np - SM
    print(x_cg)
    plt.figure(1)
    plt.plot(x_np, Sh_S, color='b')
    plt.plot(x_cg, Sh_S, color='orange')
    plt.xlabel("X_cg/MAC")
    plt.ylabel("Sh/S")
    plt.show()


if __name__ == "__main__":
    refdata = "ReferenceAircraftDataSheet.xlsx"
    SM = 0.05

    data = read_data(refdata)
    print(data)
    Vh_V = data.iloc[0]
    CL_ah = data.iloc[1]
    CL_a = data.iloc[2]
    lh = data.iloc[3]
    lh = 17
    de_da = data.iloc[4]
    x_ac = data.iloc[5]
    MAC = data.iloc[6]

    plot_scissor(x_ac, CL_ah, CL_a, de_da, lh, MAC, Vh_V, SM)