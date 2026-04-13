from ..base_detector import BaseDetector


class RocaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.ROCA_RANGO_BAJO, cfg.ROCA_RANGO_ALTO,
            cfg.ROCA_AREA_MIN_PCT, cfg.ROCA_AREA_MAX_PCT,
            cfg.ROCA_PROP_MIN, cfg.ROCA_PROP_MAX,
            "roca",
            espacio=cfg.ROCA_ESPACIO,
        )