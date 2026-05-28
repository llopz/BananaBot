from ..base_detector import BaseDetector


class GameOverDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        template_nombre = getattr(cfg, "GAME_OVER_TEMPLATE_ARCHIVO", "GameOver.png")
        threshold = float(getattr(cfg, "GAME_OVER_TEMPLATE_UMBRAL", 0.75))
        escala_template = float(getattr(cfg, "GAME_OVER_TEMPLATE_ESCALA", 1.0))
        roi_factor_x = float(getattr(cfg, "GAME_OVER_ROI_FACTOR_X", 2.0))
        roi_factor_y = float(getattr(cfg, "GAME_OVER_ROI_FACTOR_Y", 2.0))

        template = self._cargar_template(template_nombre, escala=escala_template, gris=True)
        template_h, template_w = template.shape[:2]
        alto, ancho = frame.shape[:2]

        roi_w = min(ancho, max(template_w, int(round(template_w * roi_factor_x))))
        roi_h = min(alto, max(template_h, int(round(template_h * roi_factor_y))))

        centro_x = ancho // 2
        centro_y = alto // 2
        x_inicio = max(0, min(max(0, ancho - roi_w), centro_x - roi_w // 2))
        y_inicio = max(0, min(max(0, alto - roi_h), centro_y - roi_h // 2))

        return self._detectar_por_template(
            frame,
            template_nombre=template_nombre,
            tipo="game_over",
            threshold=threshold,
            escala_template=escala_template,
            zona_x_inicio=x_inicio,
            zona_x_fin=x_inicio + roi_w,
            zona_y_inicio=y_inicio,
            zona_y_fin=y_inicio + roi_h,
        )