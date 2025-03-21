import base64


class Figure(object):
    FILE_PATH = "figure.svg"

    def __init__(self):
        self.svg = ""

    def upload(self):
        with open(self.FILE_PATH, "rb") as f:
            self.svg = str(base64.b64encode(f.read()), "utf-8")

    def getPayload(self):
        return {"type": "graph", "payload": self.svg}


class MatplotlibFigure(Figure):
    def __init__(self, canvas, height, width):
        super().__init__()
        inches_y = height / 72
        inches_x = width / 72
        canvas.figure.set_size_inches(inches_x, inches_y)
        canvas.print_svg(self.FILE_PATH)
        self.upload()


class FiguresManager(object):
    FIGURES = []
    HEIGHT = 320
    WIDTH = 320

    @classmethod
    def setPlotSizes(cls, height, width):
        cls.HEIGHT = height
        cls.WIDTH = width

    @classmethod
    def clearFigures(cls):
        cls.FIGURES = []

    @classmethod
    def getFigures(cls):
        return cls.FIGURES

    @classmethod
    def matplotlib_show(cls, canvas):
        cls.FIGURES.append(MatplotlibFigure(canvas, cls.HEIGHT, cls.WIDTH))
