import sys
import traceback

import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from src.gui.interface import MyApp
from src.parser.path import log_path


def log_error_with_tb(type, value, tback):
    now = time.asctime()
    traceback_text = ''.join(traceback.format_exception(type, value, tback))
    text = f'{now}\n' \
           f'{traceback_text}\n\n'
    with open(log_path, 'a') as f:
        f.write(text)


def my_excepthook(type, value, tback):
    if not str(value).__contains__("Не удалось загрузить страницу:"):
        QtWidgets.QMessageBox.critical(
            myApp, "CRITICAL ERROR", 'Произошла ошибка',
            QtWidgets.QMessageBox.Cancel
        )
    else:
        QtWidgets.QMessageBox.critical(
            myApp, "CRITICAL ERROR", str(value),
            QtWidgets.QMessageBox.Cancel
        )
    log_error_with_tb(type, value, tback)
    sys.__excepthook__(type, value, tback)


if __name__ == '__main__':
    sys.excepthook = my_excepthook
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    sys.exit(app.exec())
