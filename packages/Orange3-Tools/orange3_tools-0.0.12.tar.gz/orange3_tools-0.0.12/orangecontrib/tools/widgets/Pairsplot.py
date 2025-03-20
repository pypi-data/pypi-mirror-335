import Orange.data
import numpy as np
import pandas as pd
import seaborn as sns
from AnyQt.QtCore import Qt
from orangewidget import gui
from Orange.widgets import settings
from Orange.widgets.utils.itemmodels import DomainModel
from Orange.preprocess.preprocess import Normalize
from Orange.data.pandas_compat import  table_to_frame
from Orange.data import Table, Domain, ContinuousVariable
from orangecontrib.tools.widgets.utils import MatplotlibWidget

from orangecontrib.tools.widgets.mywidgets import OWWidget, Input, Msg

def safe_compare(group, value):
    """Manejo seguro de comparaciones con NumPy arrays"""
    if isinstance(value, np.ndarray):
        return np.array_equal(group, value)
    return group == value

class Pairsplot(OWWidget):
    # Nombre del widget como se verá en el lienzo
    name = 'Pairs plot'
    description = 'Pairs plot with some tunning features'
    icon = 'icons/Pairs.svg'
    keywords = ["widget", "tools"]
    category = 'Tools'

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        sample = None #Output("Sampled Data", Orange.data.Table)

    graph_name = "graph"  # QGraphicsView (pg.PlotWidget)
    settingsHandler = settings.DomainContextHandler(
        match_values=settings.DomainContextHandler.MATCH_VALUES_CLASS)
    attr_numvars=settings.ContextSetting(None)
    attr_x = settings.ContextSetting(None)
    attr_y = settings.ContextSetting(None)
    attr_size = settings.Setting(1)
    key_size = settings.Setting(1)
    attr_col = settings.ContextSetting('b')
    key_col = settings.ContextSetting('Blue')
    attr_sym = settings.Setting('o')
    key_sym = settings.Setting('Circle')
    attr_bins = settings.Setting(10)
    key_bins = settings.Setting(10)
    axes = None

    default_background_color = np.array([0, 0xbf, 0xff])

    SYMBOL_TYPES = (
        ('Circle', 'o'),
        ('Square', 's'),
        ('Triangle', 'v'),
        ('Diamond', 'D'),
        ('Plus', 'P'),
        ('Cross', 'X'),
    )
    COLOR_NAMES = (
        ('Blue', 'b'),
        ('Red', 'r'),
        ('Green', 'g'),
        ('Cyan', 'c'),
        ('Yellow', 'y'),
        ('Magenta', 'm'),
        ('Black','k')
    )
    def resizeEvent(self,e):
        #if not self._flag:
        #    self._flag = True
        #    self.scale_image()
        #    QtCore.QTimer.singleShot(50, lambda: setattr(self,"_flag",False))
        #super().resizeEvent(e)
        self.restart()


    class Error(OWWidget.Error):
        num_features = Msg("Data must contain at least {}.")
        no_class = Msg("Data must have a single target variable.")
        no_class_values = Msg("Target variable must have at least two values.")
        no_nonnan_data = Msg("No points with defined values.")
        same_variable = Msg("Select two different variables.")


    def __init__(self):
        super().__init__()
        self.Error.add_message("same_variable")
        self.data = None
        self.selected_data = None
        self.min_x = self.max_x = self.min_y = self.max_y = None
        self._add_graph()
        self.var_model = DomainModel(valid_types=ContinuousVariable,
                                     order=DomainModel.ATTRIBUTES)
        self.attr_numvars=len(self.var_model)
        self.parameters_box = gui.widgetBox(self.controlArea, "Parameters")
        opts1 = dict(
            widget=self.parameters_box, master=self, orientation=Qt.Horizontal,
            callback=self.change_parameters, sendSelectedValue=True, contentsLength=14)
        gui.comboBox(value='key_sym', label='Plot Symbol',
                     items=[i[0] for i in self.SYMBOL_TYPES], **opts1)
        gui.comboBox(value='key_col', label='Color',
                     items=[i[0] for i in self.COLOR_NAMES], **opts1)
        gui.spin(widget=self.parameters_box, master=self, value='attr_size', minv=1, maxv=30, step=1, label="Symbol Size:",
                 alignment=Qt.AlignRight, controlWidth=80, callback=self.change_parameters)
        gui.spin(widget=self.parameters_box, master=self, value='attr_bins', minv=2, maxv=500, step=1, label="Histogram Bins:",
                 alignment=Qt.AlignRight, controlWidth=80, callback=self.change_parameters)

        gui.rubber(self.controlArea)


    def change_parameters(self):
        self.attr_sym = dict(self.SYMBOL_TYPES)[self.key_sym]
        self.attr_col = dict(self.COLOR_NAMES)[self.key_col]
        self.restart()

    def _add_graph(self):
        self.graph = MatplotlibWidget()
        self.mainArea.layout().addWidget(self.graph)

    def change_attributes(self):
        self.restart()

    def restart(self):
        self.clear_plot()
        self.select_columns_optimized()
        if self.selected_data is None:
            return
        self.replot()

    #def keyPressEvent(self, e):
    #    """Bind 'back' key to step back"""
    #    if (e.modifiers(), e.key()) in self.key_actions:
    #        fun = self.key_actions[(e.modifiers(), e.key())]
    #        fun(self)
    #    else:
    #        super().keyPressEvent(e)

    #def resizeEvent(self, event):
    #    self.restart()

    ##############################
    # Signals and data-handling

    @Inputs.data
    def set_data(self, data):

        self.closeContext()
        self.Error.clear()

        self.selected_data = None
        self.data = None
        self.clear_plot()

        if data:
            self.var_model.set_domain(data.domain)
            if len(self.var_model) < 1:
                self.Error.num_features("Only one numeric variable")
                data = None
        if not data:
            self.var_model.set_domain(None)
            return

        self.data = data
        self.attr_x = self.var_model[0]
        self.attr_y = self.var_model[1]
        self.openContext(self.data)
        self.attr_numvars=len(self.var_model)
        self.restart()


    def select_columns_optimized(self):
        if "no_nonnan_data" not in self.Error.__dict__:
            self.Error.add_message("no_nonnan_data", "No valid non-NaN data available")
        self.Error.no_nonnan_data.clear()
        if hasattr(self.Error, "same_variable"):
            self.Error.same_variable(shown=False)

        if self.data is None or self.attr_x is self.attr_y:
            if self.attr_x is self.attr_y:
                self.Error.same_variable()
            return

        domain = Domain([self.attr_x, self.attr_y])
        data = self.data.transform(domain)

        valid_data = np.all(np.isfinite(data.X), axis=1)
        if not np.any(valid_data):
            self.Error.no_nonnan_data()
            return

        self.selected_data = data[valid_data]

    def select_columns(self):
        if "no_nonnan_data" not in self.Error.__dict__:
            self.Error.add_message("no_nonnan_data", "No valid non-NaN data available")
        self.Error.no_nonnan_data.clear()
        if hasattr(self.Error, "same_variable"):
            self.Error.same_variable(shown=False)  # En lugar de borrar, oculta el mensaje
        self.selected_data = None
        if self.data is None:
            return

        if self.attr_x is self.attr_y:
            self.Error.same_variable()
            return
        domain = Domain([self.attr_x, self.attr_y])
        data = self.data.transform(domain)
        valid_data = \
            np.flatnonzero(
                np.all(
                    np.isfinite(data.X),
                    axis=1)
            )

        if not valid_data.size:
            self.Error.no_nonnan_data()
            return

        data = data[valid_data]
        self.selected_data=data



    def send_report(self):
        if self.data is None:
            return
        self.report_plot()

    ##############################
    # Plot-related methods

    def clear_plot(self):
        self.graph.getFigure().clf()


    def replot(self):
        if self.data is None or self.selected_data is None:
            self.clear_plot()
            return
        self.plot()

    def plot(self):
        sns.set()
        self.graph.getFigure().clf()
        data = table_to_frame(self.data, include_metas=True)

        # A layout of nxn subplots where n= self.attr_numvars. For efficiency, maximum n=5, discard the others.
        n = self.attr_numvars
        if n>5:
            n=5
        #fig, axes = plt.subplots(4, 4, figsize=(12, 8), sharex="col", tight_layout=True)
        self.graph.axes = self.graph.getFigure().subplots(n, n, sharex="col")

        for i in range(n):
            for j in range(n):
                # If this is the lower-triangule, add a scatterlpot for each group.
                if i > j:
                    x=data[self.data.domain.attributes[i].name]
                    y=data[self.data.domain.attributes[j].name]
                    self.graph.axes[i,j].plot(x,y, marker=self.attr_sym, color=self.attr_col,markersize=self.attr_size,linestyle='None')
                else:
                    if i < j:
                        # Remove axis and grid
                        self.graph.axes[i, j].grid(False)
                        self.graph.axes[i, j].axis('off')
                        # Add correlation coefficient
                        x = data[self.data.domain.attributes[i].name]
                        y = data[self.data.domain.attributes[j].name]
                        correlation = np.corrcoef(x, y)[0, 1]
                        cor = 'Correlation coefficient:\n {:.4f}'.format(correlation)
                        left, width = .25, .5
                        bottom, height = .25, .5
                        right = left + width
                        top = bottom + height
                        self.graph.axes[i, j].text(0.5 * (left + right), 0.5 * (bottom + top), cor,
                                                   horizontalalignment='center',
                                                   verticalalignment='center',
                                                   transform=self.graph.axes[i, j].transAxes)
                    else:
                       # If this is the main diagonal, add histograms
                         x=data[self.data.domain.attributes[i].name]
                         self.graph.axes[i,j].hist(x,color=self.attr_col, bins=self.attr_bins, alpha=0.5)
                if j == 0:
                    self.graph.axes[i,j].set_ylabel(self.data.domain.attributes[i].name)
                if i == (n-1):
                    self.graph.axes[i,j].set_xlabel(self.data.domain.attributes[j].name)



#        self.graph.getFigure().tight_layout()
        self.graph.draw()

    def _format_label(self, x, y, step):
        return \
            f"<b>Step {step}:</b><br/>" \
            f"{x:.3f}, {y:.3f}<br/>" \
            f"Cost: {self.learner.j(np.array([x, y])):.5f}"


if __name__ == '__main__':
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    file = pd.read_csv('../datasets/auto-mpg.csv')
    #WidgetPreview(Pairsplot).run(Orange.data.Table(file))

    WidgetPreview(Pairsplot).run(set_data=Orange.data.Table("iris"))
