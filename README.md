# Cryptofolio
### Your cryptocurrency portfolio! 

<div style="text-align: center;" align="center">
<a href="https://cryptofolio.herokuapp.com/">
    <img src="/docs/logo.png" width="200">
</a>
<p>Available at https://cryptofolio.herokuapp.com/ </p>
</div>

[![Build Status](https://travis-ci.org/msantl/cryptofolio.svg?branch=master)](https://travis-ci.org/msantl/cryptofolio)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Usage
<b>Cryptofolio</b> has four main pages. The home page, settings page,
exchange page and user profile page.

### Home 
<img src="/docs/home.png" width="600">

Home screen takes the current state in the cryptomarket and shows you how much
are your cryptocurrency holdings worth at the given time.

The refresh button updates balances from all exchanges you have configured.

### Settings
<img src="/docs/settings.png" width="600">

Settings screen has two sections, Exchange settings and User settings.
Exchange settings allow you to add API key, secret, and passphrase for an
exchange that is available in Crypofolio. 

User settings allow you to change your details and your password.

### User Profile
<img src="/docs/user_profile.png" width="600">

In User Profile settings you can change your first and last name, and the
preffered FIAT currency.

Cryptofolio will use this to summarize your holdings.

### Exchange
<img src="/docs/exchange.png" width="600">

Exchange Settings allow you to add/update API key, secret, and passphrase and
to remove the exchange together with all the balances.


## Building From Source

### OS X and Linux

Dependencies:
* `python`
* `pip`
* `mysql`
* `bower` 

Since this is a `django` project I encourage you to use `virtualenv` and
`virtualenvwrapper`.

If you're using a `Linux` distribution, you'll need to run 
`sudo apt-get install libmariadbclient-dev` if you're running `mariadb` or
`sudo apt-get install libmysqlclient-dev` otherwise.

Install all `python` dependencies using `pip install -r requirements.txt`.

Once you checkout this repository, you need to setup some environment
variables.

Crpytofilo uses:
* `sendgrid` as an email backend, so if you want to do the same, you
need to create an account there and obtain the `sendgrid` API key.

* `sentry` for error tracking.  If you want to track all the errors by either
heroku slug commit or git commit hash, create an account there and get your
`sentry` data source name (DSN).


Environment variables:
* `SECRET_KEY`
* `SENDGRID_API_KEY`
* `FIELD_ENCRYPTION_KEY`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `DB_HOST`
* `DB_PORT`
* `SENTRY_DSN`

Once you've set up those variables you can start setting up some base project
settings.

This step is optional since all the bower dependencies are part of the repo,
but you can collect all the dependencies with: `python manage.py bower install`

After that, in order to serve the static files, you need to put them in a
folder where they will be served from. This is done with: `python manage.py collectstatic --noinput` 

Make sure you have a local `mysql` server running. You should also create a
database with the same name as the it is in environment variable `DB_NAME`.

Once you've setup your local `mysql` server, run `python manage.py migrate`.
This will create all the necessary tables in the database.

Setting up a django superuser is not necessary, but it's convenient. You can do
that with: `python manage.py createsuperuser`.

Now you're ready to launch the app locally: `python manage.py runserver`
The app should be served from `localhost:8000`.

Open up the admin console at `localhost:8000/admin` and create new entries for
`Currency` and `Exchange`. Those tables are used to list all supported FIAT
currencies and Exchanges. So go ahead and add `USD` and `EUR` in `Currency`
table, and `Binance`, `Bittrex`, `Coinbase`, `GDAX`, `Liqui` and `Poloniex` in
`Exchange` table.

Now you're ready to use <b>Cryptofolio</b> locally! 
