from tarest import app
from tarest.domain import Quote
from tarest.ta import timeseries_rsi14
from tarest.utils import get_historical_data
from flask.json import jsonify
import json


@app.route('/api/ta/rsi14/<ticker>')
def show_rsi14_for_ticker(ticker):
    quotes = Quote.query.filter_by(ticker=ticker).all()
    rsi14_result = timeseries_rsi14(quotes)
    return json.dumps(rsi14_result, default=str), 200


@app.route('/api/ta/rsi14/<ticker>/trend/<days>')
def show_rsi14_trend_for_ticker(ticker, days):
    quotes = Quote.query.filter_by(ticker=ticker).all()
    rsi14_result = timeseries_rsi14(quotes)
    trend = rsi14_result.trend(int(days))
    return json.dumps({
        "trend": trend
    }), 200


@app.route('/api/scrape/<ticker>/<from_date>/<to_date>')
def scrape_ticker(ticker, from_date, to_date):
    try:
        response = get_historical_data(ticker, from_date, to_date)
        Quote.from_yahoo_csv(ticker, response)
    except Exception as e:
        return json.dumps({"message": "failed to scrape", "exception": e}), 500
    else:
        return json.dumps({"message": "ok"}), 200


@app.route('/api/data/<ticker>/<days>')
def show_quotes(ticker, days):
    quotes = Quote.query.filter_by(ticker=ticker).order_by(Quote.date.desc()).limit(days).all()
    return jsonify([i.serialize for i in quotes]), 200