import plotly.graph_objects as go, numpy as np

from catrxneng.constants import *


class Reaction:
    def __init__(self):
        pass

    def dG_rxn(self):
        return self.dH_rxn() - self.T_K * self.dS_rxn()

    def Keq(self):
        return np.exp(-self.dG_rxn() / R["kJ/mol/K"] / self.T_K)

    def plot_K_vs_temp(self):
        self.T_K = self.T_C + 273
        fig = go.Figure()
        trace = go.Scatter(x=self.T_C, y=self.Keq(), mode="lines")
        fig.add_trace(trace)
        fig.update_layout(
            title=dict(text="<b>Equilibrium constant</b>", x=0.5),
            xaxis_title="<b>Temperature (°C)</b>",
            yaxis_title="<b>K</b>",
            width=800
        ) 
        fig.show()
