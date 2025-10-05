# TODO: Move functions in this directory to a different directory
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly.express import colors
from pydantic import BaseModel
from wrapper.data_classes import OptimizationResults
from geometry.airfoil import Airfoil
from geometry.geometric_functions import AirfoilFunctions
from typing import Optional
import numpy as np


class OptimizationResultsPlotter(BaseModel, arbitrary_types_allowed=True):
    """
    Class to plot the results of an optimization process
    """
    results: Optional[OptimizationResults] = None
    plots: list[go.Figure] = []

    # TODO: Add plots for airfoil shapes at each iteration
    def generate_all_plots(self) -> None:

        self.plot_residuals()
        self.plot_objective()
        self.plot_airfoil_shapes()

        for plot in self.plots:
            plot.show()





    def plot_residuals(self) -> None:
        """
        Plot the optimization results
        :param results: List of tuples containing the optimization results
        :return: Plotly figure object
        """
        fig = make_subplots(rows=2, cols=1)

        # Convert results to numpy array for easier manipulation
        results_array = np.array(self.results.residuals_list)

        # Plot each set of coefficients
        for i in range(results_array.shape[1]):
            fig.add_trace(
                go.Scatter(
                    x=np.arange(len(results_array)),
                    y=results_array[:, i],
                    mode='lines+markers',
                    name=f'Coefficient {i + 1}',
                    line=dict(color=colors.qualitative.Plotly[i % len(colors.qualitative.Plotly)])
                ),
                row=1, col=1
            )

        fig.update_layout(
            title='Optimization Results',
            height=800,
            width=1200,
            xaxis_title='Iteration',
            yaxis_title='Coefficient Value',
            showlegend=True)

        self.plots.append(fig)

        return None

    def plot_objective(self) -> None:
        """Plots the history of the objective function value over all the iterations"""

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=np.arange(len(self.results.objectives_list)),
                y=self.results.objectives_list,
                mode='lines+markers',
                name='Objective Value',
                line=dict(color=colors.qualitative.Plotly[0])
            )
        )

        fig.update_layout(
            title='Objective Results',
            height=800,
            width=1200,
            xaxis_title='Iteration',
            yaxis_title='Objective Value',
            showlegend=True)

        self.plots.append(fig)

        return None

    def plot_airfoil_shapes(self) -> None:
        """Plots the airfoil shapes at each iteration"""

        fig = go.Figure()

        af_functions = AirfoilFunctions()

        # Plot each airfoil shape with increasing opacity from 0.25 -> 1.0
        n = len(self.results.airfoils_list) if self.results and self.results.airfoils_list else 0
        min_opacity = 0.25
        max_opacity = 1.0

        # Plot each airfoil shape
        for i, airfoil in enumerate(self.results.airfoils_list):
            # Get the cst xy for the airfoil for the residuals
            xy_upper = af_functions.cst_xy(airfoil, 'upper')
            xy_lower = af_functions.cst_xy(airfoil, 'lower')
            all_x = np.concatenate((xy_upper[:, 0], xy_lower[:, 0]))
            all_y = np.concatenate((xy_upper[:, 1], xy_lower[:, 1]))

            # Compute opacity for this iteration (linear ramp)
            if n > 1:
                opacity = min_opacity + (max_opacity - min_opacity) * (i / (n - 1))
            else:
                opacity = max_opacity

            fig.add_trace(
                go.Scatter(
                    x=all_x,
                    y=all_y,
                    mode='lines',
                    name=f'Iteration {i + 1}',
                    line=dict(color=colors.qualitative.Plotly[i % len(colors.qualitative.Plotly)]),
                    opacity=opacity
                )
            )

        fig.update_layout(
            title='Airfoil Shapes Over Iterations',
            height=800,
            width=1200,
            xaxis_title='x',
            yaxis_title='y',
            showlegend=True,
            yaxis_scaleanchor="x",
            yaxis_scaleratio=1
        )

        self.plots.append(fig)

        return None