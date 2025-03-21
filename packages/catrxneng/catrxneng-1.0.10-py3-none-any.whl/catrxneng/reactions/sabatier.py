from scipy.optimize import fsolve
from .reaction import Reaction
from ..species import CO2, H2, CH4, H2O


class Sabatier(Reaction):
    def __init__(self, temp_C):
        self.T_C = temp_C
        self.T_K = self.T_C + 273
        self.co2 = CO2(temp_C)
        self.h2 = H2(temp_C)
        self.ch4 = CH4(temp_C)
        self.h2o = H2O(temp_C)

    def dH_rxn(self):
        return self.ch4.Hf() + 2 * self.h2o.Hf() - self.co2.Hf() - 4 * self.h2.Hf()

    def dS_rxn(self):
        return self.ch4.Sf() + 2 * self.h2o.Sf() - self.co2.Sf() - 4 * self.h2.Sf()

    def eq_conv(self, p0):
        def f(extent):
            Keq = (
                (p0[2] + extent)
                * (p0[3] + extent) ** 2
                / (p0[0] - extent)
                / (p0[1] - extent) ** 4
            )
            return Keq - self.Keq()

        extent = fsolve(f, 1)
        return extent / p0[0] * 100
