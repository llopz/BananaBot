from ..base_detector import BaseDetector


class KongDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.KONG_RANGO_BAJO, cfg.KONG_RANGO_ALTO,
            cfg.KONG_AREA_MIN_PCT, cfg.KONG_AREA_MAX_PCT,
            cfg.KONG_PROP_MIN, cfg.KONG_PROP_MAX,
            "kong",
            espacio=cfg.KONG_ESPACIO,
        )