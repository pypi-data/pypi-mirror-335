from scipy.optimize import fsolve
from .reaction import Reaction
from ..species import CO2, H2, CO, H2O


class RWGS(Reaction):
    def __init__(self, temp_C):
        self.T_C = temp_C
        self.T_K = self.T_C + 273
        self.co = CO(temp_C)
        self.co2 = CO2(temp_C)
        self.h2 = H2(temp_C)
        self.h2o = H2O(temp_C)

    def dH_rxn(self):
        return self.co.Hf() + self.h2o.Hf() - self.co2.Hf() - self.h2.Hf()

    def dS_rxn(self):
        return self.co.Sf() + self.h2o.Sf() - self.co2.Sf() - self.h2.Sf()

    def eq_conv(self, p0):
        def f(extent):
            Keq = (
                (p0[2] + extent)
                * (p0[3] + extent)
                / (p0[0] - extent)
                / (p0[1] - extent)
            )
            return Keq - self.Keq()
        extent = fsolve(f, 1)
        return extent/p0[0] * 100

