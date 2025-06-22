from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel
from qgis.core import QgsProject, QgsVectorLayer

class GeometricSimplificationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplification Parameters")
        layout = QVBoxLayout()

        # Поля для ввода параметров
        self.scaleValue = QLineEdit("1000.0")
        self.lineDeviation = QLineEdit("0.25")
        self.orthogonalSegmentSize = QLineEdit("2.0")
        self.rightAngleDeviation = QLineEdit("15.0")
        self.schematicSegmentSize = QLineEdit("12.0")
        self.inhibition = QLineEdit("3.0")
        self.outputScale = QLineEdit("4000.0")
        self.outputOrthogonalSegmentSize = QLineEdit("2.0")
        self.simplificationParam = QLineEdit("0.5")

        # Добавляем QComboBox для выбора слоя
        self.layerComboBox = QComboBox()
        self.populate_layer_combobox()

        # Метки и поля
        layout.addWidget(QLabel("Select Layer"))
        layout.addWidget(self.layerComboBox)
        layout.addWidget(QLabel("Scale Value (m/mm):"))
        layout.addWidget(self.scaleValue)
        layout.addWidget(QLabel("Line Deviation (mm):"))
        layout.addWidget(self.lineDeviation)
        layout.addWidget(QLabel("Orthogonal Segment Size (mm):"))
        layout.addWidget(self.orthogonalSegmentSize)
        layout.addWidget(QLabel("Right Angle Deviation (degree):"))
        layout.addWidget(self.rightAngleDeviation)
        layout.addWidget(QLabel("Schematic Segment Size (mm):"))
        layout.addWidget(self.schematicSegmentSize)
        layout.addWidget(QLabel("Inhibition:"))
        layout.addWidget(self.inhibition)
        layout.addWidget(QLabel("Output Scale (m/mm):"))
        layout.addWidget(self.outputScale)
        layout.addWidget(QLabel("Output Orthogonal Segment Size (mm):"))
        layout.addWidget(self.outputOrthogonalSegmentSize)
        layout.addWidget(QLabel("Simplification Param:"))
        layout.addWidget(self.simplificationParam)

        self.ok_button = QPushButton("OK")
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
        self.ok_button.clicked.connect(self.accept)
    
    def populate_layer_combobox(self):
        # Заполняем QComboBox доступными векторными слоями
        self.layerComboBox.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                self.layerComboBox.addItem(layer.name(), layer)