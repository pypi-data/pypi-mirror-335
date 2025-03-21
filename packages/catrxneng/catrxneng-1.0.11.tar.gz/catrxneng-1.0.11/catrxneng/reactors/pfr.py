import numpy as np
import plotly.graph_objects as go, numpy as np
from scipy.integrate import solve_ivp

from ..constants import *


class PFR:
    def __init__(self, components, w, P, ghsv, p0, r):
        self.components = components
        self.w = w  # gcat
        self.P = P  # bara
        self.ghsv = ghsv  # smL/min/gcat
        self.p0 = p0
        self.Ft0 = ghsv / mol_gas_vol / 60  # mmol/min
        self.y0 = p0 / P
        self.F0 = self.y0 * self.Ft0  # mmol/min
        self.r = r  # mmol/min/gcat

    def solve(self):
        def df(w, F):
            Ft = F.sum()
            y = F / Ft
            p = y * self.P
            dFdw = np.array([])
            for i in range(0, len(F)):
                ri = self.r[i](p)  # mass balance
                dFdw = np.append(dFdw, ri)
            return dFdw

        w_span = (0, self.w)
        w_eval = np.linspace(0, self.w, 100)
        solution = solve_ivp(df, w_span, self.F0, t_eval=w_eval)
        self.w = solution.t
        self.F = solution.y
        Ft = np.zeros(len(self.w))
        for Fi in self.F:
            Ft = Ft + Fi
        self.y = []
        for Fi in self.F:
            self.y.append(Fi / Ft)
        self.conv = (self.F0[0] - self.F[0]) / self.F0[0] * 100
        self.inv_ghsv = self.w / self.Ft0

    def plot_molfrac_vs_w(self, labels):
        fig = go.Figure()
        for i, label in enumerate(labels):
            if label != "inert":
                trace = go.Scatter(x=self.w, y=self.y[i], mode="lines", name=label)
                fig.add_trace(trace)
        fig.update_layout(
            title=dict(text="<b>Mole fractions vs. catalyst mass</b>", x=0.5),
            xaxis_title="<b>Catalyst mass (g)</b>",
            yaxis_title="<b>Mole fraction</b>",
            width=700,
        )
        fig.show()

    def plot_conv_vs_w(self, label, eq_conv=None):
        fig = go.Figure()
        trace = go.Scatter(x=self.w, y=self.X, mode="lines", name=label)
        fig.add_trace(trace)
        if eq_conv:
            trace = go.Scatter(
                x=self.w,
                y=np.zeros(len(self.w)) + eq_conv,
                mode="lines",
                name=f"Equilibrium {label}",
            )
            fig.add_trace(trace)
        fig.update_layout(
            title=dict(text="<b>Conversion vs. catalyst mass</b>", x=0.5),
            xaxis_title="<b>Catalyst mass (g)</b>",
            yaxis_title="<b>Conversion (%)</b>",
            width=800,
        )
        fig.show()

    def plot_conv_vs_inv_ghsv(self, label, eq_conv=None):
        fig = go.Figure()
        trace = go.Scatter(x=self.inv_ghsv, y=self.X, mode="lines", name=label)
        fig.add_trace(trace)
        if eq_conv:
            trace = go.Scatter(
                x=self.inv_ghsv,
                y=np.zeros(len(self.w)) + eq_conv,
                mode="lines",
                name=f"Equilibrium {label}",
            )
            fig.add_trace(trace)
        fig.update_layout(
            title=dict(text="<b>Conversion vs. 1/ghsv</b>", x=0.5),
            xaxis_title="<b>1/ghsv (mmol<sup>-1</sub> min gcat)</b>",
            yaxis_title="<b>Conversion (%)</b>",
            width=800,
        )
        fig.show()

    def plot_molfracs_vs_inv_ghsv(self, labels):
        fig = go.Figure()
        for i, label in enumerate(labels):
            if label != "inert":
                trace = go.Scatter(
                    x=self.inv_ghsv, y=self.y[i], mode="lines", name=label
                )
                fig.add_trace(trace)
        fig.update_layout(
            title=dict(text="<b>Mole fractions vs. 1/ghsv</b>", x=0.5),
            xaxis_title="<b>1/ghsv (mmol<sup>-1</sub> min gcat)</b>",
            yaxis_title="<b>Mole fraction</b>",
            width=800,
        )
        fig.show()
