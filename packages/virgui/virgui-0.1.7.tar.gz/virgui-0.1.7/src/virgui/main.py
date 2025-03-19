import sys

import finesse
from PySide6 import QtWidgets

from virgui.action_runner import ActionRunner
from virgui.kat_log import KatScriptLog
from virgui.katscript_viewer import KatScriptViewer
from virgui.model_layout import ModelLayout
from virgui.plotting import PlottingWidget

finesse.init_plotting()


class ZoomableGraphicsScene(QtWidgets.QGraphicsScene):

    def wheelEvent(self, event: QtWidgets.QGraphicsSceneWheelEvent) -> None:
        scale_factor = 1.15
        if event.delta() > 0:
            self.views()[0].scale(scale_factor, scale_factor)
        else:
            self.views()[0].scale(1 / scale_factor, 1 / scale_factor)
        event.accept()
        return super().wheelEvent(event)


# https://www.pythonguis.com/tutorials/pyside6-qgraphics-vector-graphics/
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VIRGUI")
        self.setFixedSize(900, 900)

        self.kat_text = KatScriptViewer()
        self.kat_log = KatScriptLog()
        self.model_layout = ModelLayout(
            katscript_listener=self.kat_text.update,
            katlog_listener=self.kat_log.update,
        )
        self.plotter = PlottingWidget()
        self.action_runner = ActionRunner(plotter=self.plotter)

        self.tabs = QtWidgets.QTabWidget()

        # layout tab
        self.tabs.addTab(self.model_layout, "Layout")

        # calculate tab
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setLayout(QtWidgets.QHBoxLayout())
        self.tabs.addTab(self.tab2, "Calculate")

        self.tab2.layout().addWidget(self.action_runner)
        self.tab2.layout().addWidget(self.plotter)

        # katscript tab
        self.tab3 = QtWidgets.QWidget()
        self.tab3.setLayout(QtWidgets.QHBoxLayout())
        self.tabs.addTab(self.tab3, "KatScript")
        self.tab3.layout().addWidget(self.kat_text)
        self.tab3.layout().addWidget(self.kat_log)


def main():
    app = QtWidgets.QApplication(sys.argv)

    w = Window()
    w.tabs.show()

    app.exec()


if __name__ == "__main__":
    main()
