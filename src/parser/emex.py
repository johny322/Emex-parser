import json
import os
import re
import time
import traceback
import pandas as pd

import requests
import urllib.request

from fake_headers import Headers
from requests import ConnectTimeout, Timeout
from requests.exceptions import ProxyError

from src.gui.threads.gui_threads_loader import progress_bar_range_thread, progress_bar_value_thread, \
    warning_message_thread, info_label_thread
from src.parser.exel_worker import Excel
from src.parser.path import log_path


def get_proxy_from_file(limit: int, proxy_path):
    work_proxy = ''
    new_proxies = []
    with open(proxy_path) as file:
        proxies = file.readlines()

    pattern = '\d{1,}-'
    for proxy in proxies:
        if work_proxy:
            new_proxies.append(proxy)
            continue
        match = re.match(pattern, proxy)
        if match:
            current_limit = int(match[0].replace('-', ''))
            if current_limit >= limit:
                new_proxies.append(proxy)
                continue
            proxy = proxy.replace(match[0], f'{current_limit + 1}-')
        else:
            proxy = '1-' + proxy
        p = re.sub(pattern, '', proxy).strip()
        try:
            is_validity = check_proxy_validity(p)
        except:
            log_error(log_path)
            return ''
        if isinstance(is_validity, bool):
            work_proxy = p
        else:
            # text = f'Прокси {p} не подходят'
            info_label_thread.info_message = is_validity
            info_label_thread.start()
            # print(is_validity)
            proxy = f'{limit}-' + p + '\n'

        new_proxies.append(proxy)
    with open(proxy_path, 'w') as file:
        file.writelines(new_proxies)

    work_proxy = re.sub(pattern, '', work_proxy).strip()
    return work_proxy


def check_proxy_validity(proxy):
    proxies = {
        'http': f'http://{proxy.strip()}',
        'https': f'https://{proxy.strip()}'
    }
    try:
        requests.get('https://icanhazip.com/', proxies=proxies, timeout=2)
        return True
    except ConnectTimeout:
        message = f'Прокси {proxy} слишком медленные'
        return message
    except ProxyError:
        message = f'Не удалось подключится к прокси {proxy}'
        return message


def check_bright_data_proxy(proxy):
    proxies = {
        'http': proxy.strip(),
        'https': proxy.strip()
    }
    try:
        requests.get('http://lumtest.com/myip.json', proxies=proxies, timeout=3, verify=False)
        return True
    except Exception:
        log_error(log_path, "Ошибка при проверке прокси bright_data")
        return False


def get_bright_data_proxy(proxy_path):
    with open(proxy_path) as file:
        proxy = file.read()
    return proxy.strip()


def log_error(path, message=''):
    now = time.asctime()
    if message:
        text = f'{now}\n' \
               f'{message}\n' \
               f'{traceback.format_exc()}\n'
    else:
        text = f'{now}\n' \
               f'{traceback.format_exc()}\n'
    with open(path, 'a') as f:
        f.write(text)


