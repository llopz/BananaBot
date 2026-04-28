import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional


ESPACIOS_COLOR = {
    "HSV":   cv2.COLOR_BGR2HSV,
    "YUV":   cv2.COLOR_BGR2YUV,
    "LAB":   cv2.COLOR_BGR2LAB,
    "HLS":   cv2.COLOR_BGR2HLS,
    "YCrCb": cv2.COLOR_BGR2YCrCb,
    "LUV":   cv2.COLOR_BGR2LUV,
    "XYZ":   cv2.COLOR_BGR2XYZ,
}


@dataclass
class Elemento:
    x: int
    y: int
    w: int
    h: int
    centro_x: int
    centro_y: int
    area: float
    proporcion: float
    tipo: str = "desconocido"


class BaseDetector:
    def __init__(self, config):
        self.config = config

    def _crear_mascara(
        self,
        frame,
        rango_bajo,
        rango_alto,
        espacio="HSV",
        erode_kernel=(3, 3),
        erode_iter=1,
        dilate_kernel=(3, 3),
        dilate_iter=1,
    ):
        codigo = ESPACIOS_COLOR.get(espacio, cv2.COLOR_BGR2HSV)
        convertida = cv2.cvtColor(frame, codigo)
        mascara = cv2.inRange(convertida, np.array(rango_bajo), np.array(rango_alto))

        erode_kernel = tuple(int(v) for v in erode_kernel)
        dilate_kernel = tuple(int(v) for v in dilate_kernel)
        erode_iter = int(erode_iter)
        dilate_iter = int(dilate_iter)

        if erode_iter > 0:
            kernel_erode = np.ones(erode_kernel, np.uint8)
            mascara = cv2.erode(mascara, kernel_erode, iterations=erode_iter)
        if dilate_iter > 0:
            kernel_dilate = np.ones(dilate_kernel, np.uint8)
            mascara = cv2.dilate(mascara, kernel_dilate, iterations=dilate_iter)

        return mascara, convertida

    def _detectar_elemento(self, frame, rango_bajo, rango_alto,
                        area_min_pct, area_max_pct,
                        prop_min, prop_max, tipo,
                        zona_y_inicio=0, zona_y_fin=None,
                        espacio="HSV",
                        erode_kernel=(3, 3), erode_iter=1,
                        dilate_kernel=(3, 3), dilate_iter=1):

        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * area_min_pct
        area_max = area_total * area_max_pct
        if zona_y_fin is None:
            zona_y_fin = alto

        mascara, _ = self._crear_mascara(
            frame, rango_bajo, rango_alto, espacio,
            erode_kernel=erode_kernel, erode_iter=erode_iter,
            dilate_kernel=dilate_kernel, dilate_iter=dilate_iter,
        )

        # connectedComponentsWithStats devuelve directamente
        # x, y, w, h y área de cada blob sin calcular polígonos
        num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(
            mascara, connectivity=8
        )

        elementos   = []
        descartados = []

        # label 0 es el fondo, se empieza desde 1
        for i in range(1, num_labels):
            x    = int(stats[i, cv2.CC_STAT_LEFT])
            y    = int(stats[i, cv2.CC_STAT_TOP])
            w    = int(stats[i, cv2.CC_STAT_WIDTH])
            h    = int(stats[i, cv2.CC_STAT_HEIGHT])
            area = float(stats[i, cv2.CC_STAT_AREA])
            centro_x = int(centroids[i, 0])
            centro_y = int(centroids[i, 1])
            proporcion = w / h if h > 0 else 0

            if area < area_min:
                descartados.append((x, y, w, h, f"{tipo} area pequeña"))
                continue
            if area > area_max:
                descartados.append((x, y, w, h, f"{tipo} area grande"))
                continue
            if proporcion < prop_min or proporcion > prop_max:
                descartados.append((x, y, w, h, f"{tipo} proporción rara"))
                continue
            if centro_y < zona_y_inicio or centro_y > zona_y_fin:
                descartados.append((x, y, w, h, f"{tipo} fuera de zona Y"))
                continue

            elementos.append(Elemento(
                x=x, y=y, w=w, h=h,
                centro_x=centro_x, centro_y=centro_y,
                area=area,
                proporcion=round(proporcion, 2),
                tipo=tipo
            ))

        return elementos, descartados, mascara