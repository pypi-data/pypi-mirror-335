from ..utils import dHf, Sf, Gf
from .species import Species


class C2H4(Species):
    def __init__(self, T_C, nu=None):
        super().__init__(T_C, nu)
        self.min_temp_K = 298
        self.max_temp_K = 1200
        self.check_temps()
        self.Hf_298 = 52.4  # kJ/mol
        self.thermo_params = {
            "A": -6.387880,
            "B": 184.4019,
            "C": -112.9718,
            "D": 28.49593,
            "E": 0.315540,
            "F": 48.17332,
            "G": 163.1568,
            "H": 52.46694
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
