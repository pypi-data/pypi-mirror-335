import threading
import textwrap
from typing import List, Dict, Any, Optional, Tuple
from Orange.data import Table, Domain, StringVariable, DiscreteVariable, ContinuousVariable
import Orange.data
try:
    from Orange.data.sql.table import SqlTable
except ImportError:
    SqlTable = None
from AnyQt.QtCore import Qt
from typing import List, Dict, Any, Optional, Tuple

from Orange.widgets import widget, gui
from Orange.widgets.widget import OWWidget, Msg, Input
from Orange.widgets.utils.localization import pl
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Input
from Orange.widgets.utils.itemmodels import DomainModel
from Orange.widgets import settings
from Orange.widgets.settings import ContextSetting, ContextHandler, Context
from Orange.data.pandas_compat import table_from_frame,table_to_frame

from orangecontrib.timeseries import Timeseries
from orangecontrib.timeseries import Timeseries as TS
from statsmodels.tsa.stattools import adfuller, kpss

class StationarityContextHandler(ContextHandler):
    """
    Context handler of Stationarity. The specifics of this widget is
    that `attrs` variable is list of lists and it is not handled with
    the DomainContextHandler.
    """
    def match(self, context, domain, *args):
        if "attrs" not in context.values or domain is None:
            return self.NO_MATCH

        attrs = context.values["attrs"]
        # match if all selected attributes in domain
        values = set(y for x in attrs for y in x)
        if len(values) > 0 and all(v in domain for v in values):
            return self.PERFECT_MATCH
        else:
            return self.NO_MATCH

