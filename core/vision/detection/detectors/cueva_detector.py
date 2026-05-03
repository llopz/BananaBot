from ..base_detector import BaseDetector


class CuevaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_por_template(
            frame,
            template_nombre=getattr(cfg, "CUEVA_TEMPLATE_ARCHIVO", "Cueva.png"),
            tipo="cueva",
            threshold=float(getattr(cfg, "CUEVA_TEMPLATE_UMBRAL", 0.65)),
            escala_template=float(getattr(cfg, "CUEVA_TEMPLATE_ESCALA", 1.10)),
        )