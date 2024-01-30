import os
import sys

import requests
from io import BytesIO
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

SCREEN_SIZE = [800, 600]
# Тест

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QLabel(self)
        self.map_ll = [37.530887, 55.703118]
        self.map_l = 'map'
        self.map_zoom = 12
        self.getImage()
        self.initUI()
        self.delta = 0.1

    def getImage(self):
        map_request = (f"http://static-maps.yandex.ru/1.x/?ll={self.map_ll[0]},{self.map_ll[1]}"
                       f"&l={self.map_l}&z={self.map_zoom}")
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.pixmap.load(self.map_file)
        self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.pixmap = QPixmap(self.map_file)
        self.image.move(0, 0)
        self.image.resize(1000, 600)
        self.image.setPixmap(self.pixmap)

        self.coord_label = QLabel(self)
        self.coord_label.move(650, 10)
        self.coord_label.setText('Введите координаты:')

        self.coord = QLineEdit(self)
        self.coord.setText(str(self.map_ll[0])[:5] + ' ' + str(self.map_ll[1])[:5])
        self.coord.setGeometry(650, 50, 100, 50)

        self.but = QPushButton(self)
        self.but.setGeometry(650, 100, 100, 50)
        self.but.setText('Обновить')
        self.but.clicked.connect(self.reload)

        self.laybut = QPushButton(self)
        self.laybut.setGeometry(650, 150, 100, 50)
        self.laybut.setText('Сменить слой')
        self.laybut.clicked.connect(self.layer)

        self.srch = QLineEdit(self)
        self.srch.setGeometry(650, 300, 100, 50)

        self.search_label = QLabel(self)
        self.search_label.move(630, 280)
        self.search_label.setText('Введите название места:')

        self.srcbut = QPushButton(self)
        self.srcbut.setGeometry(650, 350, 100, 50)
        self.srcbut.setText('Искать')
        self.srcbut.clicked.connect(self.search)

    def reload(self):
        try:
            self.map_ll[0], self.map_ll[1] = map(float, self.coord.text().split())
            self.getImage()
        except Exception:
            pass

    def layer(self):
        if self.map_l == 'map':
            self.map_l = 'sat'
        elif self.map_l == 'sat':
            self.map_l = 'sat,skl'
        else:
            self.map_l = 'map'
        self.getImage()

    def search(self):
        try:
            toponym_to_find = self.srch.text()
            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
            geocoder_params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": toponym_to_find,
                "format": "json"}
            resp = requests.get(geocoder_api_server, params=geocoder_params)
            if not resp:
                sys.exit(0)
            json_response = resp.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            self.map_ll[0], self.map_ll[1] = float(toponym_longitude), float(toponym_lattitude)

            map_params = {
                "ll": ",".join([toponym_longitude, toponym_lattitude]),
                "l": "map",
                "pt": f'{toponym_longitude},{toponym_lattitude}'
            }

            map_api_server = "http://static-maps.yandex.ru/1.x/"
            resp = requests.get(map_api_server, params=map_params)

            self.pixmap.loadFromData(BytesIO(resp.content).getvalue())
            self.map_zoom = 20
            self.image.setPixmap(self.pixmap)
        except Exception:
            self.srch.setText('Объект не найден')


    def keyPressEvent(self, event):
        key = event.key()
        self.setFocus()
        if key == Qt.Key_Left:
            self.map_ll[0] -= self.delta
        if key == Qt.Key_Right:
            self.map_ll[0] += self.delta
        if key == Qt.Key_Up:
            self.map_ll[1] += self.delta
        if key == Qt.Key_Down:
            self.map_ll[1] -= self.delta
        if key == Qt.Key_PageUp and self.map_zoom > 0:
            self.map_zoom -= 1
        if key == Qt.Key_PageDown and self.map_zoom <= 21:
            self.map_zoom += 1
        self.coord.setText(str(self.map_ll[0])[:5] + ' ' + str(self.map_ll[1])[:5])
        self.getImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
