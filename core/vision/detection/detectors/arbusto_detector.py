from ..base_detector import BaseDetector


class ArbustoDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.ARBUSTO_RANGO_BAJO, cfg.ARBUSTO_RANGO_ALTO,
            cfg.ARBUSTO_AREA_MIN_PCT, cfg.ARBUSTO_AREA_MAX_PCT,
            cfg.ARBUSTO_PROP_MIN, cfg.ARBUSTO_PROP_MAX,
            "arbusto",
            espacio=cfg.ARBUSTO_ESPACIO,
        )