class Emex:
    def __init__(self, settings: dict):
        self.settings = settings
        self.ex = Excel()
        self.proxy = ''
        self.main_key = 'Номер'
        self.ex.set_main_key(self.main_key)
        self.data = {
            self.main_key: [],
            'Бренд': [],
            'Наименование': [],
            'Поставщик': [],
            'Количество': [],
            'Цена': [],
            'Время доставки': []
        }
        self.ex.set_data(self.data)
        self.no_results_count = 0
        self.previous_no_results_index = -1
        self.create_opener_count = 0
        # self.start_time = time.time()

    def excel_iter(self, start_index=0):
        excel_path = self.settings['excel_path']
        save_path = self.settings['save_path']
        proxy_path = self.settings['proxy_path']
        df = pd.read_excel(excel_path)
        # print(df)
        if proxy_path:
            if self.settings['bright_data_proxy'] or self.settings['proxy_manager']:
                proxy = get_bright_data_proxy(proxy_path)
                if not check_bright_data_proxy(proxy):
                    if self.settings['proxy_manager']:
                        text = 'Не удалось подключиться к прокси\n' \
                               'Убедитесь, что Proxy Manager запущен. Проверьте порт'
                    else:
                        text = 'Не удалось подключиться к прокси\n' \
                               'Проверьте ссылку на прокси'
                    # print(text)
                    info_label_thread.info_message = text
                    info_label_thread.start()
                    time.sleep(1)
                    return
            else:
                proxy = get_proxy_from_file(1, proxy_path)
                if not proxy:
                    self.ex.check_data()
                    self.ex.write_exel(save_path, (True, 'max'))
                    info_label_thread.info_message = 'Прокси закончились'
                    info_label_thread.start()
                    warning_message_thread.text_message = 'Прокси закончились'
                    warning_message_thread.start()
                    return
        else:
            proxy = ''
        for column in df.columns:
            if column not in self.data:
                self.data[column] = []

        progress_bar_range_thread.max_value = len(df.index)
        progress_bar_range_thread.start()

        for index in df.index[start_index:]:
            num = df.iloc[index, 0]
            # print(num)

            url = f'https://emex.ru/api/search/search?detailNum={num}&locationId=29084&showAll=true' \
                  f'&longitude=37.617635&latitude=55.755814'
            json_data = self.get_json_data(url, proxy)
            if json_data is None:
                info_label_thread.info_message = f'Не удалось получить данные для {num}'
                info_label_thread.start()
                progress_bar_value_thread.start()
                continue
            try:
                # print(json_data)
                self.get_details(json_data,
                                 self.settings['providers'],
                                 self.settings['rating'],
                                 self.settings['with_analogs'],
                                 df.columns,
                                 df.iloc[index],
                                 index,
                                 num
                                 )
            except Exception:
                message = f'URL: {url}'
                log_error(log_path, message)
            finally:
                self.ex.check_data()
            progress_bar_value_thread.start()

            # if self.no_results_count > 5:
            #     # print(f'restart from {self.previous_no_results_index}')
            #     if self.settings['proxy_path']:
            #         # self.excel_iter(self.previous_no_results_index)
            #         pass
            #     else:
            #         info_label_thread.info_message = 'Блокировка\n' \
            #                                          'Завершение работы'
            #         info_label_thread.start()
            #         warning_message_thread.text_message = 'Блокировка'
            #         warning_message_thread.start()
            #         break
                # return
        # print(f'TIME: {time.time() - self.start_time}')
        try:
            self.ex.write_exel(save_path, (False, 'max'))
        except PermissionError:
            info_label_thread.info_message = 'Файл сохранения открыт. Закрытие...'
            info_label_thread.start()
            name = os.path.basename(save_path)
            self.ex.close_excel_by_name(name)
            time.sleep(4)
            try:
                self.ex.write_exel(save_path, (False, 'max'))
            except Exception:
                info_label_thread.info_message = 'Не удалось сохранить данные'
                info_label_thread.start()
                warning_message_thread.text_message = 'Не удалось сохранить данные. Вероятно открыт файл сохранения'
                warning_message_thread.start()
                log_error(log_path, 'Не удалось сохранить данные после закрытия файла')
        except Exception:
            info_label_thread.info_message = 'Не удалось сохранить данные'
            info_label_thread.start()
            warning_message_thread.text_message = 'Не удалось сохранить данные'
            warning_message_thread.start()
            log_error(log_path, 'Не удалось сохранить данные')

    def get_json_data(self, url, proxy=''):
        # headers = Headers(headers=True).generate()
        if self.settings['bright_data_proxy'] or self.settings['proxy_manager']:
            proxies = {
                "http": proxy.strip(),
                "https": proxy.strip()
            }
            try:
                # print(requests.get('http://lumtest.com/myip.json', proxies=proxies, timeout=3, verify=False).json())
                # try:
                #     ip = requests.get('http://lumtest.com/myip.json', proxies=proxies, timeout=3, verify=False).json().get('ip')
                #     info_label_thread.info_message = ip
                #     info_label_thread.start()
                # except Exception:
                #     info_label_thread.info_message = 'ip'
                #     info_label_thread.start()
                # r = requests.get(url, headers=headers, proxies=proxies, timeout=4, verify=False)
                r = requests.get(url, proxies=proxies, timeout=4, verify=False)
                self.create_opener_count = 0
                return r.json()
            except (ConnectTimeout, Timeout):
                # print('time')
                self.create_opener_count += 1
                if self.create_opener_count > 4:
                    self.create_opener_count = 0
                    return None
                return self.get_json_data(url, proxy)
            except Exception as e:
                if 'time' in str(e):
                    self.create_opener_count += 1
                    if self.create_opener_count > 4:
                        self.create_opener_count = 0
                        log_error(log_path, "time in exception")
                        return None
                    return self.get_json_data(url, proxy)
                else:
                    # traceback.print_exc()
                    log_error(log_path)
                    return None
        else:
            try:
                if proxy:
                    proxies = {
                        "http": f"http://{proxy.strip()}",
                        "https": f"https://{proxy.strip()}",
                    }
                    r = requests.get(url, proxies=proxies, timeout=2)
                else:
                    r = requests.get(url, timeout=2)
                return r.json()
            except (ConnectTimeout, Timeout):
                return None
            except Exception:
                log_error(log_path)
                return None

    def get_data(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def get_details(self, json_data, providers: list, rating: list, with_analogs: bool, columns, values, index, num):
        search_result = json_data['searchResult']
        no_results = search_result['noResults']
        makes = search_result.get('makes', None)
        if no_results or makes is None:
            info_label_thread.info_message = f"Не удалось получить данные для {num}"
            info_label_thread.start()
            if self.previous_no_results_index == -1:
                self.previous_no_results_index = index
                # print(f'previous_no_results_index: {self.previous_no_results_index}')
            self.no_results_count += 1
            # print(f'Не удалось получить данные для {num}. Счетчик: {self.no_results_count}')
            # if self.no_results_count > 2:
            #     print(f'restart from {self.previous_no_results_index}')
            #     if self.settings['proxy_path']:
            #         self.excel_iter(self.previous_no_results_index)
            #     else:
            #         warning_message_thread.text_message = 'Блокировка'
            #         warning_message_thread.start()
            return
        self.no_results_count = 0
        self.previous_no_results_index = -1
        makes = search_result['makes']['list']
        if len(makes) > 1:
            for make in makes:
                make_name = make['make']
                num = make['num']
                tags = make['tags']
                if not with_analogs and ('Только аналоги' in tags):
                    continue
                url = f'https://emex.ru/api/search/search?make={make_name}&detailNum={num}&locationId=29084&showAll=true' \
                      f'&longitude=37.617635&latitude=55.755814'
                # print(url)
                new_json_data = self.get_json_data(url)
                if new_json_data is None:
                    continue
                search_result = new_json_data['searchResult']
                originals = search_result.get('originals', None)
                if originals is None:
                    # print(f'Не удалось получить данные для {num}')
                    continue
                self.get_detail_data(new_json_data, providers, rating, with_analogs, columns, values)
        else:
            originals = search_result.get('originals', None)
            if originals is None:
                info_label_thread.info_message = f"Не удалось получить данные для {num}"
                info_label_thread.start()
                if self.previous_no_results_index == -1:
                    self.previous_no_results_index = index
                self.no_results_count += 1
                return
            self.get_detail_data(json_data, providers, rating, with_analogs, columns, values)
        # self.ex.check_data()

    def get_detail_data(self, json_data, providers: list, rating: list, with_analogs: bool, columns, values):
        search_result = json_data['searchResult']
        original_offers = search_result['originals'][0]['offers']
        # makes = search_result['makes']['list']
        # if len(makes) > 1:
        #     get_details(json_data, providers, rating, with_analogs)
        #     return
        make = search_result['make']
        name = search_result['name']
        num = search_result['num']
        # print(num, name, make)

        for original_offer in original_offers:
            provider = original_offer['rating2']['code']
            if providers:
                if not (provider.lower() in providers):
                    continue
            try:
                provider_rating = original_offer['rating2']['value']
            except KeyError:
                provider_rating = None
            if rating and provider_rating:
                if not (rating[0] <= provider_rating <= rating[1]):
                    continue

            for column, value in zip(columns, values):
                self.ex.add_key_value(column, value)

            self.ex.add_key_value(self.main_key, num)
            self.ex.add_key_value('Наименование', name)
            self.ex.add_key_value('Бренд', make)

            quantity = original_offer['quantity']
            delivery = f"{original_offer['delivery']['value']} {original_offer['delivery']['units']}"
            price = original_offer['displayPrice']['value']
            # print(f'quantity: {quantity}, delivery: {delivery},'
            #       f' price: {price}, provider: {provider}, '
            #       f'provider_rating: {provider_rating}')

            self.ex.add_key_value('Поставщик', provider)
            self.ex.add_key_value('Количество', quantity)
            self.ex.add_key_value('Цена', price)
            self.ex.add_key_value('Время доставки', delivery)

        if with_analogs:
            # print('ANALOGS')
            analogs = search_result['analogs']
            for analog in analogs:
                analog_num = analog['detailNum']
                analog_make = analog['make']
                analog_name = analog['name']
                # print(analog_num, analog_name, analog_make)

                analog_offers = analog['offers']
                for analog_offer in analog_offers:

                    analog_provider = analog_offer['rating2']['code']
                    if providers:
                        if not (analog_provider in providers):
                            continue
                    try:
                        analog_provider_rating = analog_offer['rating2']['value']
                    except KeyError:
                        analog_provider_rating = None
                    if rating and analog_provider_rating:
                        if not (rating[0] <= analog_provider_rating <= rating[1]):
                            continue

                    self.ex.add_key_value(self.main_key, analog_num)
                    self.ex.add_key_value('Наименование', analog_name)
                    self.ex.add_key_value('Бренд', analog_make)

                    analog_quantity = analog_offer['quantity']
                    analog_delivery = f"{analog_offer['delivery']['value']} {analog_offer['delivery']['units']}"
                    analog_price = analog_offer['displayPrice']['value']
                    # print(f'analog_quantity: {analog_quantity}, analog_delivery: {analog_delivery},'
                    #       f' analog_price: {analog_price}, analog_provider: {analog_provider}, '
                    #       f'analog_provider_rating: {analog_provider_rating}')

                    self.ex.add_key_value('Поставщик', analog_provider)
                    self.ex.add_key_value('Количество', analog_quantity)
                    self.ex.add_key_value('Цена', analog_price)
                    self.ex.add_key_value('Время доставки', analog_delivery)

                    for column, value in zip(columns, values):
                        self.ex.add_key_value(column, value)


def check_limit():
    df = pd.read_excel('gs.xlsx')
    count = 0
    for num in df['артикул'].values[80:]:
        r = requests.get(
            f'https://emex.ru/api/search/search?detailNum={num}&locationId=29084&showAll=true&'
            f'longitude=37.617635&latitude=55.755814')
        count += 1
        print(r.json())
        print('*****************************************'
              f'*****************{count}****************'
              '*****************************************')


if __name__ == '__main__':
    pass
