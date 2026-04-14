from ..base_detector import BaseDetector, Elemento
import cv2
import numpy as np


class PlataformaMaderaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * cfg.PLATAFORMA_MADERA_AREA_MIN_PCT
        area_max = area_total * cfg.PLATAFORMA_MADERA_AREA_MAX_PCT

        elementos = []
        descartados = []
        mascara_final = np.zeros((alto, ancho), dtype=np.uint8)
        kernel_shape = tuple(int(v) for v in cfg.PLATAFORMA_MADERA_DILATE_KERNEL)
        kernel = np.ones(kernel_shape, np.uint8)
        iteraciones = int(cfg.PLATAFORMA_MADERA_DILATE_ITER)

        for y_centro in sorted(cfg.PLATAFORMA_MADERA_ZONAS_Y):
            y_inicio = max(0, y_centro - 20)
            y_fin = min(alto, y_centro + 20)

            franja = frame[y_inicio:y_fin, :]
            if franja.size == 0:
                continue

            mascara, _ = self._crear_mascara(
                franja,
                cfg.PLATAFORMA_MADERA_RANGO_BAJO,
                cfg.PLATAFORMA_MADERA_RANGO_ALTO,
                cfg.PLATAFORMA_MADERA_ESPACIO,
            )
            mascara = cv2.dilate(mascara, kernel, iterations=iteraciones)
            alto_franja = y_fin - y_inicio
            mascara_recortada = mascara[:alto_franja, :]
            mascara_final[y_inicio:y_fin, :] = np.maximum(mascara_final[y_inicio:y_fin, :], mascara_recortada)

            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contorno in contornos:
                area = cv2.contourArea(contorno)
                x, y, w, h = cv2.boundingRect(contorno)
                proporcion = w / h if h > 0 else 0

                y_real = y_inicio + y
                centro_x = x + w // 2
                centro_y_real = y_real + h // 2

                if area < area_min or area > area_max:
                    descartados.append((x, y_real, w, h, "plataforma_madera area"))
                    continue
                if proporcion < cfg.PLATAFORMA_MADERA_PROP_MIN or proporcion > cfg.PLATAFORMA_MADERA_PROP_MAX:
                    descartados.append((x, y_real, w, h, f"plataforma_madera prop {proporcion:.2f}"))
                    continue

                h_limitado = min(h, cfg.PLATAFORMA_MADERA_ALTURA_STANDAR)
                y_ajustado = y_real + (h - h_limitado) // 2

                elementos.append(Elemento(
                    x=x,
                    y=y_ajustado,
                    w=w,
                    h=h_limitado,
                    centro_x=centro_x,
                    centro_y=centro_y_real,
                    area=area,
                    proporcion=round(proporcion, 2),
                    tipo="plataforma_madera"
                ))

        return elementos, descartados, mascara_final