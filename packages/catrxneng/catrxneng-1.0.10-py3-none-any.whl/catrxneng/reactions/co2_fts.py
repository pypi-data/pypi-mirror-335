from scipy.optimize import fsolve
from .reaction import Reaction
from ..species import CO2, H2, C2H4, H2O


class CO2FTS(Reaction):
    def __init__(self, temp_C):
        self.T_C = temp_C
        self.T_K = self.T_C + 273
        self.co2 = CO2(temp_C)
        self.h2 = H2(temp_C)
        self.c2h4 = C2H4(temp_C)
        self.h2o = H2O(temp_C)

    def dH_rxn(self):
        return self.c2h4.Hf() + 4 * self.h2o.Hf() - 2 * self.co2.Hf() - 6 * self.h2.Hf()

    def dS_rxn(self):
        return self.c2h4.Sf() + 4 * self.h2o.Sf() - 2 * self.co2.Sf() - 6 * self.h2.Sf()

    def eq_conv(self, p0):
        def f(extent):
            Keq = (
                (p0[2] + extent)
                * (p0[3] + extent) ** 4
                / (p0[0] - extent) ** 2
                / (p0[1] - extent) ** 6
            )
            return Keq - self.Keq()

        extent = fsolve(f, 1)
        return extent / p0[0] * 100
