# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
import io
import pandas as pd
import matplotlib.pyplot as plt
import os
import random
from io import StringIO
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import pickle
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User

from app.base.util import verify_pass
model = pickle.load(open("model1.pkl", 'rb'))
test_store = pickle.load(open("test_store.pkl", 'rb'))
#train_store = pickle.load(open("train_store.pkl", 'rb'))
test_features =['Store', 'CompetitionDistance', 'Promo', 'Promo2', 'SchoolHoliday', 'StoreType',
    'Assortment', 'StateHoliday', 'DayOfWeek', 'Month', 'Day', 'Year', 'WeekOfYear', 'Weekend', 'Weekday',
    'NumDaysToHoliday', 'NumDaysAfterHoliday',
    'PosInMonth', 'CompetitionOpen', 'PromoOpen', 'IsPromoMonth']

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'login/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'login/register.html', msg='Username already registered', form=create_account_form)

        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'login/register.html', msg='Email already registered', form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'login/register.html', success='User created please <a href="/login">login</a>', form=create_account_form)

    else:
        return render_template( 'login/register.html', form=create_account_form)

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))
##@blueprint.route('/plot.png')
#def plot_png():

        #fig = Figure()
        #axis = fig.add_subplot(1, 1, 1)

        #xs = range(100)
        #ys = [random.randint(1, 50) for x in xs]

        #axis.plot(xs, ys)
        #canvas = FigureCanvas(fig)
        #output = StringIO.StringIO()
        #canvas.print_png(output)
        #response = make_response(output.getvalue())
        #response.mimetype = 'image/png'
          #lnprice=np.log(price)
              #
              #return send_file(img, mimetype='image/png')
        #return response


@blueprint.route('/plot.png')
def plot_png():
    type = request.args.get('type')
    if(type=='all'):
        fig = draw_all_stores()
    elif type == 'one':
        store_num = request.args.get('num')
        fig = draw_single_store(store_num)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def draw_single_store(store_num):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    print(test_store)

    X = test_store[test_store.Store == 1]

    X = test_store[test_features][test_store.Store == int(store_num)]
    y_preds = model.predict(X)
    data = {'y_preds': y_preds,
            'Dates': X.index.values
            }

    df = pd.DataFrame(data, columns = [ 'y_preds','Dates'])
    print(X)
    plt.figure(figsize=(12,19))
    df = df.set_index('Dates')
    df.plot(ax=axis)
    return fig
#def predict(year):

def draw_all_stores():
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        X2 = test_store[test_features]
        y_preds2 = model.predict(X2)

        cars = {'y_preds': y_preds2,
                'Dates': X2.index.values
                }

        df = pd.DataFrame(cars, columns = [ 'y_preds','Dates'])

        plt.figure(figsize=(10,8))

        df = df.groupby('Dates')['y_preds'].sum().plot(ax=axis)
        return fig
@blueprint.route('/allstores')
def json_all_stores():
                   X2 = test_store[test_features]
                   y_preds2 = model.predict(X2)

                   cars = {'y_preds': y_preds2,
                           'Dates': X2.index.values
                           }

                   df = pd.DataFrame(cars, columns = ['y_preds','Dates'])

                   plt.figure(figsize=(10,8))
                   df['Date'] = df['Dates'].values
                   print(df)
                   df = df.groupby('Dates')['y_preds'].sum()
                   df['Date'] = df.index.strftime('%Y/%m/%d')
                   print(df)
                   return dict(zip(df.Date,df.values))
@blueprint.route('/onestore')
def json_one_store():
                       store_num = request.args.get('num')
                       print('#####################################################################################'+store_num)
                       X = test_store[test_features][test_store.Store == int(store_num)]
                       y_preds = model.predict(X)
                       data = {'y_preds': y_preds,
                               'Dates': X.index.values
                               }

                       df = pd.DataFrame(data, columns = [ 'y_preds','Dates'])
                       #print(X)
                       plt.figure(figsize=(12,19))
                       df['Dates'] = df['Dates'].dt.strftime('%Y/%m/%d')
                       #df = df.set_index('Dates')
                       #print(df.y_preds)
                       return jsonify(dict(zip(df.Dates,df.y_preds)))

@blueprint.route('/bymonth')
def by_month(year):
    store_num = request.args.get('year')
    X = train_store[['Dates','Sales']][train_store.Year == int(year)]


    X2 = X.groupby('Month')['Sales'].sum()
    plt.figure(figsize=(12,19))

    return jsonify(dict(zip(X2.Month,X2.y_preds)))


























@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/page_403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/page_500.html'), 500
