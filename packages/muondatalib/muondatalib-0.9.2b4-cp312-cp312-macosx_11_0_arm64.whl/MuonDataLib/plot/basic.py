import plotly.graph_objects as go


class Figure(object):
    """
    A simple class to make plotting easier.
    Uses plotly under the hood.
    """
    def __init__(self, title='',
                 x_label='time (micro seconds)',
                 y_label='Counts (per micro second)'):
        """
        Creates a figure for plotting.
        :param title: the title for the plot.
        :param x_label: the x label for the plot.
        :param y_label: the y label for the plot.
        """
        self._fig = go.Figure()
        self._fig.update_layout(title=title,
                                xaxis_title=x_label,
                                yaxis_title=y_label)

    def plot(self, bin_edges, y_values, label):
        """
        Adds data to the plot as point data.
        :param bin_edges: the bin edges
        :param y_values: the y values for the histogram
        :param label:  the label for the line
        """
        bin_centres = (bin_edges[:-1] + bin_edges[1:])/2.
        self._fig.add_trace(go.Scatter(x=bin_centres,
                                       y=y_values,
                                       mode='lines+markers',
                                       name=label))

    def show(self):
        """
        Shows the figure (opens in browser)
        """
        self._fig.show()

    def plot_from_instrument(self,
                             inst,
                             det_list,
                             label,
                             period=0):
        """
        Plots the data from an instrument
        :param inst: the instrument object to plot.
        :param det_list: list of the detectors to plot
        :param period: the period to plot
        """
        hists, edges = inst.get_histograms()
        for det in det_list:
            self.plot(edges, hists[period][det],
                      label + f'Detector {det}')
