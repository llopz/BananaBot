from ..base_detector import BaseDetector


class BarrilDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_por_template(
            frame,
            template_nombre=getattr(cfg, "BARRIL_TEMPLATE_ARCHIVO", "Barril.png"),
            tipo="barril",
            threshold=float(getattr(cfg, "BARRIL_TEMPLATE_UMBRAL", 0.65)),
            escala_template=float(getattr(cfg, "BARRIL_TEMPLATE_ESCALA", 1.10)),
        )
