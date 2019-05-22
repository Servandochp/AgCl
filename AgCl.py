
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtCore import QFileInfo, Qt, QDate
import numpy as np
from string import Template
import os


class MiGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)
        # self.setTransformationAnchor(self.AnchorUnderMouse)

        self._zoom = 0
        self.scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self._photo)
        self.setScene(self.scene)

        self.escala = []
        self.linea = []
        self.puntos = []
        self.distancias = []
        self.distanciasreales = []

        self.apintar = None

        self.existeescala = False
        self.existelinea = False
        self.valor_de_escala = None
        self.empty = True

    def hasPhoto(self):
        return not self.empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self.empty = False
            # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self.empty = True
            # self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def paintObject(self, e):
        if self.apintar != None:
            object = self.apintar
            if object == 1:  # Escala
                if self.existeescala == False:
                    self.escala = []
                    pen = QtGui.QPen(Qt.green)
                    self.laescala = QGraphicsLineItem(self.startX, self.startY, e.x(), e.y())
                    self.laescala.setPen(pen)
                    self.scene.addItem(self.laescala)
                    self.setScene(self.scene)
                    self.escala.extend((self.startX, self.startY, e.x(), e.y()))
                    self.existeescala = True
                    self.apintar = None
            elif object == 2:  # Linea
                if self.existelinea == False:
                    self.linea = []
                    pen = QtGui.QPen(Qt.red)
                    self.lalinea = QGraphicsLineItem(self.startX, self.startY, e.x(), e.y())
                    self.lalinea.setPen(pen)
                    self.scene.addItem(self.lalinea)
                    self.setScene(self.scene)
                    self.linea.extend((self.startX, self.startY, e.x(), e.y()))
                    self.existelinea = True
                    self.apintar = None
            elif object == 3:  # Puntos
                pen = QtGui.QPen(Qt.red)
                brush = QtGui.QBrush(Qt.SolidPattern)
                self.scene.addItem(self.scene.addEllipse(e.x(), e.y(), 2, 2, pen, brush))
                self.puntos.append(e.__pos__())
                self.setScene(self.scene)
                print(self.puntos)
                print(e.__pos__())

    def borrarescala(self):
        if self.existeescala:
            self.scene.removeItem(self.laescala)
            self.existeescala = False

    def borrarlinea(self):
        if self.existelinea:
            self.scene.removeItem(self.lalinea)
            self.existelinea = False

    def borrarpunto(self, puntiko):
        self.puntos.pop(puntiko)
        self.scene.removeItem(puntiko)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            e = QtCore.QPointF(self.mapToScene(event.pos()))
            self.startX = e.x()
            self.startY = e.y()
        if event.button() == Qt.RightButton:
            self._dragPos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            e = QtCore.QPointF(self.mapToScene(event.pos()))
            self.paintObject(e)
        if self.cursor() == Qt.ClosedHandCursor:
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if event.button() == Qt.LeftButton:
            e = QtCore.QPointF(self.mapToScene(event.pos()))
        if event.buttons() == Qt.RightButton:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())


