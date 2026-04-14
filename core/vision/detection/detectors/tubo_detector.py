from ..base_detector import BaseDetector


class TuboDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        extension_izquierda = max(0, int(cfg.TUBO_EXTENSION_IZQUIERDA))

        elementos, descartados, mascara = self._detectar_elemento(
            frame,
            cfg.TUBO_RANGO_BAJO, cfg.TUBO_RANGO_ALTO,
            cfg.TUBO_AREA_MIN_PCT, cfg.TUBO_AREA_MAX_PCT,
            cfg.TUBO_PROP_MIN, cfg.TUBO_PROP_MAX,
            "tubo",
            espacio=cfg.TUBO_ESPACIO,
        )

        if extension_izquierda > 0 and elementos:
            ancho_frame = frame.shape[1]
            for elemento in elementos:
                nuevo_x = max(0, elemento.x - extension_izquierda)
                delta_izquierda = elemento.x - nuevo_x
                elemento.x = nuevo_x
                elemento.w = min(ancho_frame - nuevo_x, elemento.w + delta_izquierda)
                elemento.centro_x = elemento.x + elemento.w // 2
                elemento.proporcion = round(elemento.w / elemento.h, 2) if elemento.h > 0 else 0

        return elementos, descartados, mascara
