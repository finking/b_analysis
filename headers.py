# Установка заголовков таблицы
from Gsheets import Gsheet

# Названия столбцов
names = ['Date', 'Spot_bids', 'Spot_ask','Coin_bids','Coin_asks','Maturity', 'Yield_period (%)', 'Yield_year (%)']

gs = Gsheet("ETHUSD")
gs.set_headers(names)






# for name, urls in dict_med.items():
#     if name == name_sheet:
#         gs.set_headers(urls)
#         gs.set_format()

