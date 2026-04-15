from ..base_detector import BaseDetector, Elemento
import cv2
import numpy as np


class AguaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]
        mascara_final = np.zeros((alto, ancho), dtype=np.uint8)

        zona_inicio = cfg.AGUA_ZONA_Y_INICIO
        franja = frame[zona_inicio:alto, :]
        if franja.size == 0:
            return [], [], mascara_final

        mascara_base, _ = self._crear_mascara(
            franja,
            cfg.AGUA_RANGO_BAJO,
            cfg.AGUA_RANGO_ALTO,
            cfg.AGUA_ESPACIO,
            erode_iter=0,
            dilate_iter=0,
        )

        mascara = mascara_base.copy()

        iter_h = int(cfg.AGUA_DILATE_ITER_H)
        if iter_h > 0:
            kernel_h = np.ones(tuple(int(v) for v in cfg.AGUA_DILATE_KERNEL_H), np.uint8)
            mascara = cv2.dilate(mascara, kernel_h, iterations=iter_h)

        iter_v = int(cfg.AGUA_DILATE_ITER_V)
        if iter_v > 0:
            kernel_v = np.ones(tuple(int(v) for v in cfg.AGUA_DILATE_KERNEL_V), np.uint8)
            mascara = cv2.dilate(mascara, kernel_v, iterations=iter_v)

        mascara_final[zona_inicio:alto, :] = mascara_base[:alto - zona_inicio, :]

        pixeles_agua = cv2.countNonZero(mascara)
        
        elementos = []
        if pixeles_agua > cfg.AGUA_PIXELES_MIN:
            # Encontrar contornos de cada región de agua separada
            contornos, _ = cv2.findContours(mascara_base, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contorno in contornos:
                area_contorno = cv2.contourArea(contorno)
                if area_contorno < cfg.AGUA_PIXELES_MIN:
                    continue

                x, y, w, h = cv2.boundingRect(contorno)
                x_inicio = x
                x_fin = x + w
                y_inicio = zona_inicio + y
                altura_agua = h

                ancho_agua = max(1, x_fin - x_inicio)

                elementos.append(Elemento(
                    x=x_inicio, y=y_inicio,
                    w=ancho_agua, h=altura_agua,
                    centro_x=x_inicio + ancho_agua // 2,
                    centro_y=(y_inicio + y_inicio + altura_agua) // 2,
                    area=float(area_contorno),
                    proporcion=round(ancho_agua / altura_agua, 2) if altura_agua > 0 else 0,
                    tipo="agua"
                ))

        return elementos, [], mascara_final