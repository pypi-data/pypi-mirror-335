
from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.data import Domain

from orangecontrib.timeseries import Timeseries, ARIMA
from orangecontrib.timeseries.widgets._owmodel import OWBaseModel
from AnyQt.QtCore import QTimer, Qt
from AnyQt.QtWidgets import QFormLayout

from Orange.data import Table
from Orange.widgets import widget, gui, settings
from Orange.widgets.widget import Input, Output
from orangecontrib.timeseries import Timeseries
from orangecontrib.timeseries.models import _BaseModel
import statsmodels.api as sm
import numpy as np
class MY_ARIMA(_BaseModel):
    """Autoregressive integrated moving average (ARIMA) model

    An auto regression (AR) and moving average (MA) model with differencing.

    If exogenous variables are provided in fit() method, this becomes an
    ARIMAX model.

    Parameters
    ----------
    order : tuple (p, d, q)
        Tuple of three non-negative integers: (p) the AR order, (d) the
        degree of differencing, and (q) the order of MA model.
        If d = 0, this becomes an ARMA model.

    Returns
    -------
    unfitted_model
    """
    REQUIRES_STATIONARY = False
#    __wrapped__ = statsmodels.tsa.arima.model.ARIMA
    __wrapped__ = sm.tsa.arima.ARIMA

    def __init__(self, order=(1, 0, 0),seasonal_order=(0,0,0,0), use_exog=False):
        super().__init__()
        self.order = order
        self.seasonal_order = seasonal_order
        self.use_exog = use_exog
        self._model_kwargs.update(order=order,seasonal_order = seasonal_order)

    def __str__(self):
        return '{}({})({})'.format('SAR{}MA{}'.format('I' if self.order[1] else '',
                                                 'X' if self.use_exog else ''),
                               ','.join(map(str, self.order)),','.join(map(str,self.seasonal_order)))

    def _predict(self, steps, exog, alpha):
        pred_res = self.results.get_forecast(steps, exog=exog)
        forecast = pred_res.predicted_mean
        confint = pred_res.conf_int(alpha=alpha)
        return np.c_[forecast, confint].T

    def _before_init(self, endog, exog):
        exog = exog if self.use_exog else None
        if len(endog) == 0:
            raise ValueError('Need an endogenous (target) variable to fit')
        return endog, exog

    def _fittedvalues(self):
        # Statsmodels supports different args whether series is
        # differentiated (order has d) or not. -- stupid statsmodels
        kwargs = dict(typ='levels') if self.order[1] > 0 else {}
        return self.results.predict(**kwargs)



class OWSARIMAModel(OWBaseModel):
    name = 'SARIMA Model'
    description = 'Model the time series using ARMA, ARIMA, or SARIMA.'
    icon = 'icons/ARIMA.svg'
    priority = 210

    p = settings.Setting(1)
    d = settings.Setting(0)
    q = settings.Setting(0)
    s_p = settings.Setting(0)
    s_d = settings.Setting(0)
    s_q = settings.Setting(0)
    s_s = settings.Setting(0)

    class Inputs(OWBaseModel.Inputs):
        exogenous_data = Input("Exogenous data", Timeseries)

    def __init__(self):
        super().__init__()
        self.exog_data = None

    @Inputs.exogenous_data
    def set_exog_data(self, data):
        self.exog_data = data
        self.update_model()

    def add_main_layout(self):
        layout = QFormLayout()
        self.controlArea.layout().addLayout(layout)
        kwargs = dict(controlWidth=50, alignment=Qt.AlignRight,
                      callback=self.apply.deferred)
        layout.addRow('Auto-regression order (p):',
                      gui.spin(None, self, 'p', 0, 100, **kwargs))
        layout.addRow('Differencing degree (d):',
                      gui.spin(None, self, 'd', 0, 2, **kwargs))
        layout.addRow('Moving average order (q):',
                      gui.spin(None, self, 'q', 0, 100, **kwargs))
        layout.addRow('Seasonal Auto-regression order (P):',
                      gui.spin(None, self, 's_p', 0, 100, **kwargs))
        layout.addRow('Seasonal Differencing degree (D):',
                      gui.spin(None, self, 's_d', 0, 2, **kwargs))
        layout.addRow('Seasonal Moving average order (Q):',
                      gui.spin(None, self, 's_q', 0, 100, **kwargs))
        layout.addRow('Seasonality order (s):',
                      gui.spin(None, self, 's_s', 0, 100, **kwargs))


    def forecast(self, model):
        return model.predict(self.forecast_steps,
                             exog=self.exog_data,
                             alpha=1 - self.forecast_confint / 100,
                             as_table=True)

    def create_learner(self):
        return MY_ARIMA((self.p, self.d, self.q),(self.s_p,self.s_d,self.s_q,self.s_s), self.exog_data is not None)


if __name__ == "__main__":
    data = Timeseries.from_file('airpassengers')
    domain = Domain(data.domain.attributes[:-1], data.domain.attributes[-1])
    data = Timeseries.from_numpy(domain, data.X[:, :-1], data.X[:, -1])
    WidgetPreview(OWSARIMAModel).run(set_data=data)
