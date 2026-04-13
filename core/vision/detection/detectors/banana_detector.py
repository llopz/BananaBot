from ..base_detector import BaseDetector, Elemento
import numpy as np


class BananaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.BANANA_RANGO_BAJO, cfg.BANANA_RANGO_ALTO,
            cfg.BANANA_AREA_MIN_PCT, cfg.BANANA_AREA_MAX_PCT,
            cfg.BANANA_PROP_MIN, cfg.BANANA_PROP_MAX,
            "banana",
            zona_y_inicio=cfg.BANANA_ZONA_Y_INICIO,
            zona_y_fin=cfg.BANANA_ZONA_Y_FIN,
            espacio=cfg.BANANA_ESPACIO,
        )