from ..base_detector import BaseDetector, Elemento


class PlataformaMaderaDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        zona_y_inicio_global = int(getattr(cfg, "PLATAFORMA_MADERA_ZONA_Y_INICIO", 230))
        elementos, descartados, mascara = self._detectar_elemento(
            frame,
            cfg.PLATAFORMA_MADERA_RANGO_BAJO,
            cfg.PLATAFORMA_MADERA_RANGO_ALTO,
            cfg.PLATAFORMA_MADERA_AREA_MIN_PCT,
            cfg.PLATAFORMA_MADERA_AREA_MAX_PCT,
            cfg.PLATAFORMA_MADERA_PROP_MIN,
            cfg.PLATAFORMA_MADERA_PROP_MAX,
            "plataforma_madera",
            zona_y_inicio=zona_y_inicio_global,
            zona_y_fin=getattr(cfg, "PLATAFORMA_MADERA_ZONA_Y_FIN", None),
            espacio=getattr(cfg, "PLATAFORMA_MADERA_ESPACIO", "HSV"),
            erode_kernel=getattr(cfg, "PLATAFORMA_MADERA_ERODE_KERNEL", (3, 3)),
            erode_iter=getattr(cfg, "PLATAFORMA_MADERA_ERODE_ITER", 0),
            dilate_kernel=getattr(cfg, "PLATAFORMA_MADERA_DILATE_KERNEL", (3, 3)),
            dilate_iter=getattr(cfg, "PLATAFORMA_MADERA_DILATE_ITER", 1),
        )

        altura_standar = cfg.PLATAFORMA_MADERA_ALTURA_STANDAR
        elementos_ajustados = []
        for e in elementos:
            h_limitado = min(e.h, altura_standar)
            y_ajustado = e.y + (e.h - h_limitado) // 2
            elementos_ajustados.append(Elemento(
                x=e.x,
                y=y_ajustado,
                w=e.w,
                h=h_limitado,
                centro_x=e.centro_x,
                centro_y=e.centro_y,
                area=float(e.w * h_limitado),
                proporcion=e.proporcion,
                tipo="plataforma_madera",
            ))

        return elementos_ajustados, descartados, mascara