import time

from PyQt5.QtCore import QThread, pyqtSignal

# from Code.src.gui.threads.gui_threads_loader import enabled_start_button_thread, progress_bar_range_thread, \
#     progress_bar_value_thread
from src.gui.threads.gui_threads_loader import enabled_start_button_thread, end_message_thread, info_label_thread
from src.parser.emex import Emex


class EmexParserTread(QThread):
    mysignal = pyqtSignal(int, str)
    settings = {}

    def __init__(self):
        super().__init__()

    def run(self):
        # progress_bar_range_thread.max_value = 10
        # progress_bar_range_thread.start()
        # for i in range(10):
        #     print(i)
        #     time.sleep(1)
        #     progress_bar_value_thread.start()
        # enabled_start_button_thread.start()
        info_label_thread.info_message = 'Начало работы'
        info_label_thread.start()
        emex = Emex(self.settings)
        emex.excel_iter()
        info_label_thread.info_message = 'Завершено'
        info_label_thread.start()
        enabled_start_button_thread.start()
        end_message_thread.start()
