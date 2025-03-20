import Orange.data
import numpy as np
import seaborn as sns
from AnyQt.QtCore import Qt
from orangewidget import gui
from Orange.widgets.widget import OWWidget, Msg, Input
from Orange.widgets import settings
from Orange.widgets.utils.itemmodels import DomainModel
from Orange.preprocess.preprocess import Normalize
from Orange.data.pandas_compat import  table_to_frame
from Orange.data import Table, Domain, ContinuousVariable
from orangecontrib.tools.widgets.utils import MatplotlibWidget

class Scaterplot(OWWidget):
    # Nombre del widget como se verá en el lienzo
    name = 'Scatter plot'
    description = 'Scatter plot with some tunning features'
    icon = 'icons/sscater.svg'
    keywords = ["widget", "tools"]
    category = 'Tools'

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        sample = None #Output("Sampled Data", Orange.data.Table)

    graph_name = "graph"  # QGraphicsView (pg.PlotWidget)
    settingsHandler = settings.DomainContextHandler(
        match_values=settings.DomainContextHandler.MATCH_VALUES_CLASS)
    attr_x = settings.ContextSetting(None)
    attr_y = settings.ContextSetting(None)
    attr_size = settings.Setting(5)
    key_size = settings.Setting(5)
    attr_col = settings.ContextSetting('b')
    key_col = settings.ContextSetting('Blue')
    attr_sym = settings.Setting('o')
    key_sym = settings.Setting('Circle')
    axes = None

    default_background_color = [0, 0xbf, 0xff]

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

    class Error(OWWidget.Error):
        num_features = Msg("Data must contain at least {}.")
        no_class = Msg("Data must have a single target variable.")
        no_class_values = Msg("Target variable must have at least two values.")
        no_nonnan_data = Msg("No points with defined values.")
        same_variable = Msg("Select two different variables.")

    def __init__(self):
        super().__init__()
        self.data = None
        self.selected_data = None
        self.min_x = self.max_x = self.min_y = self.max_y = None
        self._add_graph()
        self.var_model = DomainModel(valid_types=ContinuousVariable,
                                     order=DomainModel.ATTRIBUTES)
        self.options_box = gui.widgetBox(self.controlArea, "Variables")
        opts = dict(
            widget=self.options_box, master=self, orientation=Qt.Horizontal,
            callback=self.change_attributes)
        gui.comboBox(value='attr_x', model=self.var_model, **opts)
        gui.comboBox(value='attr_y', model=self.var_model, **opts)
        self.parameters_box = gui.widgetBox(self.controlArea, "Parameters")
        opts1 = dict(
            widget=self.parameters_box, master=self, orientation=Qt.Horizontal,
            callback=self.change_parameters, sendSelectedValue=True, contentsLength=14)
        gui.comboBox(value='key_sym', label='Symbol',
                     items=[i[0] for i in self.SYMBOL_TYPES], **opts1)
        gui.comboBox(value='key_col', label='Color',
                     items=[i[0] for i in self.COLOR_NAMES], **opts1)
        gui.spin(widget=self.parameters_box, master=self, value='attr_size', minv=1, maxv=30, step=1, label="Size:",
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
        self.select_columns()
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

    def resizeEvent(self, event):
        self.restart()

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
        self.restart()


    def select_columns(self):
        self.Error.no_nonnan_data.clear()
        self.Error.same_variable.clear()
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
        self.graph.getFigure().clf()
        data = table_to_frame(self.data, include_metas=True)
        x = self.selected_data.domain[0].name
        y = self.selected_data.domain[1].name
        sns.set()
        self.axes = self.graph.getFigure().add_subplot(111)
        self.axes.plot(data[x], data[y], marker=self.attr_sym, color=self.attr_col, markersize=self.attr_size,
                       linestyle='None')
        self.graph.getFigure().supxlabel(x)
        self.graph.getFigure().supylabel(y)
        self.graph.getFigure().tight_layout()
        self.graph.draw()

    def _format_label(self, x, y, step):
        return \
            f"<b>Step {step}:</b><br/>" \
            f"{x:.3f}, {y:.3f}<br/>" \
            f"Cost: {self.learner.j(np.array([x, y])):.5f}"


if __name__ == '__main__':
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0

    WidgetPreview(Scaterplot).run(Orange.data.Table("iris"))
