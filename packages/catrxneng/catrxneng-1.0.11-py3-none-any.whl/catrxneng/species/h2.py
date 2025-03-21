from ..utils import dHf, Sf, Gf
from .species import Species


class H2(Species):
    def __init__(self, T_C, nu=None):
        super().__init__(T_C, nu)
        self.min_temp_K = 298
        self.max_temp_K = 1000
        self.check_temps()
        self.Hf_298 =  0 # kJ/mol
        self.thermo_params = {
            "A": 33.066178,
            "B": -11.363417,
            "C": 11.432816,
            "D": -2.772874,
            "E": -0.158558,
            "F": -9.980797,
            "G": 172.707974,
            "H": 0,
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
