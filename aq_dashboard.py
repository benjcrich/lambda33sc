"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
import openaq
from flask_sqlalchemy import SQLAlchemy

api = openaq.OpenAQ()

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '(datetime ' + self.datetime + ' )(value ' + str(
            self.value) + ' )'


def get_results():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    date_value = [(body.get('results')[n].get('date').get('utc'),
                   body.get('results')[n].get('value')) for n in
                  range(0, 100)]

    ret_string = ''
    for s in date_value:
        ret_string = ret_string + '(' + s[0] + ' , ' + str(
            s[1]) + ')<br />'
        vals = Record()
        vals.datetime = s[0]
        vals.value = s[1]
        DB.session.add(vals)
    DB.session.commit()
    return ret_string


@APP.route('/')
def root():
    ret_str = ''
    data = Record.query.filter(Record.value >= 10).all()

    for s in data:
        ret_str = ret_str + str(s) + '<br />'
    return '<body>' + ret_str + '</body>'


@APP.route('/pull')
def data_pull():
    """Base view."""
    return get_results()


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    DB.session.commit()
    return 'Data refreshed!'
