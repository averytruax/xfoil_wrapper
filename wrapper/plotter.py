# TODO: Move functions in this directory to a different directory
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly.express import colors
from pydantic import BaseModel
from wrapper.data_classes import OptimizationResults
from geometry.airfoil import Airfoil
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

        residuals = self.plot_residuals()
        self.plots.append(residuals)
        objective = self.plot_objective()
        self.plots.append(objective)

        for plot in self.plots:
            plot.show()





    def plot_residuals(self) -> go.Figure:
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
            height=1200,
            width=800,
            xaxis_title='Iteration',
            yaxis_title='Coefficient Value',
            showlegend=True)

        return fig

    def plot_objective(self) -> go.Figure:
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
            height=1200,
            width=800,
            xaxis_title='Iteration',
            yaxis_title='Objective Value',
            showlegend=True)

        return fig