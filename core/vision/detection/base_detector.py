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

    def _crear_mascara(self, frame, rango_bajo, rango_alto, espacio="HSV"):
        codigo = ESPACIOS_COLOR.get(espacio, cv2.COLOR_BGR2HSV)
        convertida = cv2.cvtColor(frame, codigo)
        mascara = cv2.inRange(convertida, np.array(rango_bajo), np.array(rango_alto))
        kernel = np.ones((3, 3), np.uint8)
        mascara = cv2.erode(mascara, kernel, iterations=1)
        mascara = cv2.dilate(mascara, kernel, iterations=1)
        return mascara, convertida

    def _detectar_elemento(self, frame, rango_bajo, rango_alto,
                           area_min_pct, area_max_pct,
                           prop_min, prop_max, tipo,
                           zona_y_inicio=0, zona_y_fin=None,
                           espacio="HSV") -> Tuple[List[Elemento], List[Tuple], np.ndarray]:
        
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * area_min_pct
        area_max = area_total * area_max_pct
        if zona_y_fin is None:
            zona_y_fin = alto

        mascara, _ = self._crear_mascara(frame, rango_bajo, rango_alto, espacio)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elementos = []
        descartados = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            centro_x = x + w // 2
            centro_y = y + h // 2
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