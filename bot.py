import os
import alpaca_trade_api as tradeapi
import time
import datetime
from datetime import timedelta
from pytz import timezone

tz = timezone('EST')

api = tradeapi.REST(os.environ.get('KEY_ID'), 
                    os.environ.get('SECRET_KEY'), 
                    'https://paper-api.alpaca.markets')

def check_current_order():
    orders = api.list_orders(status='open')
    return len(orders) >= 1

def time_to_open(current_time):
    if current_time.weekday() <= 4:
        d = (current_time + timedelta(days=1)).date()
    else:
        days_to_mon = 0 - current_time.weekday() + 7
        d = (current_time + timedelta(days=days_to_mon)).date()
    next_day = datetime.datetime.combine(d, datetime.time(9, 30, tzinfo=tz))
    seconds = (next_day - current_time).total_seconds()
    return seconds

def send_order(symbol):
    while True:
        # Checks if it is currently a weekday
        if datetime.datetime.now(tz).weekday() >= 0 and datetime.datetime.now(tz).weekday() <= 4:
            # Checks if the market is open
            if datetime.datetime.now(tz).time() > datetime.time(9, 30) and datetime.datetime.now(tz).time() <= datetime.time(15, 30):
                print('Market open ({})'.format(datetime.datetime.now(tz)))
                symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
                symbol_price = symbol_bars[symbol]['close']
                if not check_current_order():
                    api.submit_order(
                        symbol=symbol,
                        qty=1,
                        side='buy',
                        type='market',
                        time_in_force='gtc',
                        order_class='bracket',
                        stop_loss={'stop_price': symbol_price * 0.95},
                        take_profit={'limit_price': symbol_price * 1.05}
                    )
                    print('Order submitted')
                time.sleep(60)
            else:
                # Sleeps until market is open
                print('Market closed ({})'.format(datetime.datetime.now(tz)))
                print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
                time.sleep(time_to_open(datetime.datetime.now(tz)))
        else:
            # Sleeps until market is open
            print('Market closed ({})'.format(datetime.datetime.now(tz)))
            print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
            time.sleep(time_to_open(datetime.datetime.now(tz)))

send_order('SPY')