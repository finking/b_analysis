from config_dev import *
from binance.client import Client
from datetime import datetime
import csv
from Gsheets import Gsheet

api_key = API_KEY
api_secret = API_SECRET
pathCSV = 'data/'
maturity = '210625'
day_in_year = 365
min_lot = 2
price_range = 3  # количество знаков после запятой в цене.
qty_range = 6  # количество знаков после запятой в кол-ве.
spot_symbol = 'ETHUSDT'
coin_futures_symbol = f'ETHUSD_{maturity}'
client = Client(api_key, api_secret)


def main():
    # Книга заявок для спотового рынка
    spot_order_book = client.get_order_book(symbol=spot_symbol)
    spot_best_price = get_best_price(spot_order_book)
    print(f'Лучшая цена спота на покупку: {spot_best_price["bids"]}')
    print(f'Лучшая цена спота на продажу: {spot_best_price["asks"]}')

    # Книга заявок для фьючерсов с базой в coin
    coin_order_book = client.futures_coin_order_book(symbol=coin_futures_symbol)
    # TODO разобраться как поменять cont (1 = 10USD) на coin (например на ETH)
    coin_best_price = get_best_price(coin_order_book)
    print(f'Лучшая цена фьючерса Coin на покупку: {coin_best_price["bids"]}')
    print(f'Лучшая цена фьючерса Coin на продажу: {coin_best_price["asks"]}')

    # Вычисление количество дней до экспирации
    maturity_date = datetime.strptime(maturity, "%y%m%d")
    delta = maturity_date - datetime.today()
    period = delta.days + 1

    # Вычисление доходности за период
    yield_period = round(((coin_best_price["bids"]/spot_best_price["asks"])-1)*100, 2)
    yield_year = round(yield_period/period*day_in_year,2)

    data = {'time': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            'spot_bids': spot_best_price["bids"],
            'spot_ask': spot_best_price["asks"],
            'coin_bids': coin_best_price["bids"],
            'coin_asks': coin_best_price["asks"],
            'period': period,
            'yield_period (%)': yield_period,
            'yield_year (%)': yield_year
            }

    # print(f"Запись в файл: {pathCSV}binance.csv")
    # write_csv(data)
    writeGoogleSheets("ETHUSD", data)


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


# def write_csv(data):
#     with open(f'{pathCSV}binance.csv', 'a', newline='', encoding='UTF-8') as f:
#         writer = csv.writer(f, delimiter=';')
#         writer.writerow([data['time'],
#                          data['spot_bids'],
#                          data['spot_ask'],
#                          data['coin_bids'],
#                          data['coin_asks'],
#                          data['period'],
#                          data['yield_period (%)'],
#                          data['yield_year (%)']])


# Запись в Гугл.Таблицы
def writeGoogleSheets(pair, data):
    sheet = Gsheet(pair)
    ws = sheet.worksheet
    try:
        ws.append_row([data['time'],
                         data['spot_bids'],
                         data['spot_ask'],
                         data['coin_bids'],
                         data['coin_asks'],
                         data['period'],
                         data['yield_period (%)'],
                         data['yield_year (%)']])
        print(f'Запись в Гугл.Таблицу по паре {pair} завершена успешна')
    except Exception as e:
        print(f'Запись в Гугл.Таблицу по {pair} не удалась')
        print(e)


if __name__ == '__main__':
    main()