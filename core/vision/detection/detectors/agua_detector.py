from ..base_detector import BaseDetector, Elemento
import cv2
import numpy as np


class AguaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]

        zona_inicio = getattr(cfg, "AGUA_ZONA_Y_INICIO", cfg.BANANA_ZONA_Y_FIN)
        franja = frame[zona_inicio:alto, :]
        if franja.size == 0:
            return [], [], None

        mascara, _ = self._crear_mascara(
            franja, cfg.AGUA_RANGO_BAJO, cfg.AGUA_RANGO_ALTO, cfg.AGUA_ESPACIO
        )

        kernel_h_shape = getattr(cfg, "AGUA_DILATE_KERNEL_H", (3, 60))
        kernel_h = np.ones(tuple(int(v) for v in kernel_h_shape), np.uint8)
        mascara = cv2.dilate(mascara, kernel_h, iterations=int(getattr(cfg, "AGUA_DILATE_ITER_H", 3)))

        kernel_v_shape = getattr(cfg, "AGUA_DILATE_KERNEL_V", (10, 1))
        kernel_v = np.ones(tuple(int(v) for v in kernel_v_shape), np.uint8)
        mascara = cv2.dilate(mascara, kernel_v, iterations=int(getattr(cfg, "AGUA_DILATE_ITER_V", 2)))

        pixeles_agua = cv2.countNonZero(mascara)

        elementos = []
        if pixeles_agua > cfg.AGUA_PIXELES_MIN:
            filas_con_agua = np.any(mascara > 0, axis=1)
            primer_fila = np.argmax(filas_con_agua)
            y_real = zona_inicio + primer_fila

            elementos.append(Elemento(
                x=0, y=y_real,
                w=ancho, h=alto - y_real,
                centro_x=ancho // 2,
                centro_y=(y_real + alto) // 2,
                area=float(pixeles_agua),
                proporcion=round(ancho / (alto - y_real), 2),
                tipo="agua"
            ))

        return elementos, [], mascara