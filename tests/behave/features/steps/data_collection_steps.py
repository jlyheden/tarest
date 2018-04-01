from behave import *
from expects import *
import vcr

from tarest.utils import get_historical_data
from tarest.domain import Quote

my_vcr = vcr.VCR(path_transformer=vcr.VCR.ensure_suffix('.yaml'))


@given(u'the ticker {ticker}')
def step_impl(context, ticker):
    context.ticker = ticker


@when(u'I ask Yahoo Finance for historical data between {start} and {end}')
def step_impl(context, start, end):
    with my_vcr.use_cassette('tests/behave/cassettes/{}_{}.yaml'.format(start, end)):
        context.response_raw = get_historical_data(context.ticker, start=start, end=end)


@when(u'I store the historical data in the database')
def step_impl(context):
    Quote.from_yahoo_csv(context.ticker, context.response_raw)


@then(u'I can query the stored data')
def step_impl(context):
    res = Quote.query.all()
    context.response_length = len(res)


@then(u'I get {num} records back')
def step_impl(context, num):
    expect(context.response_length).to(be(int(num)))
