from ..utils import dHf, Sf, Gf
from .species import Species


class H2O(Species):
    def __init__(self, T_C, nu=None):
        super().__init__(T_C, nu)
        self.min_temp_K = 500
        self.max_temp_K = 1700
        self.check_temps()
        self.Hf_298 = -241.83  # kJ/mol
        self.thermo_params = {
            "A": 30.09200,
            "B": 6.832514,
            "C": 6.793435,
            "D": -2.534480,
            "E": 0.082139,
            "F": -250.8810,
            "G": 223.3967,
            "H": -241.8264
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
