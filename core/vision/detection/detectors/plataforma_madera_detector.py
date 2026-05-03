from ..base_detector import BaseDetector, Elemento
import numpy as np


class PlataformaMaderaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]

        template_nombre = getattr(cfg, "PLATAFORMA_MADERA_TEMPLATE_ARCHIVO", "Plataforma madera.png")
        threshold = float(getattr(cfg, "PLATAFORMA_MADERA_TEMPLATE_UMBRAL", 0.18))
        escala_template = float(getattr(cfg, "PLATAFORMA_MADERA_TEMPLATE_ESCALA", 1.10))
        posiciones_y = getattr(cfg, "PLATAFORMA_MADERA_POSICIONES_Y", [255, 357, 459, 560])
        roi_padding_y = int(getattr(cfg, "PLATAFORMA_MADERA_ROI_PADDING_Y", 50))
        prop_min = cfg.PLATAFORMA_MADERA_PROP_MIN
        prop_max = cfg.PLATAFORMA_MADERA_PROP_MAX
        altura_standar = cfg.PLATAFORMA_MADERA_ALTURA_STANDAR

        elementos = []
        descartados = []
        mascara_final = np.zeros((alto, ancho), dtype=np.uint8)

        for pos_y in posiciones_y:
            y_inicio = max(0, pos_y - roi_padding_y)
            y_fin = min(alto, pos_y + roi_padding_y)

            elementos_franja, descartados_franja, mascara_franja = self._detectar_por_template(
                frame,
                template_nombre=template_nombre,
                tipo="plataforma_madera",
                threshold=threshold,
                escala_template=escala_template,
                zona_y_inicio=y_inicio,
                zona_y_fin=y_fin,
            )
            descartados.extend(descartados_franja)
            mascara_final = np.maximum(mascara_final, mascara_franja)

            if elementos_franja:
                e = elementos_franja[0]
                proporcion = e.w / e.h if e.h > 0 else 0.0

                if proporcion < prop_min or proporcion > prop_max:
                    descartados.append((e.x, e.y, e.w, e.h, f"plataforma_madera prop {proporcion:.2f}"))
                    continue

                h_limitado = min(e.h, altura_standar)
                y_ajustado = e.y + (e.h - h_limitado) // 2

                elementos.append(Elemento(
                    x=e.x,
                    y=y_ajustado,
                    w=e.w,
                    h=h_limitado,
                    centro_x=e.centro_x,
                    centro_y=e.centro_y,
                    area=float(e.w * e.h),
                    proporcion=round(proporcion, 2),
                    tipo="plataforma_madera",
                ))

        return elementos, descartados, mascara_final