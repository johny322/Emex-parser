from PyQt5.QtCore import QThread, pyqtSignal


class ProgressBarValueThread(QThread):
    mysignal = pyqtSignal(int)
    value = 1

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit(self.value)


class ProgressBarRangeThread(QThread):
    mysignal = pyqtSignal(int)
    max_value = 100

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit(self.max_value)


class EnabledStartButtonThread(QThread):
    mysignal = pyqtSignal(bool)
    enabled = True

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit(self.enabled)


class EndMessageThread(QThread):
    mysignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit('Завершено')


class WarningMessageThread(QThread):
    mysignal = pyqtSignal(str)
    text_message = ''

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit(self.text_message)


class InfoLabelThread(QThread):
    mysignal = pyqtSignal(str)
    info_message = ''

    def __init__(self):
        super().__init__()

    def run(self):
        self.mysignal.emit(self.info_message)
