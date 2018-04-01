import re
import requests
import json
import datetime


def yahoo_get(session, url):
    return session.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    })


def get_historical_data(symbol, start, end):
    start_timestamp = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%s')
    end_timestamp = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%s')

    session = requests.Session()

    resp = yahoo_get(session, f'https://finance.yahoo.com/quote/%5E{symbol}/history?p=%5E{symbol}')
    resp.raise_for_status()
    data = resp.content.decode('utf-8')
    crumb_m = re.search(r'"CrumbStore":\{"crumb":("[^"]+")\}', data)
    assert crumb_m
    crumb = json.loads(crumb_m.group(1))
    csvresp = yahoo_get(session,
        f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_timestamp}&period2={end_timestamp}&interval=1d&events=history&crumb={crumb}'
    )
    csvresp.raise_for_status()
    return csvresp.content
