import sys
import os
import re
from GUI import QtCore, QtGui, QtWidgets, Ui_MainWindow

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.path = None
        self.ui.pushButton.clicked.connect(self.get_folder)
        self.ui.pushButton_2.clicked.connect(self.start)

        self.sorting, self.renamer = Sorting(), Renamer()
        self.sorting.mysignal.connect(self.handler)
        self.renamer.mysignal.connect(self.handler)
        
    def get_folder(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите папку с файлами')

    def start(self):
        if self.path is not None:
            if self.ui.radioButton.isChecked() or self.ui.radioButton_2.isChecked():
                exceptional_extensions = self.ui.textEdit.toPlainText().split('\n')
                if self.ui.radioButton.isChecked(): # сортировка
                    self.sorting.get_folder(self.path, exceptional_extensions)
                    self.sorting.run()
                elif self.ui.radioButton_2.isChecked(): # переименовывание
                    self.renamer.get_folder(self.path, exceptional_extensions)
                    self.renamer.run()
            else:
                QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Не выбрадо действие с файлами')
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Путь до папки не задан')

    def handler(self, value):
        if value == 'finish':
            QtWidgets.QMessageBox.information(self, 'Уведомление', 'Работа завершена')
        elif value == 'error':
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Произошла ошибка\nПроверьте папку, в ней должен быть фаил Error.log')

class Sorting(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = None
        self.file_list = []
        self.global_list = []
        self.exceptional_extensions = None # что исключать из переименования
        self.current_ext = ''

    def get_folder(self, path, exceptional_extensions):
        self.path = path
        self.exceptional_extensions = exceptional_extensions

    def run(self):
        self.file_list = self.__file_files_list()
        self.__sort()

    def __file_files_list(self):
        files_not_sorted = [file.name for file in os.scandir(self.path) if file.name not in self.exceptional_extensions]
        return files_not_sorted

    def __sort(self):
        for item in self.file_list:
            try:
                file_ext = os.path.splitext(item)[1]
                pattern = r'([\w]+)'
                match = re.search(pattern, file_ext)
                if match:
                    folder_name = match.group().upper()
                    path1 = f'{self.path}//{folder_name}'

                    if not os.path.exists(path1):
                        os.mkdir(path1)

                    os.chdir(self.path)
                    os.system("move "+'"'+item+'"'+" "+'"'+path1+'"')
                    self.global_list.append(folder_name)
            except Exception as ex:
                with open(f'{self.path}//ERRORS.log', 'a') as file:
                    file.write(f'{ex}\n')

        if os.path.isfile(f'{self.path}//ERRORS.log'):
            # mysignal.emit('Программу критануло, проверьте папку с файлами, в ней будет файлик с ошибками')
            self.mysignal.emit('error')
        if len(self.global_list) > 0:
            self.mysignal.emit('finish')

class Renamer(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.path = None
        self.file_list = []
        self.exceptional_extensions = None # что исключать из переименования
        self.current_ext = ''
        self.counter = 0
        self.global_counter = 0

    def get_folder(self, path, exceptional_extensions):
        self.path = path
        self.exceptional_extensions = exceptional_extensions

    def run(self):
        self.file_list = self.__file_files_list()
        self.__rename()

    def __file_files_list(self):
        files_not_sorted = [os.path.splitext(file.name) for file in os.scandir(self.path) if not file.name in self.exceptional_extensions]
        return sorted(files_not_sorted, key=lambda a: a[1])

    def __rename(self):
        for item in self.file_list:
            if item[1] == self.current_ext:
                self.counter += 1
            else:
                self.counter = 1
                self.current_ext = item[1]
            try:
                if not os.path.isfile(f"{self.path}//{self.counter}{item[1]}"):
                    os.rename(
                        f"{self.path}//{''.join(item)}",
                        f"{self.path}//{self.counter}{item[1]}"
                    )
            except Exception as ex:
                with open(f'{self.path}//ERRORS.log', 'a') as file:
                    file.write(f'{ex}\n')
            self.global_counter += 1
        if os.path.isfile(f'{self.path}//ERRORS.log'):
            self.mysignal.emit('error')
        self.mysignal.emit('finish')



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Window = App()
    Window.show()
    sys.exit(app.exec_())
