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
manual balance entry page, exchange page and user profile page.

### Home
<img src="/docs/home.png" width="600">

Home screen takes the current state in the cryptomarket and shows you how much
are your cryptocurrency holdings worth at the given time.

Your data is shown in one table and two graphs.
The table shows how much of each cryptocurrency you hold and it's current value
in fiat.
The first graph is a piechart, which is a graphical representation of the table
in the form of a piechart.
The second graph is a historical time series graph, which shows how your
holdings converted into fiat over time.

### Settings
<img src="/docs/settings.png" width="600">

Settings screen has two sections, Exchange settings and User settings.
Exchange settings allow you to add API key, secret, and passphrase for an
exchange that is available in Crypofolio.

User settings allow you to change your details and your password.
The Refresh All button will refresh balances from all exchanges that you've
configured, and the Remove All button will remove all balances and API keys,
secrets and passphrase from your profile.

### User Profile
<img src="/docs/user_profile.png" width="600">

In User Profile settings you can change your first and last name, and the
preffered FIAT currency.

Cryptofolio will use this to summarize your holdings.

### Address Entry
<img src="/docs/address.png" width="600">

In Address Entry you can enter cryptocurrency and address pairs (ETH or BTC at
the moment) if you have any offline wallets and you want to keep track of those
funds also.

The amount will show just as if the data was pulled from an exchange, and it
will be included in your summary.

### Manual Balance Entry
<img src="/docs/manual.png" width="600">

In Manual Balance Entry you can enter cryptocurrency that you hold offline or
are uncomfortable syncing with Crpytofilo by an exchange.

The amount will show just as if the data was pulled from an exchange, and it
will be included in your summary.

### Exchange
<img src="/docs/exchange.png" width="600">

Exchange Settings allow you to add/update API key, secret, and passphrase and
to remove the exchange together with all the balances.


## Building From Source

### OS X and Linux

Dependencies:
* `python3`
* `pip3`
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

* `etherscan.io` to get balance for an ETH address. If you want to send API
requests you need to create an accont and obtain an API key.

* `blockchain.info` to get balance for a BTC address. If you want to send API
requests you need to create an accont and obtain an API key.

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
* `ETHERSCAN_API_KEY`

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
and crypto currencies, and Exchanges. So go ahead and add `USD` and `EUR`
with unchecked `crypto` checkbox, and `BTC`, `ETC`, `LTC` with checked `crypto`
checkbox in `Currency` table, and `Binance`, `Bittrex`, `Coinbase`, `GDAX`,
`Kraken`, `Liqui` and `Poloniex` in `Exchange` table.

`TimeSeries` and `BalanceTimeSeries` tables are supposed to be populated by a
cronjob that runs `python manage.py update_balances` every hour.

Now you're ready to use <b>Cryptofolio</b> locally!
