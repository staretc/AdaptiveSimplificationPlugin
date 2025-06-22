from qgis.core import QgsVectorLayer, QgsProject, QgsFeatureRequest, QgsVectorFileWriter, QgsGeometry, QgsPointXY, QgsFeature, Qgis
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtCore import QSettings
from qgis.utils import QgsMessageBar
from pathlib import Path
import importlib.util
import os
import sys
#import processing
#sys.path.append(os.path.dirname(__file__))
#import AdaptiveSimplificationCore

class GeometricSimplificationPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None

    def initGui(self):
        self.action = QAction("Run Simplification Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        from .geometricsimplification_dialog import GeometricSimplificationDialog
        self.dlg = GeometricSimplificationDialog()
        if self.dlg.exec_():
            # Получение параметров из диалога
            scaleValue = float(self.dlg.scaleValue.text())
            lineDeviation = float(self.dlg.lineDeviation.text())
            orthogonalSegmentSize = float(self.dlg.orthogonalSegmentSize.text())
            rightAngleDeviation = float(self.dlg.rightAngleDeviation.text())
            schematicSegmentSize = float(self.dlg.schematicSegmentSize.text())
            inhibition = float(self.dlg.inhibition.text())
            outputScale = float(self.dlg.outputScale.text())
            outputOrthogonalSegmentSize = float(self.dlg.outputOrthogonalSegmentSize.text())
            simplificationParam = float(self.dlg.simplificationParam.text())

            # Получение выбранного слоя из QComboBox
            layer = self.dlg.layerComboBox.currentData()
            if not layer or not isinstance(layer, QgsVectorLayer):
                self.iface.messageBar().pushMessage("Error", "No valid layer selected", level=Qgis.MessageLevel.Critical)
                return

            if not layer.isValid():
                self.iface.messageBar().pushMessage("Error", "Layer is not valid", level=Qgis.MessageLevel.Critical)
                return

            module_name = "AdaptiveSimplificationCore"
            file_path = os.path.join(os.path.dirname(__file__), f"{module_name}.cp312-win_amd64.pyd")
            if not os.path.exists(file_path):
                self.iface.messageBar().pushMessage("Error", f"Module not found: {file_path}", level=Qgis.MessageLevel.Critical)
                return
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Извлечение точек
            input_data = module.MapData()
            vertex_list = []
            obj_id = 0
            for feature in layer.getFeatures():
                geometry = feature.geometry()
                if geometry:
                    polyline = []
                    vertex_id = 0
                    for point in geometry.vertices():
                        weighted_vertex = module.WeightedVertex(
                            point.x(), point.y(), obj_id, vertex_id, 0.0
                        )
                        polyline.append(weighted_vertex)
                        vertex_id += 1
                    vertex_list.append(polyline)
                    obj_id += 1
            input_data.set_vertex_list(vertex_list)

            # Упрощение на C++
            try:
                simplified_result = module.run_simplification(
                    input_data,
                    scaleValue=scaleValue,
                    lineDeviation=lineDeviation,
                    orthogonalSegmentSize=orthogonalSegmentSize,
                    rightAngleDeviation=rightAngleDeviation,
                    schematicSegmentSize=schematicSegmentSize,
                    inhibition=inhibition,
                    outputScale=outputScale,
                    outputOrthogonalSegmentSize=outputOrthogonalSegmentSize,
                    simplificationParam=simplificationParam
                )
                # Получение MHD
                mhd = module.get_last_mhd()
            except Exception as e:
                self.iface.messageBar().pushMessage("Error", f"Simplification failed: {str(e)}", level=Qgis.MessageLevel.Critical)
                return
            
            # Формирование уникального имени выходного файла
            base_output_name = layer.name() + "_simplified"
            output_dir = os.path.dirname(layer.source())
            output_extension = ".shp"
            output_file_name = base_output_name + output_extension
            output_path = os.path.join(output_dir, output_file_name)
            counter = 1
            while os.path.exists(output_path):
                output_file_name = f"{base_output_name}_{counter}{output_extension}"
                output_path = os.path.join(output_dir, output_file_name)
                counter += 1
            
            
            # Настройка опций сохранения
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.fileEncoding = "UTF-8"
            writer = QgsVectorFileWriter.create(
                str(output_path),
                layer.fields(),
                layer.wkbType(),
                layer.crs(),
                QgsProject.instance().transformContext(),
                options
            )
            if writer.hasError() != QgsVectorFileWriter.NoError:
                self.iface.messageBar().pushMessage("Error", "Failed to create output layer", level=Qgis.MessageLevel.Critical)
                return

            # Заполнение нового слоя
            for polyline in simplified_result.get_vertex_list():
                points = [QgsPointXY(v.get_x(), v.get_y()) for v in polyline]
                geometry = QgsGeometry.fromPolylineXY(points)
                feature = QgsFeature()
                feature.setGeometry(geometry)
                writer.addFeature(feature)

            del writer
            self.iface.messageBar().pushMessage("Success", f"Layer simplified and saved to {output_path}", level=Qgis.MessageLevel.Info)
            self.iface.messageBar().pushMessage(f"Modified Hausdorf Distance: {mhd}")
            QgsProject.instance().addMapLayer(QgsVectorLayer(str(output_path), output_file_name, "ogr"))

            # Вызов функции упрощения
            #success = module.run_simplification(
            #    inputFile,
            #    scaleValue,
            #    lineDeviation,
            #    orthogonalSegmentSize,
            #    rightAngleDeviation,
            #    schematicSegmentSize,
            #    inhibition,
            #    outputScale,
            #    outputOrthogonalSegmentSize,
            #    simplificationParam
            #)
            #if success:
            #    input_path = Path(inputFile)
            #    output_file_name = input_path.stem + "_simplified.shp"
            #    output_path = input_path.parent / output_file_name
            #    self.iface.messageBar().pushMessage("Success", f"Layer simplified and saved to {output_path}")
            #else:
            #    self.iface.messageBar().pushMessage("Error", "Simplification failed")