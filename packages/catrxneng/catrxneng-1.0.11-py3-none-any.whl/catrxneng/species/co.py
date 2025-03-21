from ..utils import dHf, Sf, Gf
from .species import Species


class CO(Species):
    def __init__(self, T_C, nu=None):
        # https://webbook.nist.gov/cgi/cbook.cgi?ID=C630080&Units=SI&Mask=1#Thermo-Gas
        super().__init__(T_C, nu)
        self.min_temp_K = 298
        self.max_temp_K = 1300
        self.check_temps()
        self.Hf_298 = -110.53  # kJ/mol
        self.thermo_params = {
            "A": 25.56759,
            "B": 6.096130,
            "C": 4.054656,
            "D": -2.671301,
            "E": 0.131021,
            "F": -118.0089,
            "G": 227.3665,
            "H": -110.5271,
        }

    def Hf(self):
        return self.Hf_298 + dHf(self)  # kJ/mol

    def Sf(self):
        return Sf(self)  # kJ/mol

    def Gf(self):
        return Gf(self)  # kJ/mol
