from .species import Species
from ..utils import dHf, Sf, Gf


class CO2(Species):
    def __init__(self, T_C,nu=None):
        super().__init__(T_C, nu)
        self.min_temp_K = 298
        self.max_temp_K = 1200
        self.check_temps()
        self.Hf_298 = -393.51  # kJ/mol
        self.thermo_params = {
            "A": 24.99735,
            "B": 55.18696,
            "C": -33.69137,
            "D": 7.948387,
            "E": -0.136638,
            "F": -403.6075,
            "G": 228.2431,
            "H": -393.5224,
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
