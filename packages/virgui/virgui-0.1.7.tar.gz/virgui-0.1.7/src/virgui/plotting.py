from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6 import QtWidgets


# based on https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
class PlottingWidget(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.static_canvas = FigureCanvas(Figure())
        self.plot_toolbar = NavigationToolbar(self.static_canvas)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.plot_toolbar)
        self.layout().addWidget(self.static_canvas)

    # this is not the correct way to do it according to the matplotlib docs
    # but finesse returns a new figure object, so I can't update the existing one
    # except by replacing it.
    def update_figure(self, fig):
        temp_static_canvas = FigureCanvas(fig)
        temp_toolbar = NavigationToolbar(temp_static_canvas)

        self.layout().replaceWidget(self.plot_toolbar, temp_toolbar)
        self.layout().replaceWidget(self.static_canvas, temp_static_canvas)

        self.static_canvas = temp_static_canvas
        self.temp_toolbar = NavigationToolbar
