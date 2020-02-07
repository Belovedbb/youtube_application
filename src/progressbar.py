from PyQt5.QtWidgets import QProgressBar, QVBoxLayout, QWidget, QLabel, QApplication, QHBoxLayout, QPushButton, QGroupBox
from PyQt5.QtGui import QPixmap
class  DownloaderWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DownloaderWidget, self).__init__(*args, **kwargs)
        self.setLayout(QHBoxLayout())
        self.label_title = QLabel("Title")
        self.label_title.setObjectName("label_title")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.label_progress = QLabel("Loading...")
        self.label_progress.setObjectName("label_progress")
        self.label_image = QLabel()
        self.label_image.setPixmap(QPixmap(":resource/clock_load.png"))
        self.label_image.setFixedSize(50,50)
        self.button_cancel = QPushButton("Cancel")
        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(10)
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(10)
        self.group_box = QGroupBox()
        self.group_box.setObjectName("download_group_box")

        self.vbox.addWidget(self.label_title)
        self.vbox.addWidget(self.label_progress)
        self.vbox.addWidget(self.progress_bar)

        self.hbox.addWidget(self.label_image)
        self.hbox.addLayout(self.vbox)
        self.hbox.addWidget(self.button_cancel)

        self.group_box.setLayout(self.hbox)
        self.layout().addWidget(self.group_box)

if __name__ == "__main__":
    app = QApplication([])
    p = DownloaderWidget()
    p.show()
    app.exec()