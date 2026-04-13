from ..base_detector import BaseDetector, Elemento
import cv2
import numpy as np


class AvionDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * cfg.AVION_AREA_MIN_PCT
        area_max = area_total * cfg.AVION_AREA_MAX_PCT

        mascara, _ = self._crear_mascara(
            frame, cfg.AVION_RANGO_BAJO, cfg.AVION_RANGO_ALTO, cfg.AVION_ESPACIO
        )
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        elementos = []
        descartados = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            proporcion = w / h if h > 0 else 0

            if area < area_min or area > area_max:
                descartados.append((x, y, w, h, "avion area fuera de rango"))
                continue
            if proporcion < cfg.AVION_PROP_MIN or proporcion > cfg.AVION_PROP_MAX:
                descartados.append((x, y, w, h, "avion proporción rara"))
                continue

            centro_y = y + h // 2
            if centro_y > cfg.BANANA_ZONA_Y_FIN:
                descartados.append((x, y, w, h, "avion fuera de zona"))
                continue

            expansion_x = int(w * 0.5)
            expansion_y = int(h * 0.6)
            x_exp = max(0, x - expansion_x)
            w_exp = min(ancho - x_exp, w + expansion_x * 2)
            y_exp = max(0, y - expansion_y)
            h_exp = min(alto - y_exp, h + expansion_y * 2)

            elementos.append(Elemento(
                x=x_exp, y=y_exp, w=w_exp, h=h_exp,
                centro_x=x_exp + w_exp // 2,
                centro_y=y_exp + h_exp // 2,
                area=area,
                proporcion=round(w_exp / h_exp, 2),
                tipo="avion",
            ))

        return elementos, descartados, mascara