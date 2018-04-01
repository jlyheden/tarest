from behave import *
from expects import *
from expects.matchers import Matcher

from tarest.domain import Quote
from tarest.ta import calculate_sma, calculate_rsi14, timeseries_sma, timeseries_rsi14, timeseries_ema, calculate_macd
import datetime


class be_float(Matcher):
    """ custom behave float matcher """
    def __init__(self, expected):
        self._expected = expected

    def _match(self, request):
        import math
        if math.isclose(self._expected, request, rel_tol=1e-2):
            return True, ['float is equal']
        return False, ['float {} is not equal to {}'.format(self._expected, request)]


#
# behave steps
#

@given(u'some data set')
def step_impl(context):
    def to_datetime(d):
        return datetime.datetime.strptime(d, "%Y-%m-%d")
    for i in range(1, 11):
        ii = float(i)
        Quote.from_params(ticker="FAKE", open_price=ii, high_price=ii, low_price=ii, close_price=ii,
                          date=to_datetime("2015-01-{}".format(str(i).zfill(2))))


@when(u'I calculate SMA 10 day average on the data set')
def step_impl(context):
    context.result = calculate_sma("FAKE", 10)


@then(u'I get a value of {value}')
def step_impl(context, value):
    float_value = float(value)
    expect(context.result).to(be_float(float_value))


@when(u'I calculate RSI 14 on the data set')
def step_impl(context):
    context.result = calculate_rsi14(context.ticker)


@when(u'I calculate SMA 10 into time series')
def step_impl(context):
    data_set = Quote.query.filter_by(ticker=context.ticker).all()
    context.result = timeseries_sma(data_set, 10)


@then(u'I get the last value of {value}')
def step_impl(context, value):
    expect(context.result[-1]["value"]).to(be_float(float(value)))


@when(u'I calculate RSI14 into time series')
def step_impl(context):
    data_set = Quote.query.filter_by(ticker=context.ticker).all()
    context.result = timeseries_rsi14(data_set)
    # some plotting testing
    # import matplotlib.pyplot as plt
    # x = []
    # y = []
    # for (i, item) in enumerate(context.result):
    #     x.append(i)
    #     y.append(item["value"])
    # plt.plot(x, y)
    # plt.show()


@when(u'I calculate the trend based on 10 days')
def step_impl(context):
    context.result = context.result.trend(10)


@when(u'I calculate EMA10 into time series')
def step_impl(context):
    data_set = Quote.query.filter_by(ticker=context.ticker).all()
    context.result = timeseries_ema(data_set, 10)
    print(context.result)


@when(u'I calculate MACD with short EMA {short}, long EMA {long} and signal EMA {signal}')
def step_impl(context, short, long, signal):
    data_set = Quote.query.filter_by(ticker=context.ticker).all()
    macd_result = calculate_macd(data_set, int(short), int(long), int(signal))
    context.result = macd_result.get_macd_signal_series()
    print(context.result)
