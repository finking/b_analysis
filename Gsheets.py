import gspread

name_json = 'binance-analysis.json'
name_book = 'Binance_analysis'


class Gsheet:

    def __init__(self, name):
        self.gs = gspread.service_account(filename=name_json)
        self.book = self.gs.open(name_book)
        self.worksheet = self.book.worksheet(name)

    def set_format(self):
        self.worksheet.format('3:3', {'textFormat': {'bold': True},
                                        'horizontalAlignment': 'CENTER',
                                        'verticalAlignment': 'MIDDLE',
                                        # 'wrapStrategy': 'WRAP'
                              })
        self.worksheet.format('B4:G', {'numberFormat': {'type': 'NUMBER', 'pattern': '# ### ₽'}})
        self.worksheet.format('A4:A', {'numberFormat': {'type': 'DATE_TIME', 'pattern': 'dd-mm-yyyy hh:mm'}})

    def set_headers(self, names, row=3, col=1):
        try:
            for name in names:
                self.worksheet.update_cell(row, col, name)  # Заголовок у столбца А
                col = col + 1  # Устанавливаем следующий столбец
            print(f'Заголовки на листе "{self.worksheet.title}" установлены успешно')
        except Exception as e:
            print(f'Заголовки на листе "{self.worksheet.title}" не установлены. Ошибка: {e}')
