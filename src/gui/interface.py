import os
import sys

from PyQt5.QtGui import QIcon, QFont, QTextList
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QProgressBar, QLineEdit, QPushButton, \
    QListWidget, QLabel, QDoubleSpinBox, QCheckBox, QToolButton, QFileDialog, QMessageBox, QTextBrowser, QTextEdit, \
    QRadioButton

from src.gui.threads.gui_threads_loader import progress_bar_value_thread, progress_bar_range_thread, \
    enabled_start_button_thread, end_message_thread, warning_message_thread, info_label_thread
from src.gui.threads.parser_threads_loader import emex_parser_tread


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {}

        self.setWindowTitle('Emex parser')
        self.resize(600, 400)
        try:
            self.setWindowIcon(QIcon(os.path.join(sys._MEIPASS, 'emex.ico')))
        except AttributeError:
            self.setWindowIcon(QIcon('emex.ico'))

        self.font = QFont()
        self.font.setFamily("Times New Roman")
        self.font.setPointSize(12)

        self.setFont(self.font)

        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.vlayout.addLayout(self.hlayout)

        self.tabWidget = QTabWidget()

        # tab1 widgets
        self.tab1 = QWidget()
        self.tabWidget.addTab(self.tab1, 'Запуск')

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.start_excel_path = QLineEdit()
        self.start_excel_path.setPlaceholderText('Путь до исходного файла')
        self.start_excel_path.setReadOnly(True)
        self.start_excel_btn = QToolButton()
        self.start_excel_btn.setText('...')

        self.finish_excel_path = QLineEdit()
        self.finish_excel_path.setPlaceholderText('Путь до финального файла')
        self.finish_excel_path.setReadOnly(True)
        self.finish_excel_btn = QToolButton()
        self.finish_excel_btn.setText('...')

        # self.info_label = QLabel()
        self.info = QTextEdit()
        self.info.setReadOnly(True)

        self.btn_start = QPushButton('Старт')

        # tab2 widgets
        self.tab2 = QWidget()
        self.tabWidget.addTab(self.tab2, 'Настройки')

        self.providers_list = QListWidget()
        self.providers_label = QLabel('Добавить поставщика')
        self.providers_line = QLineEdit()
        self.providers_line.setPlaceholderText('Поставщик')
        self.add_providers_btn = QPushButton('Добавить')

        self.rating_label = QLabel('Оценка')
        self.min_rating_sb = QDoubleSpinBox()
        self.min_rating_sb.setRange(0.0, 5.0)
        self.min_rating_sb.setWrapping(True)
        self.min_rating_sb.setSingleStep(0.1)

        self.max_rating_sb = QDoubleSpinBox()
        self.max_rating_sb.setWrapping(True)
        self.max_rating_sb.setSingleStep(0.1)
        self.max_rating_sb.setRange(0.0, 5.0)

        self.analogs_check_box = QCheckBox('Аналоги')

        # self.proxy_check_box = QCheckBox('Использовать обычные прокси')
        #
        # self.bright_data_proxy_check_box = QCheckBox('Использовать прокси brightdata')
        self.use_proxy_check_box = QCheckBox('Использовать прокси')
        self.use_proxy_check_box.setChecked(True)
        self.proxy_rbt = QRadioButton('Обычные прокси')
        self.bright_data_proxy_rbt = QRadioButton('Прокси brightdata')
        self.proxy_manager_rbt = QRadioButton('Proxy Manager')
        self.proxy_manager_rbt.setChecked(True)

        self.proxy_path = QLineEdit()
        self.proxy_path.setPlaceholderText('Путь до файла с прокси')
        self.proxy_path.setReadOnly(True)

        self.proxy_path_btn = QToolButton()
        self.proxy_path_btn.setText('...')
        # self.proxy_path_btn.setEnabled(False)

        self.settings_btn = QPushButton('Задать')

        self.setup_layout()

        self.add_providers_btn.clicked.connect(self.evt_add_provider)
        self.providers_list.doubleClicked.connect(self.evt_delete_provider)
        self.providers_line.returnPressed.connect(self.add_providers_btn.click)

        self.proxy_path_btn.clicked.connect(self.evt_add_proxy_path)

        self.use_proxy_check_box.clicked.connect(self.evt_use_proxy)
        # self.bright_data_proxy_check_box.clicked.connect(self.evt_use_proxy)

        # self.proxy_check_box.clicked.connect(self.evt_type_proxy)
        # self.bright_data_proxy_check_box.clicked.connect(self.evt_type_proxy)

        self.settings_btn.clicked.connect(self.evt_set_settings)

        self.start_excel_btn.clicked.connect(self.evt_set_start_excel_path)
        self.finish_excel_btn.clicked.connect(self.evt_set_finish_excel_path)

        self.btn_start.clicked.connect(self.evt_start)

        progress_bar_value_thread.mysignal.connect(self.add_progress_bar)
        progress_bar_range_thread.mysignal.connect(self.set_progress_bar_range)
        enabled_start_button_thread.mysignal.connect(self.set_start_btn_enabled)
        end_message_thread.mysignal.connect(self.end_message)
        warning_message_thread.mysignal.connect(self.warning_message)
        info_label_thread.mysignal.connect(self.set_info_text)

    # def evt_type_proxy(self):
    #     if self.bright_data_proxy_check_box.isChecked():
    #         self.proxy_check_box.setChecked(False)
    #     elif self.proxy_check_box.isChecked():
    #         self.bright_data_proxy_check_box.setChecked(False)

    def set_info_text(self, info_message: str):
        # self.info_label.setText(info_message)
        self.info.append(info_message)

    def warning_message(self, text_message: str):
        QMessageBox.warning(self, 'Предупреждение', text_message)

    def end_message(self, value: str):
        QMessageBox.information(self, 'Информация', value)

    def set_start_btn_enabled(self, value):
        self.btn_start.setEnabled(value)
        self.settings_btn.setEnabled(value)

    def set_progress_bar_range(self, value):
        self.progress_bar.setRange(0, value)

    def evt_start(self):
        self.progress_bar.setValue(0)
        excel_path = self.start_excel_path.text()
        if not excel_path:
            QMessageBox.warning(self, 'Предупреждение', 'Не задан начальный файл')
            return
        save_path = self.finish_excel_path.text()
        if not save_path:
            QMessageBox.warning(self, 'Предупреждение', 'Не задан файл сохранения')
            return
        self.settings['excel_path'] = excel_path
        self.settings['save_path'] = save_path
        if 'proxy_path' not in self.settings:
            QMessageBox.warning(self, 'Предупреждение', 'Не заданы настройки')
            return
        self.btn_start.setEnabled(False)
        self.settings_btn.setEnabled(False)
        emex_parser_tread.settings = self.settings
        emex_parser_tread.start()
        # progress_bar_value_thread.start()
        # self.btn_start.setEnabled(True)

    def add_progress_bar(self, value):
        cur_val = self.progress_bar.value()
        self.progress_bar.setValue(cur_val + value)

    def evt_set_start_excel_path(self):
        frame = QFileDialog.getOpenFileName(self, caption='Выберите файл эксель',
                                            filter='XLSX File (*.xlsx);;XLS File (*.xls)')
        file = frame[0]
        if file:
            self.start_excel_path.setText(file)

    def evt_set_finish_excel_path(self):
        frame = QFileDialog.getOpenFileName(self, caption='Выберите файл эксель',
                                            filter='XLSX File (*.xlsx);;XLS File (*.xls)')
        file = frame[0]
        if file:
            self.finish_excel_path.setText(file)

    def evt_set_settings(self):
        if self.min_rating_sb.value() > self.max_rating_sb.value():
            QMessageBox.warning(self, 'Предупреждение', 'Некоректное значение рейтинга')
            return
        if self.use_proxy_check_box.isChecked() and not self.proxy_path.text():
            QMessageBox.warning(self, 'Предупреждение', 'Не задан путь до прокси')
            return
        if self.min_rating_sb.value() == self.max_rating_sb.value() == 0:
            self.settings['rating'] = []
        else:
            self.settings['rating'] = [self.min_rating_sb.value(), self.max_rating_sb.value()]
        self.settings['proxy_path'] = self.proxy_path.text()
        if not self.use_proxy_check_box.isChecked():
            self.settings['bright_data_proxy'] = False
            self.settings['proxy_manager'] = False
        else:
            self.settings['bright_data_proxy'] = self.bright_data_proxy_rbt.isChecked()
            self.settings['proxy_manager'] = self.proxy_manager_rbt.isChecked()
        self.settings['providers'] = [self.providers_list.item(i).text().lower()
                                      for i in range(self.providers_list.count())]
        self.settings['with_analogs'] = self.analogs_check_box.isChecked()
        print(self.settings)
        QMessageBox.information(self, 'Информация', 'Настройки заданы')

    def evt_use_proxy(self):
        if self.use_proxy_check_box.isChecked():
            self.proxy_path_btn.setEnabled(True)
            self.proxy_manager_rbt.setEnabled(True)
            self.bright_data_proxy_rbt.setEnabled(True)
            self.proxy_rbt.setEnabled(True)
        else:
            self.proxy_path_btn.setEnabled(False)
            self.proxy_path.setText('')

            self.proxy_rbt.setEnabled(False)

            self.bright_data_proxy_rbt.setEnabled(False)

            self.proxy_manager_rbt.setEnabled(False)

    def evt_add_proxy_path(self):
        frame = QFileDialog.getOpenFileName(self, caption='Выберите текстовый файл',
                                            filter='TXT File (*.txt)')
        file = frame[0]
        if file:
            self.proxy_path.setText(file)

    def evt_add_provider(self):
        provider = self.providers_line.text()
        if provider:
            self.providers_list.addItem(provider.strip())
            self.providers_line.clear()

    def evt_delete_provider(self):
        row = self.providers_list.currentRow()
        self.providers_list.takeItem(row).text()

    def setup_layout(self):
        self.vlayout.addWidget(self.tabWidget)
        self.setLayout(self.vlayout)
        self.set_tab1_layout()
        self.set_tab2_layout()

    def set_tab1_layout(self):
        self.tab1_vlayout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_vlayout)

        self.start_file_layout = QHBoxLayout()
        self.start_file_layout.addWidget(self.start_excel_path)
        self.start_file_layout.addWidget(self.start_excel_btn)
        self.tab1_vlayout.addLayout(self.start_file_layout)

        self.finish_file_layout = QHBoxLayout()
        self.finish_file_layout.addWidget(self.finish_excel_path)
        self.finish_file_layout.addWidget(self.finish_excel_btn)
        self.tab1_vlayout.addLayout(self.finish_file_layout)

        # self.tab1_vlayout.addWidget(self.info_label)
        self.tab1_vlayout.addWidget(self.info)

        self.tab1_vlayout.addStretch()

        self.pb_btn_layout = QHBoxLayout()
        self.pb_btn_layout.addWidget(self.progress_bar)
        self.pb_btn_layout.addWidget(self.btn_start)
        self.tab1_vlayout.addLayout(self.pb_btn_layout)

    def set_tab2_layout(self):
        self.tab2_vlayout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_vlayout)

        self.tab2_vlayout.addWidget(self.providers_label)

        providers_hlayout = QHBoxLayout()
        providers_vlayout = QVBoxLayout()
        providers_vlayout.addWidget(self.providers_line)
        providers_vlayout.addWidget(self.add_providers_btn)
        providers_vlayout.addStretch()

        providers_hlayout.addLayout(providers_vlayout)
        providers_hlayout.addWidget(self.providers_list)

        self.tab2_vlayout.addLayout(providers_hlayout)

        self.tab2_vlayout.addWidget(self.rating_label)
        rating_hlayout = QHBoxLayout()
        # rating_hlayout.addWidget(QLabel('От'))
        rating_hlayout.addWidget(self.min_rating_sb)
        # rating_hlayout.addWidget(QLabel('до'))
        rating_hlayout.addWidget(self.max_rating_sb)
        self.tab2_vlayout.addLayout(rating_hlayout)

        self.tab2_vlayout.addWidget(self.analogs_check_box)
        self.tab2_vlayout.addWidget(self.use_proxy_check_box)

        proxy_check_box_hlayout = QHBoxLayout()
        # proxy_check_box_hlayout.addWidget(self.proxy_check_box)
        # proxy_check_box_hlayout.addWidget(self.bright_data_proxy_check_box)
        proxy_check_box_hlayout.addWidget(self.proxy_manager_rbt)
        proxy_check_box_hlayout.addWidget(self.bright_data_proxy_rbt)
        proxy_check_box_hlayout.addWidget(self.proxy_rbt)

        # self.tab2_vlayout.addWidget(self.proxy_check_box)
        self.tab2_vlayout.addLayout(proxy_check_box_hlayout)

        proxy_hlayout = QHBoxLayout()
        proxy_hlayout.addWidget(self.proxy_path)
        proxy_hlayout.addWidget(self.proxy_path_btn)
        self.tab2_vlayout.addLayout(proxy_hlayout)

        settings_hlayout = QHBoxLayout()
        settings_hlayout.addStretch()
        settings_hlayout.addWidget(self.settings_btn)
        self.tab2_vlayout.addLayout(settings_hlayout)
