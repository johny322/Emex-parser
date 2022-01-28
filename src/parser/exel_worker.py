import os

import pandas as pd


class Excel:
    def create_writer(self, path):
        """
        Создает writer для работы с листами экселя

        :param path: путь для сохранения будущего файла
        """
        self.writer = pd.ExcelWriter(path)

    def add_to_sheet(self, sheet_name):
        """
        Создает df из self.data и добавляет его на лист sheet_name.
        После добавления надо задать начальное значение self.data для сохранения на другие листы.

        :param sheet_name: имя листа в экселе
        :return:
        """
        self.check_data()
        df = pd.DataFrame(self.data)
        df.to_excel(self.writer, sheet_name=sheet_name, index=False)

    def writer_save(self):
        """
        Сохраняет файл с помощью writer по пути path из метода self.create_writer(path)
        """
        self.writer.save()

    def set_data(self, data):
        self.data = data

    def set_main_key(self, main_key):
        self.main_key = main_key

    def add_several_values(self, values: list, name: str):
        """
        Добавляет значения из массива в столбцы с названием и порядковым номером.

        Пример:

        add_several_values(['value1', 'value2', 'value3', 'name']
        Добавится в столбцы name1 - value1, name2 - value2, name3 - value3, если их не было, они создадутся.

        :param values: массив значений
        :param name: имя столбца для добавления
        """
        keys = list(self.data.keys())
        p_key = []
        for k in keys:
            if name in k:
                p_key.append(k)
        if len(values) >= len(p_key):
            for i in range(len(p_key) + 1, len(values) + 1):
                self.data[f'{name}{i}'] = [None] * (len(self.data[self.main_key]) - 1)
            for i in range(len(values)):
                self.data[f'{name}{i + 1}'].append(values[i])
        else:
            for i in range(len(values)):
                if f'{name}{i + 1}' not in self.data:
                    self.data[f'{name}{i + 1}'] = [None] * (len(self.data[self.main_key]) - 1)
                self.data[f'{name}{i + 1}'].append(values[i])
            for i in range(len(values) + 1, len(p_key) + 1):
                if f'{name}{i}' not in self.data:
                    self.data[f'{name}{i}'] = [None] * (len(self.data[self.main_key]) - 1)
                self.data[f'{name}{i}'].append(None)

    def add_key_value(self, key, value):
        """
        Добавляет значение в колонку по ключу.

        :param key: ключ для колонки
        :param value: значение для добавлния
        """
        keys = list(self.data.keys())
        if key in keys:
            difference = len(self.data[self.main_key]) - len(self.data[key])
            if difference > 1:
                self.data[key].extend([None] * (difference - 1))
            # if difference < 0:
            #     self.add_several_values([value], key)
            # if difference - 1 < 0 and key != self.main_key:
            #     self.add_several_values([value], key)
            self.data[key].append(value)
        else:
            self.data[key] = [None] * (len(self.data[self.main_key]) - 1)
            self.data[key].append(value)

    def check_data(self):
        """
        Проверяет данные, чтобы в каждом столбце было одинаковое количество значений, если не так, то добавит None.

        """
        keys = list(self.data.keys())
        main_len = len(self.data[self.main_key])
        for key in keys:
            key_len = len(self.data[key])
            diff = main_len - key_len
            if diff > 0:
                self.data[key].extend([None] * diff)
            if diff < 0:
                self.data[key] = self.data[key][:diff]

    def write_exel(self, path, beautiful=(False, 'max')):
        """
        Записывает файл по пути.

        :param beautiful:
        :param path: путь для записи (some_path.xlsx)
        :return: абсолютный путь до файла
        """
        self.check_data()
        df = pd.DataFrame(self.data)
        if beautiful[0]:
            bt_type = beautiful[1]
            writer = pd.ExcelWriter(path)
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            for column in df:
                if bt_type == 'max':
                    column_width = max(df[column].astype(str).map(len).max(), len(column))
                else:
                    column_width = len(column) + 5
                col_idx = df.columns.get_loc(column)
                writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)
            writer.save()
        else:
            df.to_excel(path, index=False)
        return os.path.abspath(path)

    def get_df(self):
        self.check_data()
        df = pd.DataFrame(self.data)
        return df

    @staticmethod
    def close_excel_by_name(name):
        return os.system(f'taskkill /FI "WindowTitle eq {name}*" /F')

    @staticmethod
    def beautiful_exel(open_path, save_path, sheet_name='Sheet1', bt_type='max'):
        """
        

        :param open_path:
        :param save_path:
        :param sheet_name:
        :param bt_type:
        :return:
        """
        df = pd.read_excel(open_path)
        writer = pd.ExcelWriter(save_path)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        for column in df:
            if bt_type == 'max':
                column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
            else:
                column_width = len(column) + 5
            col_idx = df.columns.get_loc(column)
            writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)
        writer.save()
        return os.path.abspath(save_path)

    @staticmethod
    def concat_files(files: list, final_name: str, drop_duplicates: bool = False, subset=''):
        con_files = []
        for file in files:
            con_files.append(pd.read_excel(file))
        df = pd.concat(con_files, ignore_index=True)
        if drop_duplicates:
            df = df.drop_duplicates(subset=subset, keep='first')
        df.to_excel(final_name, index=False)
        return os.path.abspath(final_name)

