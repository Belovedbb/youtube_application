from PyQt5.QtWidgets import  QWidget, QPushButton, QDialog, QVBoxLayout, QApplication\
    , QTabWidget, QScrollArea, QProgressBar
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize
from downloadlayout import DownloadLayout
from progressbar import DownloaderWidget


class Downloads(QDialog):
    def __init__(self, *args, **kwargs):
        super(Downloads, self).__init__(*args, **kwargs)
        self.main_pointer = args[0]
        self.tab = None

        self.setFixedSize(500, 500)
        self.setWindowTitle("Youtube Downloads")

        layout = QVBoxLayout()
        self.setPalette(self.set_back_pix())

        self.back_button = QPushButton("Back")
        self.back_button.setObjectName("download_back_button")
        self.back_button.pressed.connect(self.back_it_up)

        self.tab = QTabWidget()
        self.tab.setTabsClosable(False)

        tab_downloading_widget = QWidget()
        tab_downloading_widget.setFixedWidth(self.width())
        tab_downloading_widget.setObjectName("tab_downloading")
        tab_downloading_widget.setAutoFillBackground(True)
        downloading_scroll_area = QScrollArea()
        downloading_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) 
        downloading_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        downloading_scroll_area.setWidgetResizable(True)
        self.download_handler = DownloadLayout(self.main_pointer.data_app,0, self.main_pointer)
        tab_downloading_widget.setLayout(self.download_handler)
        tab_downloading_widget.setPalette(self.set_back_pix(tab_downloading_widget.layout().geometry().size()))
        downloading_scroll_area.setWidget(tab_downloading_widget)
        self.tab.addTab(downloading_scroll_area, "Downloading")

        tab_downloaded_widget = QWidget()
        tab_downloaded_widget.setFixedWidth(self.width())
        tab_downloaded_widget.setObjectName("tab_downloaded")
        tab_downloaded_widget.setAutoFillBackground(True)
        downloaded_scroll_area = QScrollArea()
        downloaded_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        downloaded_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        downloaded_scroll_area.setWidgetResizable(True)
        tab_downloaded_widget.setLayout(DownloadLayout(self.main_pointer.data_app, 1, None))
        tab_downloaded_widget.setPalette(self.set_back_pix(tab_downloaded_widget.layout().geometry().size()))
        downloaded_scroll_area.setWidget(tab_downloaded_widget)
        self.tab.addTab(downloaded_scroll_area, "Downloaded")

        layout.addWidget(self.back_button)
        layout.addWidget(self.tab)
        self.setLayout(layout)
        self.setWindowFlags(Qt.Window |Qt.WindowSystemMenuHint)
        self.setModal(False)
        self.show()

    def progress_bar_appender(self):
        download_widget = DownloaderWidget()
        self.download_handler.create_downloading_layout(download_widget, self.main_pointer)
    def resizeEvent(self, event):
        self.set_back_pix()
        return super(Downloads, self).resizeEvent(event)

    def back_it_up(self):
        self.hide()
        self.main_pointer.show()

    def set_back_pix(self, size = None):
        if size == None:
            size = self.size() if not self.tab else self.tab.size()
        print(size)
        pixmap = QPixmap(":resource/bck_img.jpg")
        back_g = pixmap.scaled(size, Qt.IgnoreAspectRatio)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(back_g))
        return palette

    def closeEvent(self, event):
        self.main_pointer.show()
        return super().closeEvent(event)