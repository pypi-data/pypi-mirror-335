import numpy as np
import math
from scipy.signal import argrelextrema

from AnyQt.QtCore import Qt
import pyqtgraph as pg

from orangecontrib.timeseries.widgets.owperiodbase import OWPeriodBase
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview

from Orange.widgets import gui
from orangecontrib.timeseries import Timeseries

#from orangecontrib.timeseries import (
#    Timeseries, autocorrelation, partial_autocorrelation)

def _significant_acf(corr, has_confint):
    if has_confint:
        corr, confint = corr

    periods = argrelextrema(np.abs(corr), np.greater, order=3)[0]
    num = (len(corr))
    periods = np.arange(num)
    corr = corr[periods]
    if has_confint:
        confint = confint[periods]

    result = np.column_stack((periods, corr))
    if has_confint:
        result = (result, np.column_stack((periods, confint)))
    return result

def autocorrelation(x, *args, nlags=None, fft=True, **kwargs):
    """
    Return autocorrelation function of signal `x`.

    Parameters
    ----------
    x: array_like
        A 1D signal.
    nlags: int
        The number of lags to calculate the correlation for (default .9*len(x))
    fft:  bool
        Compute the ACF via FFT.
    args, kwargs
        As accepted by `statsmodels.tsa.stattools.acf`.

    Returns
    -------
    acf: array
        Autocorrelation function.
    confint: array, optional
        Confidence intervals if alpha kwarg provided.
    """
    from statsmodels.tsa.stattools import acf
    if nlags == 0:
#        nlags = int(.9 * len(x))
        nlags = int(10 * math.log10(len(x)))
    corr = acf(x, *args, nlags=nlags, fft=fft, **kwargs)
    return _significant_acf(corr, kwargs.get('alpha'))


def partial_autocorrelation(x, *args, nlags=None, method='ldb', **kwargs):
    """
    Return partial autocorrelation function (PACF) of signal `x`.

    Parameters
    ----------
    x: array_like
        A 1D signal.
    nlags: int
        The number of lags to calculate the correlation for
        (default: min(len(x)//2 - 1, len(x) - 1))
    args, kwargs
        As accepted by `statsmodels.tsa.stattools.pacf`.

    Returns
    -------
    acf: array
        Partioal autocorrelation function.
    confint : optional
        As returned by `statsmodels.tsa.stattools.pacf`.
    """
    from statsmodels.tsa.stattools import pacf
    if nlags == 0:
        nlags = min(len(x)//2 - 1, len(x) - 1)
    corr = pacf(x, *args, nlags=nlags, method=method, **kwargs)
    return _significant_acf(corr, kwargs.get('alpha'))


class OWCorrelogram(OWPeriodBase):
    # TODO: allow computing cross-correlation of two distinct series
    name = 'Correlogram_mod'
    description = "Visualize variables' auto-correlation."
    icon = 'icons/Correlogram.svg'
    priority = 110
    lags = Setting(0)
    use_pacf = Setting(False)
    use_confint = Setting(True)

    yrange = (-1, 1)

    def __init__(self):
        super().__init__()
        gui.separator(self.controlArea)
        gui.spin(widget=self.controlArea, master=self, value='lags', minv=0, maxv=300, step=1, label="Lags:",
                 alignment=Qt.AlignRight, controlWidth=80, callback=self.replot)
        gui.checkBox(self.controlArea, self, 'use_pacf',
                     label='Compute partial auto-correlation',
                     callback=self.replot)
        gui.checkBox(self.controlArea, self, 'use_confint',
                     label='Plot 95% significance interval',
                     callback=self.replot)


    def acf(self, attr, lags,pacf, confint):
        key = (attr, pacf,lags, confint)
        if key not in self._cached:
            x = self.data.interp(attr).ravel()
            func = partial_autocorrelation if pacf else autocorrelation
            self._cached[key] = func(x, nlags=self.lags,alpha=.05 if confint else None)
        return self._cached[key]

    def replot(self):
        self.plot.clear()
        if not self.selection:
            return

        self.plot_widget.addItem(pg.InfiniteLine(0, 0, pen=pg.mkPen(0., width=2)))

        palette = self.get_palette()
        for i, attr in enumerate(self.selection):
            color = palette.value_to_qcolor(i)
            x, acf = np.array(self.acf(attr, self.lags,self.use_pacf, False)).T
            x = np.repeat(x, 2)
            y = np.vstack((np.zeros(len(acf)), acf)).T.flatten()
            item = pg.PlotCurveItem(
                x=x, y=y, connect="pairs", antialias=True,
                pen=pg.mkPen(color, width=5))
            self.plot_widget.addItem(item)

            if self.use_confint:
                # Confidence intervals, from:
                # https://www.mathworks.com/help/econ/autocorrelation-and-partial-autocorrelation.html
                # https://www.mathworks.com/help/signal/ug/confidence-intervals-for-sample-autocorrelation.html
                se = np.sqrt((1 + 2 * (acf ** 2).sum()) / len(self.data))
                #std = 1.96 * se
                std = 1.96 * se / np.sqrt(len(acf))
                color = palette.value_to_qcolor(i + 1)
                pen = pg.mkPen(color, width=2, style=Qt.DashLine)
                self.plot_widget.addItem(pg.InfiniteLine(std, 0, pen=pen))
                self.plot_widget.addItem(pg.InfiniteLine(-std, 0, pen=pen))


if __name__ == "__main__":
    WidgetPreview(OWCorrelogram).run(
        Timeseries.from_file("airpassengers")
    )
