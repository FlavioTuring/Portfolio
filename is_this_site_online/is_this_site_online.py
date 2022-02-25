from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from mypy import mywebpy as mwp


def is_url_online(url):

    try:
        response = mwp.my_head_request(url)
        got_response = response.find("200", 0, 20)
    except:
        return "error"
    else:
        if got_response == -1:
            return "offline"
        else:
            return "online"


class Window(QWidget):
    def __init__(self, *, centralized=False):
        super().__init__()
        self.std_x = 0
        self.std_y = 0
        self.std_width = 1000
        self.std_height = 800
        self.std_coord = QPoint(self.std_x, self.std_y)
        self.std_size = QSize(self.std_width, self.std_height)
        self.std_rect = QRect(self.std_coord, self.std_size)
        self.screen_center = self.get_screen_center()

        if centralized:
            self.centralize()
        else:
            self.set_std_geometry()

    @staticmethod
    def get_screen_center():
        screen = QApplication.primaryScreen()
        screen_center = screen.geometry().center()
        return screen_center

    def set_std_geometry(self):
        self.setGeometry(self.std_rect)

    def centralize(self, width=None, height=None):
        if width is None:
            width = self.std_width
        if height is None:
            height = self.std_height
        centralized_rect_size = QSize(width, height)
        centralized_rect = QRect(self.std_coord, centralized_rect_size)
        centralized_rect.moveCenter(self.screen_center)
        self.setGeometry(centralized_rect)


class MainWindow(Window):
    def __init__(self, centralized=True):
        super().__init__(centralized=centralized)
        self.url_label = None
        self.status_label = None
        self.site_status_label = None
        self.url_txt = None
        self.check_button = None
        self.grid = None

        self.centralize(425, 152)
        self.setMinimumSize(225, 152)
        self.setMaximumSize(998, 383)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Is This Site Online")
        self.setWindowIcon(QIcon('icon.png'))

        self.url_label = QLabel(self)
        self.url_label.setText("URL: ")
        self.status_label = QLabel(self)
        self.status_label.setText("Status: ")
        self.url_txt = QLineEdit(self)

        self.site_status_label = QLabel()
        self.site_status_label.setText("------")
        self.site_status_label.setStyleSheet("QLabel { color : grey; }")

        self.check_button = QPushButton(self)
        self.check_button.setText("Check")

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.url_label, 0, 0)
        self.grid.addWidget(self.status_label, 1, 0)
        self.grid.addWidget(self.url_txt, 0, 1, 1, 4)
        self.grid.addWidget(self.site_status_label, 1, 1)
        self.grid.addWidget(self.check_button, 3, 3)

        for i in range(4):
            self.grid.setRowMinimumHeight(i, 30)
        for i in range(4):
            self.grid.setColumnMinimumWidth(i, 10)

        h_spacer_item = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        v_spacer_item = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        aux_spacer_item = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.grid.addItem(h_spacer_item, 1, 2)
        self.grid.addItem(v_spacer_item, 2, 0)
        self.grid.addItem(aux_spacer_item, 2, 4)

        self.check_button.clicked.connect(self.check)

        self.show()

    def check(self):
        url = self.url_txt.text()
        if url == '':
            pass
        else:
            site_status = is_url_online(url)
            if site_status == "online":
                self.site_status_label.setText("ONLINE")
                self.site_status_label.setStyleSheet("QLabel { color : green; }")
            elif site_status == "offline":
                self.site_status_label.setText("OFFLINE")
                self.site_status_label.setStyleSheet("QLabel { color : red; }")
            elif site_status == "error":
                self.site_status_label.setText("ERROR")
                self.site_status_label.setStyleSheet("QLabel { color : black; }")
            self.grid.addWidget(self.site_status_label, 1, 1)


app = QApplication([])
app.setStyle('Fusion')
main_window = MainWindow()
app.exec()
