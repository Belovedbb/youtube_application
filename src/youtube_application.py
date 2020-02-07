from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QPushButton, QStyleFactory\
    , QWidget, QLabel, QComboBox, QHBoxLayout, QGroupBox, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QPalette, QPixmap, QBrush, QIcon, QFont, QPalette, QColor, QImage
from PyQt5.QtCore import Qt, QSize, QPoint, pyqtProperty, QPropertyAnimation, QRunnable, QThreadPool\
    , QObject, pyqtSignal, pyqtSlot
import sys, copy, re
from resource import main_rc
from LineEdit import LineEdit
from downloads import Downloads
from pytube import YouTube
import traceback
import urllib
import database

#pyrcc5 -o resource/main_rc.py resource/main.qrc
class WorkerSignal(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class WorkerYouTube(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, fn, *args, **kwargs):
            super(WorkerYouTube, self).__init__()
            # Store constructor arguments (re-used for processing)
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
            self.signal =  WorkerSignal()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signal.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signal.result.emit(result)
        finally:
            self.signal.finished.emit()

class ContinueButton(QPushButton):
    def __init__(self, *args):
        super(ContinueButton, self).__init__(*args)

    def _set_pos(self, pos):
        self.move(pos)

    pos = pyqtProperty(QPoint, fset = _set_pos )

class YoutubeScene(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(YoutubeScene, self).__init__(*args, **kwargs)
        QApplication.instance().setStyleSheet(open("resource/main.qss","r").read())
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(500, 500)
        self.setAnimated(True)
        self.setObjectName("Youtube")
        self.setWindowTitle("Youtube Downloader")
        self.download_dialog = None
        self.youtube_dict = {}
        self.youtube_download_tuple = {}
        self.youtube_choice = {}
        self.counter = 0
        self.data_app = database.App_database()


        self.next_button = ContinueButton("Continue")
        self.next_button.setFixedSize(QSize(100,20))
        self.next_button.setObjectName("next_button")
        

        self.anim = QPropertyAnimation(self.next_button, b"pos")
        self.anim.setDuration(1000)

        self.main_layout = QVBoxLayout()

        url_layout = QVBoxLayout()
        
        search_label = QLabel("Youtube Downloader Url")
        label_font = QFont() 
        label_font.setFamily("Kunstler Script")
        label_font.setPointSize(20)
        search_label.setFont(label_font)
        search_label.setAlignment(Qt.AlignCenter )
        url_layout.addWidget(search_label)


        url_input = LineEdit()
        url_input.setFixedSize(QSize(self.width() * (1/2), 50))

        url_button = QPushButton("Url Search")
        url_button.setFixedSize(QSize(self.width() * (1/2.5), url_input.height()))
        url_button.setObjectName("url_button")
        url_button.clicked.connect(lambda: self.call_youtube(url_input.text()))

        line_button = QHBoxLayout()
        line_button.addWidget(url_input)
        line_button.addWidget(url_button)

        url_layout.addLayout(line_button)

        view_pane = QGroupBox()
        view_pane.setObjectName("view_pane")
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setScaledContents(True)
        stack_layout = QStackedLayout()
        
        stack_layout.addWidget(self.thumbnail_label)
        view_pane.setLayout(stack_layout)
        #view_pane.setGeometry(0,0, self.width() * 1/1.2, self.height() * 1/4 )
        view_pane.setFixedSize(QSize(self.width() -20, self.height() * 1/4))

        sub_section_layout = QHBoxLayout()
        sub_section_layout.setAlignment(Qt.AlignTop)

        self.combo_left = QComboBox()
        self.combo_left.setObjectName("combo_left")
        self.combo_left.setFixedHeight(25)
        self.combo_left.addItems(["Download Page"])
       
        self.combo_left.currentIndexChanged.connect(self.current_index_left_slot)
        self.combo_left.setDisabled(True)

        self.combo_right = QComboBox()
        self.combo_right.setObjectName("combo_right")
        self.combo_right.setFixedHeight(25)
        self.combo_right.addItems(["Download Page"])
        self.combo_right.currentIndexChanged.connect(self.current_index_right_slot)
        self.combo_right.setDisabled(True)
        
        sub_section_layout.addWidget(self.combo_left)
        sub_section_layout.addWidget(self.combo_right)

        self.main_layout.addLayout(url_layout)
        self.main_layout.addWidget(view_pane)
        self.main_layout.addLayout(sub_section_layout)
        self.main_layout.addWidget(self.next_button, Qt.AlignLeft)
        
        self.window_widget = QWidget()
        self.window_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.window_widget)

        self.next_button.clicked.connect(self.download_page)
        self.thread_pool = QThreadPool()
        

    def resizeEvent(self, event):
        self.set_back_pix()
        return super(YoutubeScene, self).resizeEvent(event)

    def sizeHint(self):
        return QSize(500, 500)

    def set_back_pix(self):
        pixmap = QPixmap(":resource/bck_img.jpg")
        back_g = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(back_g))
        self.setPalette(palette)

    def th_youtube_list(self, youtube_url):
        print(youtube_url)
        yt = YouTube(youtube_url)
        return yt, [yt.title, yt.description, yt.age_restricted, yt.rating]
    def print_output(self, result):
        self.youtube_dict[self.counter] = result
        self.counter_switch = False
        self.counter  += 1
        url = "https://img.youtube.com/vi/%s/maxresdefault.jpg" % result[0].video_id
        data = urllib.request.urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.thumbnail_label.setPixmap(pixmap)
        for i in result[1]:
            print(i)
    def th_youtube_codecs(self):
        download_tuple = self.youtube_dict[self.counter - 1][0].streams.filter(only_audio=True).order_by('abr').desc().all(),\
               self.youtube_dict[self.counter - 1][0].streams.filter(subtype='mp4', progressive=True).order_by('resolution').desc().all()
        return download_tuple
    def th_load_box(self, result):
        self.youtube_download_tuple[self.counter - 1] = result
        for index,audio_codec in enumerate(result[0]):
            labels = re.search("abr[=\"a-z0-9]*", str(audio_codec)).group()[5:-1], re.search("\/[a-z0-9]+", str(audio_codec)).group()[1:],\
                str(round(result[0][index].filesize/(1024*1024)))
            self.combo_left.addItem("%s %s %smb" % labels)
        for index,video_codec in enumerate(result[1]):
            labels = re.search("res[=\"a-z0-9]*", str(video_codec)).group()[5:-1], re.search("\/[a-z0-9]+", str(video_codec)).group()[1:],\
                str(round(result[1][index].filesize/(1024*1024)))
            self.combo_right.addItem("%s %s  %smb" % labels)
        if self.combo_left.count() > 1 and self.combo_right.count() > 1:
            self.combo_left.setDisabled(False)
            self.combo_right.setDisabled(False)
    def th_finish_signal(self):
        print("codecs loaded")

    def thread_complete(self):
        print("THREAD DESCRIPTION COMPLETE!")
        if self.combo_right.count() > 1:
            for item_index in range(0,self.combo_right.count()):
                if not item_index == 0:
                    self.combo_right.removeItem(item_index)

        if self.combo_left.count() > 1:
            for item_index in range(0,self.combo_left.count()):
                if not item_index == 0:
                    self.combo_left.removeItem(item_index)

        worker = WorkerYouTube(self.th_youtube_codecs)
        worker.signal.result.connect(self.th_load_box)
        worker.signal.finished.connect(self.th_finish_signal)
        self.thread_pool.start(worker)
        
    def call_youtube(self, youtube_url):
        worker = WorkerYouTube(self.th_youtube_list, youtube_url)
        worker.signal.result.connect(self.print_output)
        worker.signal.finished.connect(self.thread_complete)
        self.thread_pool.start(worker)

    def current_index_left_slot(self, index):
        if int(self.next_button.x()) > int(self.width()/2):
            start0, start1 = (self.next_button.x()), (self.next_button.y())
            end0, end1 = (self.width() - self.next_button.width() - self.next_button.x()), (self.next_button.y())
            self.anim.setStartValue(QPoint(start0, start1))
            self.anim.setEndValue(QPoint(end0, end1))
            self.anim.start()
        self.youtube_choice[self.counter -1] = None if index == 0 or not self.combo_left.count() > 1 else  self.youtube_download_tuple[self.counter - 1][0][index - 1]
            
    def current_index_right_slot(self, index):
        
        if int(self.next_button.x()) < int(self.width()/2):
            start0, start1 = (self.next_button.x()), (self.next_button.y())
            end0, end1 = (self.width() - self.next_button.width() - self.next_button.x()), (self.next_button.y())
            self.anim.setStartValue(QPoint(start0, start1))
            self.anim.setEndValue(QPoint(end0, end1))
            self.anim.start()
        self.youtube_choice[self.counter -1] = None if index == 0 or not self.combo_right.count() > 1 else  self.youtube_download_tuple[self.counter - 1][1][index - 1]

    def download_page(self):
        self.hide()
        if not self.download_dialog:
            self.download_dialog = Downloads( self)
        elif self.download_dialog and self.counter == 0:
            self.download_dialog.show()
        elif self.youtube_choice[self.counter -1] == None and self.download_dialog:
            self.download_dialog.show()
        else:
            self.download_dialog.progress_bar_appender()
            self.download_dialog.show()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    window = YoutubeScene()
    window.show()
    app.exec_()
#https://www.youtube.com/watch?v=zAGVQLHvwOY