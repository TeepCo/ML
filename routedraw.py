import datetime

from PyQt5.QtGui import QPainter,QColor, QImage, QBrush
import pandas as pd
import matplotlib.pyplot as plt

class BitmapDrawer:
    def __init__(self, nw, se):
        self.se = se
        self.nw = nw

    def drawPoint(self, painter, w, lat, lon):
        x, y = self.transform(lat, lon, painter.device().width(), painter.device().height())
        painter.drawEllipse(x - w // 2, y - w // 2, w, w)

    def transform(self, lat, lon, width, height):
        x = width * (lon - self.nw[1]) / (self.se[1] - self.nw[1])
        y = height * (1 - (lat - self.se[0]) / (self.nw[0] - self.se[0]))
        return int(x), int(y)


def draw_image(image, routes, df):
    mn = 20
    mx = 200
    drawer = BitmapDrawer((50.5325933, 14.0653781), (50.5269597, 14.0754631))
    painter = QPainter(image)
    s = len(routes)
    cmap = plt.get_cmap("plasma")
    for p, index in enumerate(routes.index):
        duration = routes.loc[index, "duration"]
        if mn < duration <= mx:
            rgb = [int(x * 255) for x in cmap((duration-mn) / (mx-mn))[0:3]]
            for i in range(index, routes.loc[index, "end_beat"]):
                if i in df.index:
                    if not isinstance(df.loc[i, "locLat"], float): # some ambiguous indices
                        continue
                    painter.setPen(QColor(*rgb))
                    painter.setBrush(QColor(*rgb))
                    drawer.drawPoint(painter, 5, df.loc[i, "locLat"], df.loc[i, "locLon"])


class ColorPicker(object):
    def __init__(self, cmap, n):
        self.cmap = cmap
        self.cdict = {}
        self.i = 0
        self.n = n

    def get(self, key):
        if key not in self.cdict:
            self.cdict[key] = self.cmap((self.i % self.n) / self.n)
            self.i += 1
        return [int(x * 255) for x in self.cdict[key][0:3]]


def draw_days(image, routes, df):
    colorpicker = ColorPicker(plt.get_cmap("plasma"), 3)
    drawer = BitmapDrawer((50.5325933, 14.0653781), (50.5269597, 14.0754631))
    painter = QPainter(image)
    s = len(routes)
    for p, index in enumerate(routes.index):
        date = datetime.datetime.fromtimestamp(routes.loc[index, "end_beat"]).date()
        if (datetime.date(2021,3,16) <= date <= datetime.date(2021,3,16) or
            date == datetime.date(2021,2,25)):
            rgb = colorpicker.get(date)
            for i in range(index, routes.loc[index, "end_beat"]):
                if i in df.index:
                    if not isinstance(df.loc[i, "locLat"], float): # some ambiguous indices
                        continue
                    painter.setPen(QColor(*rgb))
                    painter.setOpacity(0.05)
                    painter.setBrush(QColor(*rgb))
                    drawer.drawPoint(painter, 5, df.loc[i, "locLat"], df.loc[i, "locLon"])


image = QImage("background.png")
routes = pd.read_csv("data/routes_01.csv", index_col="beat")
df = pd.read_csv("data/onesec_all_01.csv", index_col="beat")
draw_days(image, routes, df)
image.save("routes-draw.png")