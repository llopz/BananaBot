from ..base_detector import BaseDetector


class TotemDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.TOTEM_RANGO_BAJO,
            cfg.TOTEM_RANGO_ALTO,
            cfg.TOTEM_AREA_MIN_PCT,
            cfg.TOTEM_AREA_MAX_PCT,
            cfg.TOTEM_PROP_MIN,
            cfg.TOTEM_PROP_MAX,
            "totem",
            espacio=cfg.TOTEM_ESPACIO,
            dilate_kernel=cfg.TOTEM_DILATE_KERNEL,
            dilate_iter=cfg.TOTEM_DILATE_ITER,
        )