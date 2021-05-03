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
maturities = ['210625', '210924']
day_in_year = 365
min_lot = 1
price_range = 3  # количество знаков после запятой в цене.
qty_range = 6  # количество знаков после запятой в кол-ве.
spot_symbols = ['ETHUSD', 'LTCUSD', 'LINKUSD', 'ADAUSD', 'DOTUSD', 'BCHUSD', 'XRPUSD', 'BTCUSD']
client = Client(api_key, api_secret)


def main():
    for spot_symbol in spot_symbols:
        coin_futures_symbol_near = f'{spot_symbol}_{maturities[0]}'  # ближний фьючерс
        coin_futures_symbol_further = f'{spot_symbol}_{maturities[1]}'  # дальний фьючерс
        # Книга заявок для спотового рынка
        print(f"Загрузка котировок для {spot_symbol}")
        try:
            spot_order_book = client.get_order_book(symbol=spot_symbol+'T')
            spot_best_price = get_best_price(spot_order_book)
            print(f'Лучшая цена спота на покупку: {spot_best_price["bids"]}')
            print(f'Лучшая цена спота на продажу: {spot_best_price["asks"]}')
        except Exception as e:
            print(e)

        # Книга заявок для фьючерсов с базой в coin
        try:
            coin_best_price_near = get_coin_futures_price(coin_futures_symbol_near, 'ближнего')
            coin_best_price_further = get_coin_futures_price(coin_futures_symbol_further, 'дальнего')
        except Exception as e:
            print(e)

        # Вычисление количество дней до экспирации
        period_near = get_period(maturities[0])
        period_further = get_period(maturities[1])

        # Вычисление доходности за период
        try:
            yield_period_near = round(((coin_best_price_near["bids"] / spot_best_price["asks"]) - 1) * 100, 2)
            yield_year_near = round(yield_period_near / period_near * day_in_year, 2)

            yield_period_further = round(((coin_best_price_further["bids"] / spot_best_price["asks"]) - 1) * 100, 2)
            yield_year_further = round(yield_period_further / period_further * day_in_year, 2)

            data = {'time': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    'spot_bids': spot_best_price["bids"],
                    'spot_ask': spot_best_price["asks"],
                    'coin_bids_near': coin_best_price_near["bids"],
                    'coin_asks_near': coin_best_price_near["asks"],
                    'period_near': period_near,
                    'yield_period_near': yield_period_near,
                    'yield_year_near': yield_year_near,
                    'space': '',
                    'coin_bids_further': coin_best_price_further["bids"],
                    'coin_asks_further': coin_best_price_further["asks"],
                    'period_further': period_further,
                    'yield_period_further': yield_period_further,
                    'yield_year_further': yield_year_further,
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


def get_coin_futures_price(coin_futures_symbol, name):
    coin_order_book = client.futures_coin_order_book(symbol=coin_futures_symbol)
    # TODO разобраться как поменять cont (1 = 10USD) на coin (например на ETH)
    coin_best_price = get_best_price(coin_order_book)
    print(f'Лучшая цена {name} фьючерса Coin на покупку: {coin_best_price["bids"]}')
    print(f'Лучшая цена {name} фьючерса Coin на продажу: {coin_best_price["asks"]}')
    return coin_best_price


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
                        data['coin_bids_near'],
                        data['coin_asks_near'],
                        data['period_near'],
                        data['yield_period_near'],
                        data['yield_year_near'],
                        data['space'],
                        data['coin_bids_further'],
                        data['coin_asks_further'],
                        data['period_further'],
                        data['yield_period_further'],
                        data['yield_year_further'],
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
