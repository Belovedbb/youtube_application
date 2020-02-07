from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget,  QLabel, QProgressBar, QVBoxLayout, QPushButton\
    , QSizePolicy
from PyQt5.QtCore import QPoint, QRectF, Qt, QSize, pyqtSignal, QRunnable, QThreadPool, QObject, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QPixmap, QFontMetrics, QFont, QPen
import database, time, traceback, sys, os
from progressbar import DownloaderWidget
from pytube import request
import threading

W_WIDTH , W_HEIGHT = 640, 53.3333338

class WorkerSignal(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class WorkerDownload(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, fn, *args, **kwargs):
            super(WorkerDownload, self).__init__()
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

class DownloadWidget(QLabel):
    def __init__(self, number, *args, **kwargs):
        super(DownloadWidget, self).__init__(*args, **kwargs)
        self.number = number
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(QSize(W_WIDTH, W_HEIGHT * number) )
        self.setStyleSheet("color: 	#4B0082;")
        #pix = QPixmap(r"C:\Users\Beloved\Documents\Python\themes\a.jpg")
        effect_widget = QGraphicsDropShadowEffect(offset=QPoint(4, 4), blurRadius=5)
        self.setGraphicsEffect(effect_widget)
        self.setWordWrap(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect().x(), self.rect().y(), self.rect().width()/1.5, self.rect().height())
        path_shadow = QPainterPath()
        path_shadow.addRoundedRect(rect.translated(QPoint(4, 4)), 10, 10)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.fillPath(path_shadow, QColor("#9370db").darker())
        painter.fillPath(path, QColor("#9370db"))
        pen = QPen(QColor("black"))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        return super().paintEvent(event)

    def sizeHint(self):
        return QSize(W_WIDTH , W_HEIGHT)

class DownloadLayout(QVBoxLayout):
    DOWNLOADING, DOWNLOADED = range(2)
    def __init__(self,database,state, main_pointer, *args, **kwargs):
        super(DownloadLayout, self).__init__(*args, **kwargs)
        self.state = state
        self.setSpacing(10)
        self.thread_pool = QThreadPool()
        self.main_pointer = main_pointer
        self.data_app = database
        self.data_app.create_table()
        self.setAlignment(Qt.AlignTop)
        if self.state == DownloadLayout.DOWNLOADING:
            self.create_downloading_layout(DownloaderWidget(), self.main_pointer)
        elif self.state == DownloadLayout.DOWNLOADED:
            self.create_downloaded_layout()

    def create_downloading_layout(self, download_widget, main_pointer = None):
        if main_pointer.youtube_choice:
            self.main_pointer.youtube_choice[self.main_pointer.counter - 1]\
               if not main_pointer.youtube_choice[main_pointer.counter - 1] == None\
              else self.main_pointer.youtube_choice[self.main_pointer.counter - 1]
            #self.addWidget(DownloadWidget(6, "cool shit"))
            if self.main_pointer.youtube_choice[self.main_pointer.counter - 1]:
                download_widget.setFixedSize(W_WIDTH - 200, W_HEIGHT*2)
                download_widget.progress_bar.setFixedSize(300, 5)
                self.addWidget(download_widget)
                
                worker = WorkerDownload(self.progress_event, download_widget,\
                   self.main_pointer.youtube_choice[self.main_pointer.counter - 1])
                self.thread_pool.start(worker)
                worker.signal.finished.connect(lambda:self.progress_finish(self.data_app, download_widget.label_progress))
                
    def progress_event(self, download_widget, stream):#ba3 2904
        progress_bar = download_widget.progress_bar
        label = download_widget.label_progress
        download_widget.label_title.setText(self.main_pointer.youtube_choice[self.main_pointer.counter - 1].default_filename)
        size = stream.filesize
        bytes_remaining = size
        p = 0
        fp = os.path.join(os.getcwd(), stream.default_filename)
        with open(fp, 'wb') as fh:
            for chunk in request.get(stream.url):
                bytes_remaining -= len(chunk)
                progress_bar.setValue(p)
                label.setText("%d%s" % (progress_bar.value(), "%"))
                minor = bytes_remaining - size
                if minor < 0:
                    minor *= -1
                print(minor,size, minor/size, (minor/size)*100, sep="---")
                p = (minor/size)* 100
                stream.on_progress(chunk, fh, bytes_remaining)
        stream.on_complete(fh)

    def progress_finish(self,data_app, label):
        name = self.main_pointer.youtube_choice[self.main_pointer.counter - 1].default_filename
        data_app.insert_row([name, os.getcwd()])
        label.setText("Completed")

    def create_downloaded_layout(self):
        if self.data_app.get():
            data = self.arrange_data(self.data_app.get())
            for years in reversed(data):
                for months in reversed(years):
                    multiple_anchor = None
                    for days in reversed(months):
                        if not len(months) > 1:
                            widget = DownloadWidget(len(months), self.formatting(days[1], days[2], days[3]))
                            self.addWidget(widget)
                        else:
                            if not multiple_anchor:
                                multiple_anchor = DownloadWidget(len(months), self.formatting(days[1], days[2], days[3]))
                                self.addWidget(multiple_anchor)
                            else:
                                prev_text = multiple_anchor.text()
                                multiple_anchor.setText(prev_text+ self.formatting(days[1], days[2]))
                            


    def formatting(self, name, location, date = None):
        formatted_str = None
        wid = QFontMetrics(QFont()).boundingRect(name).width()
        rect_words_len = (W_WIDTH/1.5 * len(name))/ wid
        for j in range(0, int(rect_words_len/ 1.5)):
            if date:
                date = " " + date
        for i in range(0, int(rect_words_len/4)):
            name = " "+name
            location = " " + location
        if date:
            formatted_str = date + "\n" + name + "\n"+location
        else:
            formatted_str = "\n" + name + "\n"+location
        return formatted_str

    def arrange_data(self, raw_data):
        raw_data = sorted(raw_data, key = lambda element:self.keyer(element,"Y"))
        year_sort = self.__sort_(raw_data, "Y")
        month_sort = self.__sort_m(year_sort)
        day_sort = self.__sort_d(month_sort)
        return day_sort


    def keyer(self, element, key):
        if key == "Y":
            return int(element[-1].split("-")[-1])
        elif key == "M":
            return int(element[-1].split("-")[1])
        elif key == "D":
            return int(element[-1].split("-")[0])

    def __sort_(self, raw_data, key):
        overall_list = []
        sub_list = []
        starter = self.keyer(raw_data[0], key)
        for i in raw_data:
            if starter == self.keyer(i, key):
                sub_list.append(i)
            else:
                overall_list.append(sub_list)
                sub_list = []
                starter = self.keyer(i, key)
                sub_list.append(i)
        overall_list.append(sub_list)
        return overall_list

    def __sort_m(self, year_sort):
        month_sort = []
        for year in year_sort:
            month = sorted(year, key = lambda element:self.keyer(element, "M"))
            month_sort.append(self.__sort_(month, "M"))
        return month_sort

    def __sort_d(self, month_sort):
        day_sort = []
        for years in month_sort:
            for month in years:
                day = sorted(month, key = lambda element:self.keyer(element, "D"))
                day_sort.append(self.__sort_(day, "D"))
        return day_sort
