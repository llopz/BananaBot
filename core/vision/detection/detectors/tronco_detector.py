from ..base_detector import BaseDetector


class TroncoDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.TRONCO_RANGO_BAJO, cfg.TRONCO_RANGO_ALTO,
            cfg.TRONCO_AREA_MIN_PCT, cfg.TRONCO_AREA_MAX_PCT,
            cfg.TRONCO_PROP_MIN, cfg.TRONCO_PROP_MAX,
            "tronco",
            espacio=cfg.TRONCO_ESPACIO,
        )