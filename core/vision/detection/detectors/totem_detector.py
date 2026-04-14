import cv2
import numpy as np
from ..base_detector import BaseDetector, Elemento


class TotemDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * cfg.TOTEM_AREA_MIN_PCT
        area_max = area_total * cfg.TOTEM_AREA_MAX_PCT

        mascara, _ = self._crear_mascara(
            frame,
            cfg.TOTEM_RANGO_BAJO,
            cfg.TOTEM_RANGO_ALTO,
            cfg.TOTEM_ESPACIO,
        )

        kx, ky = getattr(cfg, "TOTEM_DILATE_KERNEL", (7, 7))
        iteraciones = int(getattr(cfg, "TOTEM_DILATE_ITER", 2))
        kernel = np.ones((int(kx), int(ky)), np.uint8)
        mascara = cv2.dilate(mascara, kernel, iterations=max(1, iteraciones))

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
                descartados.append((x, y, w, h, "totem area pequeña"))
                continue
            if area > area_max:
                descartados.append((x, y, w, h, "totem area grande"))
                continue
            if proporcion < cfg.TOTEM_PROP_MIN or proporcion > cfg.TOTEM_PROP_MAX:
                descartados.append((x, y, w, h, "totem proporción rara"))
                continue

            elementos.append(Elemento(
                x=x,
                y=y,
                w=w,
                h=h,
                centro_x=centro_x,
                centro_y=centro_y,
                area=area,
                proporcion=round(proporcion, 2),
                tipo="totem",
            ))

        return elementos, descartados, mascara
