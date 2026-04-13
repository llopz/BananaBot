from ..base_detector import BaseDetector


class ParedDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.PARED_RANGO_BAJO, cfg.PARED_RANGO_ALTO,
            cfg.PARED_AREA_MIN_PCT, cfg.PARED_AREA_MAX_PCT,
            cfg.PARED_PROP_MIN, cfg.PARED_PROP_MAX,
            "pared",
            espacio=cfg.PARED_ESPACIO,
        )