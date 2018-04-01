from tarest.domain import *
import logging

LOG = logging.getLogger(__name__)


class TimeSeriesResult(tuple):

    def trend(self, days):
        items = self[-days:]
        half = int(days / 2)
        first = sum(x["value"] for x in items[:half])
        second = sum(x["value"] for x in items[half:])
        return (first / second) - 1


class MacdResult(object):

    def __init__(self, macd, signal):
        self.macd = macd
        self.signal = signal

    def get_macd_signal_series(self):
        timeseries = []
        for (m, s) in zip(self.macd, self.signal):
            timeseries.append({
                "date": m["date"],
                "value": m["value"] - s["value"]
            })
        return TimeSeriesResult(timeseries)


# TODO: Refactor
def calculate_sma(ticker, duration):
    response = Quote.query.filter_by(ticker=ticker).order_by(Quote.date).limit(duration).all()
    return sum([x.close_price for x in response]) / duration


# TODO: Kill
def calculate_rsi14(ticker):
    # from http://cns.bu.edu/~gsc/CN710/fincast/Technical%20_indicators/Relative%20Strength%20Index%20(RSI).htm
    response = Quote.query.filter_by(ticker=ticker).order_by(Quote.date).limit(14).all()
    avg_gain = sum([x.difference for x in response if x.difference > 0]) / 14
    avg_loss = sum([-x.difference for x in response if x.difference < 0]) / 14
    rs = avg_gain / avg_loss
    rsi14 = 100 - (100 / (1 + rs))
    return rsi14


def calculate_macd(quotes, short_period, long_period, signal_period):
    """
    Algo: http://investexcel.net/how-to-calculate-macd-in-excel/

    :param quotes: list of quotes
    :type quotes: list
    :param short_period: short ema period
    :type short_period: int
    :param long_period: long ema period
    :type long_period: int
    :param signal_period: signal ema period
    :type signal_period: int
    :return: macd result object
    :rtype: MacdResult
    """

    # this is flawed, these lists will not be the same size since the period
    # length decides how much data must be aggregated before series can be generated
    # basically the longest period length should decide how many elements should be popped
    # or if we add another optional field to timeseries_ema like skip_series_until=long_period
    short_ema = timeseries_ema(quotes, short_period, skip_until=long_period)
    long_ema = timeseries_ema(quotes, long_period)

    # calculating the signal and macd is a bit more convoluted
    timeseries_macd = []
    timeseries_signal = []
    macds = []
    signal = None
    multiplier = (2 / (signal_period + 1))
    for i, (short, long) in enumerate(zip(short_ema, long_ema)):
        macd = short["value"] - long["value"]
        if i == signal_period:
            signal = sum(macds) / signal_period
        elif i > signal_period:
            signal = (macd * multiplier) + (signal * (1 - multiplier))
        else:
            macds.append(macd)
        if signal is not None and i >= long_period:
            timeseries_macd.append({
                "date": short["date"],
                "value": macd
            })
            timeseries_signal.append({
                "date": short["date"],
                "value": signal
            })
    return MacdResult(timeseries_macd, timeseries_signal)


def timeseries_ema(quotes, period, skip_until=None):
    """
    Calculates Exponential Moving Average over period and returns a time series result

    :param quotes: list of quotes
    :type quotes: list
    :param period: aggregation period
    :type period: int
    :param skip_until: ignore series until this index has been enumerated
    :type skip_until: int
    :return: time series result
    :rtype: TimeSeriesResult
    """
    timeseries = []
    close_prices = []
    ema = None
    multiplier = (2 / (period + 1))
    for (i, quote) in enumerate(sorted(quotes, key=lambda x: x.date)):
        if i == period:
            ema = sum(close_prices) / period
        elif i > period:
            ema = (quote.close_price * multiplier) + (ema * (1 - multiplier))
        else:
            close_prices.append(quote.close_price)
        if ema is not None:
            if skip_until is None or i >= skip_until:
                timeseries.append({
                    "date": quote.date,
                    "value": ema
                })
    return TimeSeriesResult(timeseries)


def timeseries_sma(quotes, duration):
    """
    Calculates Simple Moving Average over duration and returns a time series result

    :param quotes: list of quotes
    :type quotes: list
    :param duration: duration in days on which average should be calculated
    :type duration: int
    :return: time series
    :rtype: TimeSeriesResult
    """
    timeseries = []
    close_prices = []
    for (i, quote) in enumerate(sorted(quotes, key=lambda x: x.date)):
        close_prices.append(quote.close_price)
        if i >= duration:
            close_prices.pop(0)
            timeseries.append({
                "date": quote.date,
                "value": sum(close_prices) / duration
            })
    return TimeSeriesResult(timeseries)


def timeseries_rsi14(quotes):
    """
    Calculates RSI 14 on list of quotes and returns a time series result

    :param quotes: list of quotes
    :type quotes: list
    :return: time series
    :rtype: TimeSeriesResult
    """
    timeseries = []
    differences = []
    rsi = None
    gain_avg = 0
    loss_avg = 0
    for (i, quote) in enumerate(sorted(quotes, key=lambda x: x.date)):
        if i == 13:
            gain_avg = sum([x for x in differences if x > 0]) / 14
            loss_avg = sum([-x for x in differences if x < 0]) / 14
            if loss_avg == 0:
                rsi = 100
            else:
                rs = gain_avg / loss_avg
                rsi = 100 - (100 / (1 + rs))
        elif i > 13:
            positive_diff = quote.difference if quote.difference > 0 else 0
            negative_diff = -quote.difference if quote.difference < 0 else 0
            gain_avg = ((gain_avg * 13) + positive_diff) / 14
            loss_avg = ((loss_avg * 13) + negative_diff) / 14
            if loss_avg == 0:
                rsi = 100
            else:
                rs = gain_avg / loss_avg
                rsi = 100 - (100 / (1 + rs))
        else:
            differences.append(quote.difference)
        if rsi is not None:
            timeseries.append({
                "date": quote.date,
                "value": rsi
            })
    return TimeSeriesResult(timeseries)