class OWStationarity(OWWidget):
    name = "Stationarity Tests"
    description = "Augmented Dickey-Fuller and Kwiatkowski-Phillips-Schmidt-Shin Tests"
    icon = "icons/DataInfo.svg"
    priority = 120
    keywords = "time series, ADF, KPSS, stationarity"

    vars = settings.ContextSetting(None)
    settingsHandler = StationarityContextHandler()
    attrs: List[List[str]] = ContextSetting([])

    class Inputs:
        time_series = Input("Time series", Table)

    want_main_area = False
    buttons_area_orientation = None
    resizing_enabled = False

    class Error(OWWidget.Error):
        num_features = Msg("Data must contain at least {}.")
        no_class = Msg("Data must have a single target variable.")
        no_class_values = Msg("Target variable must have at least two values.")
        no_nonnan_data = Msg("No points with defined values.")
        same_variable = Msg("Select two different variables.")


    def __init__(self):
        super().__init__()
        self.data: Optional[Timeseries] = None
        self._vars_model = DomainModel(order=DomainModel.MIXED,
                                       valid_types=ContinuousVariable)
        self.vars = None
        self.data = None
        self.data_ADF = {}
        self.data_KPSS = {}
        self.options_box = gui.widgetBox(self.controlArea, "Variable")
        opts = dict(
            widget=self.options_box, master=self, orientation=Qt.Horizontal,
            callback=self.change_attributes)
        self.description1=gui.widgetLabel(gui.comboBox(value='vars', model=self._vars_model, **opts))
        label = "<center><b><font size = \"+2\" color = \"#8B0000\">Augmented Dickey-Fuller Test</font></b></center>"
        self.title1 = gui.widgetLabel(
                   gui.vBox(self.controlArea, box=''))
        self.title1.setText(label)
        self.description = gui.widgetLabel(
                   gui.vBox(self.controlArea, box=''))
        #       self.description = gui.widgetLabel(
 #           gui.vBox(self.controlArea, box="Augmented Dickey-Fuller Test"))
        label = "<center><br><b><font size = \"+2\" color = \"#8B0000\">  Kwiatkowski-Phillips-Schmidt-Shin Test </font></br></b></center>"
        self.title1 = gui.widgetLabel(
                   gui.vBox(self.controlArea, box=''))
        self.title1.setText(label)
        self.attributes = gui.widgetLabel(
            gui.vBox(self.controlArea, box=""))

    @Inputs.time_series
    def set_data(self, data: Table):
        self.closeContext()
        self.data = data and Timeseries.from_data_table(data)
        self.selected_data = None
        self.init_model()
        self.openContext(self.data.domain if self.data else None)
        self.apply_settings()
        self.vars=(self._vars_model[:1])[0]


        if data is None:
            self.data_ADF = self.data_KPSS = {}
            self.update_info()
        else:
            self.calculate()
            self.update_info()

    def calculate(self):
        vars_name = self.vars.name
        temp_data = (table_to_frame(self.data))[vars_name]
        self.data_ADF = self.adf_test(temp_data.dropna())
        self.data_KPSS = self.kpss_test(temp_data.dropna())

    def adf_test(self,data):
        tmp_result={}
        result = adfuller(data)
        labels = ['Test Statistic', 'p-value', '#Lags Used', '#Observations Used']
        for value, label in zip(result, labels):
            if (label=='p-value'):
                val=round(value,2)
            else:
                val=round(value,3)
            tmp_result[label]=str(val)
        for key in result[4]:
            key1 = "Critical Value ({0})".format(key)
            tmp_result[key1] = str(round(result[4][key],3))
        if ((result[0] < result[4]["5%"])&(result[1]<=0.05)):
            tmp_result['<font color=\'green\' > Reject Ho </font>']="<font color=\'green\' >Time Series is Stationary</font>"
        else:
            tmp_result['<font color=\'red\' > Failed to Reject Ho </font>']="<font color=\"red\" > Time Series is Non-Stationary</font>"
        return tmp_result

    def kpss_test(self,data):
        tmp_result={}
        result = kpss(data)
        labels = ['Test Statistic', 'p-value', '#Lags Used']
        for value, label in zip(result, labels):
            if (label=='p-value'):
                val=round(value,2)
            else:
                val=round(value,3)
            tmp_result[label]=str(round(value,3))
        for key in result[3]:
            key1 = "Critical Value ({0})".format(key)
            tmp_result[key1] = str(result[3][key])
        if ((result[0] < result[3]["5%"])&(result[1]<=0.05)):
            tmp_result['<font color=\'green\'> Reject Ho </font>']="<font color=\'green\' > Time Series is Stationary</font>"
        else:
            tmp_result['<font color=\'red\' > Failed to Reject Ho </font>']="<font color=\"red\" > Time Series is Non-Stationary</font>"
        return tmp_result


    def init_model(self):
        domain = None
        if self.data is not None:
            has_time_var = hasattr(self.data, "time_variable")

            def filter_vars(variables):
                return [var for var in variables if not has_time_var or
                        has_time_var and var != self.data.time_variable]

            domain = Domain(filter_vars(self.data.domain.attributes),
                            filter_vars(self.data.domain.class_vars),
                            filter_vars(self.data.domain.metas))
        self._vars_model.set_domain(domain)

    def apply_settings(self):
        for attrs, log, typ in zip(self.attrs):
            if typ == "spline":  # TODO - spline is missing
                typ = "line"
            self._add_editor({"vars": attrs, "is_log": log,
                              "type": CurveTypes.ITEMS.index(typ)})

    def update_info(self):
        style = """<style>
                       th { text-align: right; vertical-align: top; }
                       th, td { padding-top: 4px; line-height: 125%}
                    </style>"""

        def dict_as_table(d):
            return "<table>" + \
                   "".join(f"<tr><th>{label}: </th><td>" + \
                           '<br/>'.join(textwrap.wrap(value, width=60)) + \
                           "</td></tr>"
                           for label, value in d.items()) + \
                   "</table>"

        if not self.data_ADF:
            self.description.setText("No data.")
        else:
            self.description.setText(style + dict_as_table(self.data_ADF))
        self.attributes.setHidden(not self.data_KPSS)
        if self.data_KPSS:
            self.attributes.setText(
                style + dict_as_table(self.data_KPSS))

    def send_report(self):
        if self.data_ADF:
            self.report_items("Data table properties", self.data_ADF)
        if self.data_KPSS:
            self.report_items("Additional attributes", self.data_KPSS)

    def select_columns(self):
        self.Error.no_nonnan_data.clear()
        self.Error.same_variable.clear()
        self.selected_data = None
        if self.data is None:
            return

        domain = Domain(self.vars)
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

    def change_attributes(self):
        self.restart()

    def restart(self):
        self.selected_data=vars
        #self.select_columns()
        if self.selected_data is None:
            return
        self.calculate()
        self.update_info()


if __name__ == "__main__":  # pragma: no cover
    data = Table(TS.from_file('airpassengers'))
    #data=Orange.data.Table("iris")
    #domain = Domain(data.domain.attributes[:-1], data.domain.attributes[-1])
    #data = Timeseries.from_numpy(domain, data.X[:, :-1], data.X[:, -1])
    WidgetPreview(OWStationarity).run(set_data=data)
