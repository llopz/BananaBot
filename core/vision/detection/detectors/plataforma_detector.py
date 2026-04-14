from ..base_detector import BaseDetector, Elemento
import cv2
import numpy as np


class PlataformaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]

        elementos = []
        descartados = []
        mascara_final = None

        for y_centro in cfg.PLATAFORMA_ZONAS_Y:
            y_inicio = max(0, y_centro - 25)
            y_fin    = min(alto, y_centro + 25)

            franja = frame[y_inicio:y_fin, :]
            if franja.size == 0:
                continue

            mascara, _ = self._crear_mascara(
                franja,
                cfg.PLATAFORMA_RANGO_BAJO,
                cfg.PLATAFORMA_RANGO_ALTO,
                cfg.PLATAFORMA_ESPACIO
            )

            # Dilatar más para unir fragmentos
            kernel_shape = getattr(cfg, "PLATAFORMA_DILATE_KERNEL", (3, 15))
            kernel_h = np.ones(tuple(int(v) for v in kernel_shape), np.uint8)
            mascara = cv2.dilate(mascara, kernel_h, iterations=int(getattr(cfg, "PLATAFORMA_DILATE_ITER", 3)))

            # Mantener la última máscara para debug
            mascara_final = mascara.copy()

            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contorno in contornos:
                area = cv2.contourArea(contorno)
                x, y, w, h = cv2.boundingRect(contorno)
                centro_x = x + w // 2
                centro_y_real = y_inicio + y + h // 2
                proporcion = w / h if h > 0 else 0

                area_total = alto * ancho
                area_min = area_total * cfg.PLATAFORMA_AREA_MIN_PCT
                area_max = area_total * cfg.PLATAFORMA_AREA_MAX_PCT

                if area < area_min or area > area_max:
                    continue
                if proporcion < cfg.PLATAFORMA_PROP_MIN or proporcion > cfg.PLATAFORMA_PROP_MAX:
                    continue
                # Permitir plataformas en cualquier posición horizontal

                # Limitar altura al estándar si detecta algo muy alto
                h_limitado = min(h, cfg.PLATAFORMA_ALTURA_STANDAR)
                y_ajustado = y_inicio + y + (h - h_limitado) // 2  # centrar si se reduce

                elementos.append(Elemento(
                    x=x,
                    y=y_ajustado,
                    w=w,
                    h=h_limitado,
                    centro_x=centro_x,
                    centro_y=centro_y_real,
                    area=area,
                    proporcion=round(proporcion, 2),
                    tipo="plataforma"
                ))

        return elementos, descartados, mascara_final