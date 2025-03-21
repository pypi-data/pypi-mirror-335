from .reaction import Reaction
from ..species import CO, H2O, CO2, H2


class WGS(Reaction):
    def __init__(self,temp_C):
        self.T_C = temp_C
        self.T_K = self.T_C + 273
        self.co = CO(temp_C)
        self.co2 = CO2(temp_C)
        self.h2 = H2(temp_C)
        self.h2o = H2O(temp_C)

    def dH_rxn(self):
        return self.co2.Hf() + self.h2.Hf() - self.co.Hf() - self.h2o.Hf()

    def dS_rxn(self):
        return self.co2.Sf() + self.h2.Sf() - self.co.Sf() - self.h2o.Sf()