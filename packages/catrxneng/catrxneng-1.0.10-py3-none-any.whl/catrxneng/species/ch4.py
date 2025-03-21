from ..utils import dHf, Sf, Gf
from .species import Species


class CH4(Species):
    def __init__(self, T_C, nu=None):
        super().__init__(T_C, nu)
        self.min_temp_K = 298
        self.max_temp_K = 1300
        self.check_temps()
        self.Hf_298 = -74.6 # kJ/mol
        self.thermo_params = {
            "A": -0.703029,
            "B": 108.4773,
            "C": -42.52157,
            "D": 5.862788,
            "E": 0.678565,
            "F": -76.84376,
            "G": 158.7163,
            "H": -74.87310
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
