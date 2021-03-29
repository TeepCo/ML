from datetime import datetime
from hashlib import md5
from pathlib import Path

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPainter, QPaintEvent, QColor, QImage, QBrush, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy, QSlider, QAction
import pandas as pd


def dateformat(posix):
    return datetime.fromtimestamp(posix).strftime("%d.%m %H:%M:%S")


def read_data() -> pd.DataFrame:
#    files =  ["onesec_01_2020-11-27.csv", "onesec_01_2020-11-30.csv"]
    files = ["onesec_02_2020-11-26.csv", "onesec_02_2020-11-27.csv",
             "onesec_02_2020-11-30.csv",
             "onesec_02_2020-12-01.csv", "onesec_02_2020-12-02.csv",
             "onesec_02_2020-12-03.csv", "onesec_02_2020-12-04.csv",
             "onesec_02_2020-12-08.csv", "onesec_02_2020-12-09.csv",
             "onesec_02_2020-12-10.csv", "onesec_02_2020-12-11.csv"
             ]
    dfs = [pd.read_csv(file) for file in files]
    df = pd.concat(dfs)
    df.name = md5("".join(files).encode(encoding="utf-8")).hexdigest()
    return df


class MapView(QWidget):
    def __init__(self, map, nw, se, df, out):
        super().__init__()
        self.stopped = False
        self.delta = 10
        self.dir = 1
        self.nw = nw
        self.se = se
        self.i = 0
        self.df = df
        self.out = out
        if Path(self.df.name+".png").exists():
            self.map = QImage(self.df.name+".png")
        else:
            self.map = QImage(map)
            self.map.convertToFormat(QImage.Format_ARGB32_Premultiplied)
            self.drawPixmap()
            self.map.save(self.df.name+".png")
        self.layer = QImage(self.map.size(), QImage.Format_ARGB32_Premultiplied)
        self.layer.fill(Qt.transparent)

    def drawPixmap(self):
        painter = QPainter()
        painter.begin(self.map)
        painter.setOpacity(0.20)
        painter.setPen(QColor(0,0,0))
        painter.setBrush(QColor(0,0,0))
        for i in range(len(self.df)):
            self.drawPoint(painter, 2, self.df.iloc[i, 2], self.df.iloc[i, 3])

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.drawImage(self.rect(), self.map, self.map.rect())
        self.drawLayer()
        painter.drawImage(self.rect(), self.layer, self.layer.rect())
        vdist = int(self.df.iloc[self.i, 4])
        colorf = min(255, vdist*3)
        painter.setPen(QColor(colorf, 0, 255-colorf))
        painter.setBrush(QColor(colorf, 0, 255-colorf))
        self.drawPoint(painter, 20, self.df.iloc[self.i, 2], self.df.iloc[self.i, 3])
        painter.end()

    def drawLayer(self):
        painter = QPainter()
        painter.begin(self.layer)
        if self.df.iloc[self.i, 5] > 0:
            color = QColor("red" if self.dir == 1 else "blue")
            painter.setPen(color)
            painter.setBrush(color)
            self.drawPoint(painter, 3, self.df.iloc[self.i, 2], self.df.iloc[self.i, 3])
        if self.i % 60 == 30:
            painter.setOpacity(0.96)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(self.layer.rect(), QBrush(QColor(0, 0, 0)))
        painter.end()

    def transform(self, lat, lon, width, height):
        x = width * (lon - self.nw[1]) / (self.se[1] - self.nw[1])
        y = height * (1 - (lat - self.se[0]) / (self.nw[0] - self.se[0]))
        return int(x), int(y)

    def drawPoint(self, painter, w, lat, lon):
        x, y = self.transform(lat, lon, painter.device().width(), painter.device().height())
        painter.drawEllipse(x-w//2, y-w//2, w, w)

    def step(self):
        if self.dir == 1 and self.i == len(self.df) - 2:
            self.changeDir()
            self.stop()
        if self.dir == -1 and self.i == 1:
            self.changeDir()
            self.stop()
        self.i += self.dir
        time = dateformat(self.df.iloc[self.i, 1] / 1000)
        vdist = self.df.iloc[self.i, 4]
        hdist = self.df.iloc[self.i, 5]
        self.out.setText(f"Time: {time}, vdist: {vdist}, hdist: {hdist} dir: {self.dir}")
        self.update()

    def resetTimer(self, value):
        self.delta = value
        timer.setInterval(self.delta)

    def changeDelta(self, k, slider: QSlider):
        self.delta = min(int(self.delta * k) + 1, slider.maximum())
        print(self.delta)
        slider.setValue(self.delta)
        timer.setInterval(self.delta)

    def stop(self):
        if self.stopped:
            timer.setInterval(self.delta)
            self.stopped = False
        else:
            timer.setInterval(1_000_000_000)
            self.stopped = True

    def changeDir(self):
        self.dir = -self.dir


def addAction(widget, shortcut, slot):
    a = QAction(window)
    a.setShortcut(QKeySequence(shortcut))
    a.triggered.connect(slot)
    widget.addAction(a)


app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
info = QLabel(f"Time:")
info.setStyleSheet("font-size: 20pt")
layout.addWidget(info)
view = MapView("background.png", (50.5325933, 14.0653781), (50.5269597, 14.0754631), read_data(), info)
view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
slider = QSlider(Qt.Horizontal)
slider.setMinimum(0)
slider.setMaximum(100)
slider.setValue(view.delta)
slider.valueChanged.connect(view.resetTimer)
layout.addWidget(slider)
layout.addWidget(view)
window.setLayout(layout)
window.showMaximized()
timer = QTimer(window)
timer.timeout.connect(view.step)
timer.start(view.delta)
addAction(window, Qt.Key_Space, view.stop)
addAction(window, Qt.Key_Right, lambda: view.changeDelta(2, slider))
addAction(window, Qt.Key_Left, lambda: view.changeDelta(0.5, slider))
addAction(window, Qt.Key_R, view.changeDir)
app.exec_()