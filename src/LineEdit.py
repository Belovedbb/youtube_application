from PyQt5.QtWidgets import QApplication , QLineEdit, QSizePolicy, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush, QImage, QBitmap\
    ,QPixmap, QRegion, QFontMetrics, QFont
from PyQt5.QtCore import QRect, QPoint, Qt, QLineF, QSize

class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        self.static, self.counter = range(2)
        super(LineEdit, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.IBeamCursor)
        self.cursorPen = QPen()
        self.cursorPen.setColor(QColor("black"))
        self.cursor_width = None
        self.previous_character_width = 0
        self.cursor_offset = 0
        
    def sizeHint(self):
        return QSize(50, 20)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gray_composite = round((50.2*255)/100)
        pen = QPen(QColor(gray_composite, gray_composite, gray_composite, 255))
        pen.setWidthF(0.8)
        pen.setCapStyle(Qt.RoundCap)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        self.draw_border(painter)
        self.draw_inline(painter)
        pen = QPen(QColor("black"))
        pen.setWidthF(0.8)
        painter.setPen(pen)
        text = self.get_characters_size(self.text())
        self.draw_text(painter, text)

    def draw_inline(self, painter):
        self.text_origin_x, self.text_origin_y = 0, int(self.height() - (self.height() * (1/2.5)))
        painter.drawLine(self.text_origin_x, self.text_origin_y,\
             self.text_origin_x + self.width() - self.padding, self.text_origin_y)

    def draw_border(self, painter):
        self.padding = 3
        self.angle_x, self.angle_y = 20.0, 15.0
        self.box_rect = QRect(0,0, self.width() - self.padding, self.height() -self.padding )
        painter.drawRoundedRect(self.box_rect, self.angle_x, self.angle_y)

    def get_characters_size(self, words):
        character_width = self.fontMetrics().boundingRect(words).width()
        character_width = character_width + (self.padding )
        if  round(character_width) > round(self.width()):
            if self.counter == 1:
                self.static = len(words)
                self.counter += 1
        elif words.rfind("...") is not -1:
            self.static, self.counter = range(2)
        return words, character_width

    def draw_text(self, painter, text):
        #define angles
        angle_x_ , angle_y_= self.text_origin_x, self.text_origin_y
        if text[1]+self.padding < self.box_rect.width():
            #to measure the height from the origin it is angle y + angle y minus and half of it
            painter.drawText( angle_x_ + self.padding, 2 * angle_y_ - (angle_y_ * 0.5), text[0] )
        else:
            self.width_ellipse = int(self.box_rect.width()/self.get_characters_size(" ")[1])
            painter.drawText(angle_x_ + self.padding,  2 * angle_y_ - (angle_y_ * 0.5),
                 text[0][0:self.width_ellipse])
            original_font  = painter.font()
            mag_font = QFont()
            mag_font.setBold(True)
            mag_font.setPointSize(8)
            painter.setFont(mag_font)
            painter.drawText(angle_x_ + self.padding, angle_y_ - (angle_y_ * 0.25),\
                 self.text_reverse(text[0][self.width_ellipse - (self.padding * 2):], self.box_rect.width()))
            painter.setFont(original_font)
        self.draw_cursor( painter, text[1])
    
    def text_reverse(self, text, rect_width):
        #max number of characters the rect can contain
        rect_width_chars = int((len(text) * rect_width) / self.get_characters_size(text)[1])
        if self.get_characters_size(text)[1] < rect_width:
            space_padding_size = rect_width_chars - len(text)
            for i in range(0, space_padding_size):
                text = " " + text
        else:
            diff = (len(text) - rect_width_chars)
            text = text[ diff + (self.padding * 2) : len(text)]
        return text
        
    def setCursorColor(self, color):
        self.cursorPen.setColor(color)

    def draw_cursor(self, painter, character_width_):
        prev_pen = painter.pen()
        painter.setPen(self.cursorPen)
        self.ellipsis_padding = 8
        if self.cursor_width == None:
            character_width = character_width_
            #handle mouse press event
        else:
            if (character_width_ - self.previous_character_width) != 0:
                self.cursor_offset += (character_width_ - self.previous_character_width)
            character_width = self.cursor_width + self.cursor_offset

        #draw based on border
        if self.fontMetrics().boundingRect(self.text()).width() <= self.angle_y:
            painter.drawLine(character_width , self.text_origin_y + (self.text_origin_y * 0.1 ),\
                character_width , (self.height() - (self.padding * 3)) )
        elif self.fontMetrics().boundingRect(self.text()).width() > self.box_rect.width() - self.angle_y and\
            self.fontMetrics().boundingRect(self.text()).width() < self.box_rect.width():
            painter.drawLine(character_width , self.text_origin_y + (self.text_origin_y * 0.1 ),\
                character_width , (self.height() - (self.padding * 3)) )
        else:
            painter.drawLine(character_width , self.text_origin_y + (self.text_origin_y * 0.1 ),\
                character_width , (self.height() - (self.padding)) )

        self.previous_character_width = character_width_
        painter.setPen(prev_pen)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        boundary_offset = self.angle_x
        if event.x() <= self.fontMetrics().boundingRect(self.text()).width() + boundary_offset:
            self.cursor_width = event.x() + self.padding
        else:
            self.cursor_width = self.fontMetrics().boundingRect(self.text()).width()  + self.padding