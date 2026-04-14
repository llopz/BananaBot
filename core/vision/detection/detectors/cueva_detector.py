from ..base_detector import BaseDetector


class CuevaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        zona_y_inicio = getattr(cfg, "CUEVA_ZONA_Y_INICIO", 458)
        extension_izquierda = max(0, int(getattr(cfg, "CUEVA_EXTENSION_IZQUIERDA", 73)))

        elementos, descartados, mascara = self._detectar_elemento(
            frame,
            cfg.CUEVA_RANGO_BAJO, cfg.CUEVA_RANGO_ALTO,
            cfg.CUEVA_AREA_MIN_PCT, cfg.CUEVA_AREA_MAX_PCT,
            cfg.CUEVA_PROP_MIN, cfg.CUEVA_PROP_MAX,
            "cueva",
            zona_y_inicio=zona_y_inicio,
            espacio=cfg.CUEVA_ESPACIO,
        )

        if extension_izquierda > 0 and elementos:
            ancho_frame = frame.shape[1]
            for elemento in elementos:
                nuevo_x = max(0, elemento.x - extension_izquierda)
                delta_izq = elemento.x - nuevo_x
                elemento.x = nuevo_x
                elemento.w = min(ancho_frame - nuevo_x, elemento.w + delta_izq)
                elemento.centro_x = elemento.x + elemento.w // 2
                elemento.proporcion = round(elemento.w / elemento.h, 2) if elemento.h > 0 else 0

        return elementos, descartados, mascara