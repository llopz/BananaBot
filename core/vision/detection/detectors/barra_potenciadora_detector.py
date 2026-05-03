from ..base_detector import BaseDetector


class BarraPotenciadoraDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        template_nombre = getattr(cfg, "BARRA_POTENCIADORA_TEMPLATE_ARCHIVO", "Barra Potenciadora.png")
        threshold = float(getattr(cfg, "BARRA_POTENCIADORA_TEMPLATE_UMBRAL", 0.60))
        escala_template = float(getattr(cfg, "BARRA_POTENCIADORA_TEMPLATE_ESCALA", 1.10))
        pos_x = int(getattr(cfg, "BARRA_POTENCIADORA_POS_X", 138))
        pos_y = int(getattr(cfg, "BARRA_POTENCIADORA_POS_Y", 100))
        tol_x = int(getattr(cfg, "BARRA_POTENCIADORA_TOL_X", 60))
        tol_y = int(getattr(cfg, "BARRA_POTENCIADORA_TOL_Y", 50))
        roi_padding = int(getattr(cfg, "BARRA_POTENCIADORA_ROI_PADDING", 16))

        template = self._cargar_template(template_nombre, escala=escala_template, gris=True)
        template_h, template_w = template.shape[:2]
        alto, ancho = frame.shape[:2]

        x_inicio = max(0, pos_x - tol_x - (template_w // 2) - roi_padding)
        x_fin = min(ancho, pos_x + tol_x + (template_w // 2) + roi_padding)
        y_inicio = max(0, pos_y - tol_y - (template_h // 2) - roi_padding)
        y_fin = min(alto, pos_y + tol_y + (template_h // 2) + roi_padding)

        elementos, descartados, mascara = self._detectar_por_template(
            frame,
            template_nombre=template_nombre,
            tipo="barra_potenciadora",
            threshold=threshold,
            escala_template=escala_template,
            zona_x_inicio=x_inicio,
            zona_x_fin=x_fin,
            zona_y_inicio=y_inicio,
            zona_y_fin=y_fin,
        )

        elementos_filtrados = []
        for e in elementos:
            if abs(e.centro_x - pos_x) <= tol_x and abs(e.centro_y - pos_y) <= tol_y:
                elementos_filtrados.append(e)
            else:
                descartados.append((e.x, e.y, e.w, e.h, "barra_potenciadora fuera de posicion fija"))

        if elementos_filtrados:
            elementos_filtrados.sort(key=lambda e: abs(e.centro_x - pos_x) + abs(e.centro_y - pos_y))
            elementos_filtrados = [elementos_filtrados[0]]

        if len(elementos_filtrados) != len(elementos):
            mascara[:] = 0
            for e in elementos_filtrados:
                mascara[e.y:e.y + e.h, e.x:e.x + e.w] = 255

        return elementos_filtrados, descartados, mascara