class About(QtWidgets.QLabel):

    def __init__(self):
        QtWidgets.QLabel.__init__(self,
                        "pAgCl 1.0\n\nPor Servando Chinchón Payá, 2018\n\nPor favor no dude en comentar cualquier sugerencia\n\nservando@ietcc.csic.es\n\n¡Gracias!")
        self.setAlignment(QtCore.Qt.AlignCenter)

    def initUI(self):
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = app.desktop().availableGeometry().centre()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(899, 496)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icono.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.graphicsView = MiGraphicsView()
        self.graphicsView.setAutoFillBackground(False)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_3.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.tabla = QtWidgets.QTableWidget(self.centralwidget)
        self.tabla.setEnabled(False)
        self.tabla.setObjectName("tabla")
        self.tabla.setColumnCount(0)
        self.tabla.setRowCount(0)
        self.gridLayout_2.addWidget(self.tabla, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 2, 1, 1)
        self.pb_calcular = QtWidgets.QPushButton(self.centralwidget)
        self.pb_calcular.setEnabled(False)
        self.pb_calcular.setObjectName("pb_calcular")
        self.gridLayout_2.addWidget(self.pb_calcular, 2, 1, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.rb_puntos = QtWidgets.QRadioButton(self.centralwidget)
        self.rb_puntos.setEnabled(False)
        self.rb_puntos.setObjectName("rb_puntos")
        self.gridLayout.addWidget(self.rb_puntos, 5, 0, 1, 2)
        self.le_escala = QtWidgets.QLineEdit(self.centralwidget)
        self.le_escala.setEnabled(False)
        self.le_escala.setObjectName("le_escala")
        self.gridLayout.addWidget(self.le_escala, 3, 0, 1, 1)
        self.rb_linea = QtWidgets.QRadioButton(self.centralwidget)
        self.rb_linea.setEnabled(False)
        self.rb_linea.setObjectName("rb_linea")
        self.gridLayout.addWidget(self.rb_linea, 4, 0, 1, 1)
        self.pb_OK = QtWidgets.QPushButton(self.centralwidget)
        self.pb_OK.setEnabled(False)
        self.pb_OK.setObjectName("pb_OK")
        self.gridLayout.addWidget(self.pb_OK, 3, 1, 1, 1)
        self.rb_escala = QtWidgets.QRadioButton(self.centralwidget)
        self.rb_escala.setEnabled(False)
        self.rb_escala.setObjectName("rb_escala")
        self.gridLayout.addWidget(self.rb_escala, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 899, 21))
        self.menubar.setObjectName("menubar")
        self.menuArchivo = QtWidgets.QMenu(self.menubar)
        self.menuArchivo.setObjectName("menuArchivo")
        self.menuInformacion = QtWidgets.QMenu(self.menubar)
        self.menuInformacion.setObjectName("menuInformacion")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbrir_imagen = QtWidgets.QAction(MainWindow)
        self.actionAbrir_imagen.setObjectName("actionAbrir_imagen")
        self.actionCrear_informe = QtWidgets.QAction(MainWindow)
        self.actionCrear_informe.setEnabled(False)
        self.actionCrear_informe.setObjectName("actionCrear_informe")
        self.actionImagen = QtWidgets.QAction(MainWindow)
        self.actionImagen.setObjectName("actionImagen")
        self.actionResultados = QtWidgets.QAction(MainWindow)
        self.actionResultados.setObjectName("actionResultados")
        self.actionSalir = QtWidgets.QAction(MainWindow)
        self.actionSalir.setObjectName("actionSalir")
        self.actionAyuda = QtWidgets.QAction(MainWindow)
        self.actionAyuda.setObjectName("actionAyuda")
        self.actionSobre_el_programa = QtWidgets.QAction(MainWindow)
        self.actionSobre_el_programa.setObjectName("actionSobre_el_programa")
        self.actionGuardar_imagen = QtWidgets.QAction(MainWindow)
        self.actionGuardar_imagen.setEnabled(False)
        self.actionGuardar_imagen.setObjectName("actionGuardar_imagen")
        self.menuArchivo.addAction(self.actionAbrir_imagen)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionCrear_informe)
        self.menuArchivo.addAction(self.actionGuardar_imagen)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionSalir)
        self.menuInformacion.addAction(self.actionAyuda)
        self.menuInformacion.addAction(self.actionSobre_el_programa)
        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuInformacion.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.titulos_tabla = ["posición", "ditancia(px)", "distancia(valor real)"]

        self.actionAbrir_imagen.triggered.connect(self.loadImage)

        self.rb_escala.toggled.connect(self.pe)
        self.pb_OK.clicked.connect(self.ok)
        self.rb_linea.toggled.connect(self.pl)
        self.rb_puntos.toggled.connect(self.pp)
        self.pb_calcular.clicked.connect(self.calcular)
        self.actionGuardar_imagen.triggered.connect(self.guardar_imagen)
        self.actionCrear_informe.triggered.connect(self.report)
        self.actionSalir.triggered.connect(self.close_application)
        self.actionSobre_el_programa.triggered.connect(self.sobre_programa)

        self.ayuda = 'Tutorial.pdf'
        self.actionAyuda.triggered.connect(self.Ayuda)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Penetración de cloruros. Tinción AgCl (versión beta)"))
        self.pb_calcular.setText(_translate("MainWindow", "Calcular"))
        self.rb_puntos.setText(_translate("MainWindow", "Puntos"))
        self.rb_linea.setText(_translate("MainWindow", "Linea"))
        self.pb_OK.setText(_translate("MainWindow", "OK"))
        self.rb_escala.setText(_translate("MainWindow", "Escala"))
        self.menuArchivo.setTitle(_translate("MainWindow", "Archivo"))
        self.menuInformacion.setTitle(_translate("MainWindow", "Información"))
        self.actionAbrir_imagen.setText(_translate("MainWindow", "Abrir imagen"))
        self.actionAbrir_imagen.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionCrear_informe.setText(_translate("MainWindow", "Crear informe"))
        self.actionCrear_informe.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.actionImagen.setText(_translate("MainWindow", "Imagen"))
        self.actionResultados.setText(_translate("MainWindow", "Resultados"))
        self.actionSalir.setText(_translate("MainWindow", "Salir"))
        self.actionSalir.setShortcut(_translate("MainWindow", "Shift+S"))
        self.actionAyuda.setText(_translate("MainWindow", "Ayuda"))
        self.actionAyuda.setShortcut(_translate("MainWindow", "F1"))
        self.actionSobre_el_programa.setText(_translate("MainWindow", "Sobre el programa"))
        self.actionGuardar_imagen.setText(_translate("MainWindow", "Guardar imagen"))
        self.actionGuardar_imagen.setShortcut(_translate("MainWindow", "Ctrl+G"))

    def Ayuda(self):
        os.startfile(self.ayuda)

    def sobre_programa(self):
        self.pop = About()
        self.pop.resize(555, 333)
        self.pop.setWindowTitle("Sobre pAgCl")
        self.pop.show()

    def close_application(self):
        choice = QMessageBox.information(None, 'Información',
                                         "¿Estás seguro de que quieres salir?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def loadImage(self):
        name, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Abrir imagen')
        self.img = QtGui.QPixmap(name)
        self.graphicsView.setPhoto(self.img)
        self.filename = QFileInfo(name).fileName()
        if self.graphicsView.empty == False:
            self.rb_escala.setEnabled(True)
            self.rb_escala.setChecked(True)
            # self.pb_rehacerescala.setEnabled(True)
            self.le_escala.setEnabled(True)
            self.pb_OK.setEnabled(True)
            self.rb_linea.setEnabled(True)
            # self.pb_rehacerlinea.setEnabled(True)
            self.rb_puntos.setEnabled(True)
            self.tabla.setRowCount(0)
            self.tabla.setColumnCount(3)
            self.tabla.setHorizontalHeaderLabels(self.titulos_tabla)
            self.tabla.resizeColumnsToContents()
            self.tabla.setEnabled(True)
            self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
            self.pb_calcular.setEnabled(True)
            self.actionGuardar_imagen.setEnabled(True)
            self.actionCrear_informe.setEnabled(True)

    def guardar_imagen(self):
        name, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Guardar Imagen", "", "PNG(*.png);;JPEG(*.jpg)")
        if name == "":
            return
        if "." not in name:
            name += ".png"
        pixmap = QtGui.QPixmap(self.graphicsView.viewport().size())
        self.graphicsView.viewport().render(pixmap)
        pixmap.save(name)

    def pe(self):
        if self.rb_escala.isChecked():
            self.graphicsView.borrarescala()
            self.graphicsView.apintar = 1

    def pl(self):
        if self.rb_linea.isChecked():
            self.graphicsView.borrarlinea()
            self.graphicsView.apintar = 2

    def pp(self):
        if self.rb_puntos.isChecked():
            self.graphicsView.apintar = 3

    def ok(self):
        try:
            valor_escala = int(self.le_escala.text())
            self.graphicsView.valor_de_escala = valor_escala
        except ValueError:
            info = QMessageBox.information(None, 'Información', "Has de introducir un número entero, sin decimales", QMessageBox.Ok)
            if info == QMessageBox.Ok:
                self.le_escala.clear()

    def calcular(self):
        """
        Cálculo de la distancia entre los dos puntos de la escala, del valor del segmento o longitud de la escala
        """

        """
        y = mx + b
        """
        if len(self.graphicsView.linea) > 1:
            m = (self.graphicsView.linea[3] - self.graphicsView.linea[1]) / (self.graphicsView.linea[2] - self.graphicsView.linea[0])
            b = self.graphicsView.linea[1] - (m*self.graphicsView.linea[0])
            self.dist(m, b)
        """
        Mucho ojo porque las coordenadas reales en la foto son (x, -y). El (0,0) es la esquina superior izquierda
        """

        self.llenar_tabla()

    def dist(self, m, b):
        self.graphicsView.distancias.clear()
        self.graphicsView.distanciasreales.clear()
        for pto in self.graphicsView.puntos:
            dist = abs(m * pto.x() - pto.y() + b) / np.sqrt((m ** 2) + 1)
            self.graphicsView.distancias.append(dist)
        if self.graphicsView.existeescala and self.graphicsView.valor_de_escala:
            self.d_escala_pix = ((self.graphicsView.escala[2]-self.graphicsView.escala[0])**2 +
                                 (self.graphicsView.escala[3]-self.graphicsView.escala[1])**2)**(0.5)
            for i in self.graphicsView.distancias:
                dist_real = (self.graphicsView.valor_de_escala * i)/self.d_escala_pix
                self.graphicsView.distanciasreales.append(dist_real)
        else:
            pass

    def llenar_tabla(self):
        n = 0
        self.tabla.setRowCount(len(self.graphicsView.puntos))
        for item in self.graphicsView.puntos:
            self.tabla.setItem(n, 0, QTableWidgetItem(str(int(item.x())) + " , " + str(int(item.y()))))
            self.tabla.resizeColumnsToContents()
            n += 1
        if self.graphicsView.existelinea:
            m = 0
            for elemento in self.graphicsView.distancias:
                self.tabla.setItem(m, 1, QTableWidgetItem(str(int(elemento))))
                self.tabla.resizeColumnsToContents()
                m += 1
        if self.graphicsView.existeescala:
            k = 0
            for element in self.graphicsView.distanciasreales:
                self.tabla.setItem(k, 2, QTableWidgetItem(str(element)))
                self.tabla.resizeColumnsToContents()
                k += 1

    def report(self,):
        filein = open('plantilla_resultados.txt')
        src = Template(filein.read())

        fecha = QDate.currentDate()
        fecha2 = fecha.toString(Qt.DefaultLocaleLongDate)
        title = "La fotografía tratada es la: " + str(self.filename)
        date = str(fecha2)
        distancias = [str(x) for x in self.graphicsView.distanciasreales]
        media = np.mean(self.graphicsView.distanciasreales)
        distancia_media = str(media)
        pmax = np.amax(self.graphicsView.distanciasreales)
        d = {'title':title, 'date':date, 'distancias':'\n'.join(distancias), 'distancia_media':distancia_media, "pmax":pmax}
        result = src.substitute(d)

        name, _ = QFileDialog.getSaveFileName(None, 'Save file', "", "Text Files (*.txt)")
        filename = QFileInfo(name).fileName()
        if filename:
            file = open(name, 'w')
            text = result
            file.write(text)
            file.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

