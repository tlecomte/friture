from PyQt5.QtGui import QPolygonF
import numpy as np

def arrays_to_qpolygon(x_array, y_array):
    if x_array.size != y_array.size:
        raise ValueError("Input arrays must have the same size")

    if x_array.ndim != 1 or y_array.ndim != 1:
        raise ValueError("Input arrays must be 1D")

    size = x_array.size

    polygon = QPolygonF(size)
    polygon_data = polygon.data()
    polygon_data.setsize(2 * np.dtype(np.float64).itemsize * size)  # 2 float64 coordinates per point

    polygon_array = np.frombuffer(polygon_data, np.float64)
    polygon_array[: (size - 1) * 2 + 1 : 2] = np.array(x_array, dtype=np.float64, copy=False)
    polygon_array[1 : (size - 1) * 2 + 2 : 2] = np.array(y_array, dtype=np.float64, copy=False)

    return polygon
