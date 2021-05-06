from config_dev import *
from binance.client import Client
from datetime import datetime
import csv
from Gsheets import Gsheet
import schedule
import time

api_key = API_KEY
api_secret = API_SECRET
pathCSV = 'data/'
maturity = '210625'
day_in_year = 365
min_lot = 1
price_range = 3  # количество знаков после запятой в цене.
qty_range = 6  # количество знаков после запятой в кол-ве.
spot_symbols = ['ETHUSDT', 'BTCUSDT']
client = Client(api_key, api_secret)


def main():
    for spot_symbol in spot_symbols:
        usdt_futures_symbol = f'{spot_symbol}_{maturity}'  # usdt фьючерс
        # Книга заявок для спотового рынка
        print(f"Загрузка котировок для {spot_symbol}")
        try:
            spot_order_book = client.get_order_book(symbol=spot_symbol)
            spot_best_price = get_best_price(spot_order_book)
            print(f'Лучшая цена спота на покупку: {spot_best_price["bids"]}')
            print(f'Лучшая цена спота на продажу: {spot_best_price["asks"]}')
        except Exception as e:
            print(e)

        # Книга заявок для фьючерсов с базой в coin
        try:
            usdt_best_price = get_futures_price(usdt_futures_symbol)
        except Exception as e:
            print(e)

        # Вычисление количество дней до экспирации
        period = get_period(maturity)
        # period_further = get_period(maturities[1])

        # Вычисление доходности за период
        try:
            yield_period = round(((usdt_best_price["bids"] / spot_best_price["asks"]) - 1) * 100, 2)
            yield_year = round(yield_period / period * day_in_year, 2)
            spread = round(((usdt_best_price["asks"] / usdt_best_price["bids"]) - 1) * 100, 2)

            data = {'time': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    'spot_bids': spot_best_price["bids"],
                    'spot_ask': spot_best_price["asks"],
                    'future_bids': usdt_best_price["bids"],
                    'future_asks': usdt_best_price["asks"],
                    'period': period,
                    'yield_period': yield_period,
                    'yield_year': yield_year,
                    'spread': spread
                    }
            write_google_sheets(spot_symbol, data)
        except Exception as e:
            print(f'Рачет доходности не удался! ERROR: {e}')
    print('Ожидание времени запуска скрипта')
        # print(f"Запись в файл: {pathCSV}binance.csv")
        # write_csv(data)


def get_period(maturity):
    maturity_date = datetime.strptime(maturity, "%y%m%d")
    delta = maturity_date - datetime.today()
    period = delta.days + 1
    return period


def get_futures_price(coin_futures_symbol):
    future_order_book = client.futures_order_book(symbol=coin_futures_symbol)
    future_best_price = get_best_price(future_order_book)
    print(f'Лучшая цена фьючерса на покупку: {future_best_price["bids"]}')
    print(f'Лучшая цена фьючерса на продажу: {future_best_price["asks"]}')
    return future_best_price


def get_best_price(order_book):
    list_best_price = {}
    for key, value in order_book.items():
        price = 0.00
        qty = 0.00
        if key == 'bids' or key == 'asks':
            for i in value:
                qty = qty + float(i[1])
                if qty > min_lot:
                    price = round(float(i[0]), price_range)
                    # print(f'price {key}: {price}, qty: {round(qty, qty_range)}')
                    break
            # Если пришедшее общее количество меньше минимального значения лота для торговли
            if qty < min_lot:
                print('Недостаточное количество для торговли')
                break
        list_best_price[f'{key}'] = price
    return list_best_price


# Запись в Гугл.Таблицы
def write_google_sheets(pair, data):
    sheet = Gsheet(pair)
    ws = sheet.worksheet
    try:
        ws.append_row([data['time'],
                        data['spot_bids'],
                        data['spot_ask'],
                        data['future_bids'],
                        data['future_asks'],
                        data['period'],
                        data['yield_period'],
                        data['yield_year'],
                        data['spread']
                       ])
        print(f'Запись в Гугл.Таблицу по паре {pair} завершена успешна')
    except Exception as e:
        print(f'Запись в Гугл.Таблицу по {pair} не удалась')
        print(e)


if __name__ == '__main__':
    schedule.every().hour.at(":00").do(main)
    print('Ожидание времени запуска скрипта')

    while True:
        schedule.run_pending()
        time.sleep(1)
