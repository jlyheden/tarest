from tarest import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
import datetime
import logging

LOG = logging.getLogger(__name__)


class Quote(db.Model):
    __table_args__ = (UniqueConstraint('ticker', 'date', name='unique_ticker_date'),)
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(50), nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<Quote {} {} {} {}>".format(self.ticker, self.date, self.open_price, self.close_price)

    @property
    def difference(self):
        return self.close_price - self.open_price

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'ticker': self.ticker,
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'difference': self.difference,
            'date': self.date.strftime("%Y-%m-%d")
        }

    @staticmethod
    def from_yahoo_csv(ticker, csv):
        for line in csv.splitlines():
            line_split = line.decode('utf-8').split(',')
            try:
                #if line_split[1] == line_split[2] == line_split[3] == line_split[4]:
                #    LOG.warning("All data columns contain the same data")
                #    continue
                date = datetime.datetime.strptime(line_split[0], '%Y-%m-%d')
                open_price = float(line_split[1])
                high_price = float(line_split[2])
                low_price = float(line_split[3])
                close_price = float(line_split[4])
                volume = float(line_split[6])
                db.session.add(Quote(ticker=ticker, open_price=open_price, high_price=high_price, low_price=low_price,
                                     close_price=close_price, volume=volume, date=date))
                db.session.flush()
            except IntegrityError as e:
                LOG.warning("Failed to update db")
                LOG.warning(e)
                db.session.rollback()
            except Exception as e:
                # this is pretty shitty, should catch more specific exception
                # or strip invalid lines from the data set before looping over it
                LOG.warning("Failed to serialise line: {}".format(",".join(line_split)))
                LOG.warning(e)
        db.session.commit()

    @staticmethod
    def from_params(**kwargs):
        db.session.add(Quote(**kwargs))
        db.session.commit()
