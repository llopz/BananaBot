import cv2
import numpy as np
from dataclasses import dataclass


@dataclass
class Elemento:
    x: int
    y: int
    w: int
    h: int
    centro_x: int
    centro_y: int
    area: float
    proporcion: float
    tipo: str = "desconocido"


class Detector:

    def __init__(self, config):
        self.config = config

    def _crear_mascara(self, frame, hsv_bajo, hsv_alto):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = cv2.inRange(hsv, np.array(hsv_bajo), np.array(hsv_alto))
        kernel = np.ones((3, 3), np.uint8)
        mascara = cv2.erode(mascara, kernel, iterations=1)
        mascara = cv2.dilate(mascara, kernel, iterations=1)
        return mascara, hsv

    def _detectar_elemento(
        self,
        frame,
        hsv_bajo,
        hsv_alto,
        area_min_pct,
        area_max_pct,
        prop_min,
        prop_max,
        tipo,
        zona_y_inicio=0,
        zona_y_fin=None,
    ):
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * area_min_pct
        area_max = area_total * area_max_pct
        if zona_y_fin is None:
            zona_y_fin = alto

        mascara, _ = self._crear_mascara(frame, hsv_bajo, hsv_alto)
        contornos, _ = cv2.findContours(
            mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        elementos = []
        descartados = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            centro_x = x + w // 2
            centro_y = y + h // 2
            proporcion = w / h if h > 0 else 0

            if area < area_min:
                descartados.append((x, y, w, h, f"{tipo} area {int(area)} pequeña"))
                continue
            if area > area_max:
                descartados.append((x, y, w, h, f"{tipo} area {int(area)} grande"))
                continue
            if proporcion < prop_min or proporcion > prop_max:
                descartados.append((x, y, w, h, f"{tipo} prop {proporcion:.2f} rara"))
                continue
            if centro_y < zona_y_inicio:
                descartados.append((x, y, w, h, f"{tipo} y={centro_y} arriba"))
                continue
            if centro_y > zona_y_fin:
                descartados.append((x, y, w, h, f"{tipo} y={centro_y} abajo"))
                continue

            elementos.append(
                Elemento(
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    centro_x=centro_x,
                    centro_y=centro_y,
                    area=area,
                    proporcion=round(proporcion, 2),
                    tipo=tipo,
                )
            )

        return elementos, descartados, mascara

    def detectar_bananas(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.BANANA_HSV_BAJO,
            cfg.BANANA_HSV_ALTO,
            cfg.BANANA_AREA_MIN_PCT,
            cfg.BANANA_AREA_MAX_PCT,
            cfg.BANANA_PROP_MIN,
            cfg.BANANA_PROP_MAX,
            "banana",
            zona_y_inicio=cfg.BANANA_ZONA_Y_INICIO,
            zona_y_fin=cfg.BANANA_ZONA_Y_FIN,
        )

    def detectar_tronco(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.TRONCO_HSV_BAJO,
            cfg.TRONCO_HSV_ALTO,
            cfg.TRONCO_AREA_MIN_PCT,
            cfg.TRONCO_AREA_MAX_PCT,
            cfg.TRONCO_PROP_MIN,
            cfg.TRONCO_PROP_MAX,
            "tronco",
        )

    def detectar_arbusto(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.ARBUSTO_HSV_BAJO,
            cfg.ARBUSTO_HSV_ALTO,
            cfg.ARBUSTO_AREA_MIN_PCT,
            cfg.ARBUSTO_AREA_MAX_PCT,
            cfg.ARBUSTO_PROP_MIN,
            cfg.ARBUSTO_PROP_MAX,
            "arbusto",
        )

    def detectar_avion(self, frame):
        cfg = self.config
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * cfg.AVION_AREA_MIN_PCT
        area_max = area_total * cfg.AVION_AREA_MAX_PCT

        mascara, _ = self._crear_mascara(frame, cfg.AVION_HSV_BAJO, cfg.AVION_HSV_ALTO)
        contornos, _ = cv2.findContours(
            mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        elementos = []
        descartados = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)
            x, y, w, h = cv2.boundingRect(contorno)
            proporcion = w / h if h > 0 else 0

            if area < area_min:
                descartados.append((x, y, w, h, f"avion area {int(area)} pequeña"))
                continue
            if area > area_max:
                descartados.append((x, y, w, h, f"avion area {int(area)} grande"))
                continue
            if proporcion < cfg.AVION_PROP_MIN or proporcion > cfg.AVION_PROP_MAX:
                descartados.append((x, y, w, h, f"avion prop {proporcion:.2f} rara"))
                continue
            # Si está debajo de la zona de juego no es el avión
            centro_y = y + h // 2
            if centro_y > cfg.BANANA_ZONA_Y_FIN:
                descartados.append((x, y, w, h, f"avion y={centro_y} fuera de zona"))
                continue

            # Expandir horizontalmente desde la franja azul
            expansion_x = int(w * 0.5)
            expansion_y = int(h * 0.6)
            x_exp = max(0, x - expansion_x)
            w_exp = min(ancho - x_exp, w + expansion_x * 2)

            y_exp = max(0, y - expansion_y)
            h_exp = min(alto - y_exp, h + expansion_y * 2)

            elementos.append(
                Elemento(
                    x=x_exp,
                    y=y_exp,
                    w=w_exp,
                    h=h_exp,
                    centro_x=x_exp + w_exp // 2,
                    centro_y=y_exp + h_exp // 2,
                    area=area,
                    proporcion=round(w_exp / h_exp, 2),
                    tipo="avion",
                )
            )

        return elementos, descartados, mascara

    def detectar_kong(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.KONG_HSV_BAJO,
            cfg.KONG_HSV_ALTO,
            cfg.KONG_AREA_MIN_PCT,
            cfg.KONG_AREA_MAX_PCT,
            cfg.KONG_PROP_MIN,
            cfg.KONG_PROP_MAX,
            "kong",
        )

    def detectar_todos(self, frame) -> dict:
        bananas, desc_b, mascara_b = self.detectar_bananas(frame)
        troncos, desc_t, mascara_t = self.detectar_tronco(frame)
        arbustos, desc_a, mascara_a = self.detectar_arbusto(frame)
        aviones, desc_v, mascara_v = self.detectar_avion(frame)
        kongs, desc_k, mascara_k = self.detectar_kong(frame)

        return {
            "bananas": bananas,
            "troncos": troncos,
            "arbustos": arbustos,
            "aviones": aviones,
            "kong": kongs,
            "descartados": desc_b + desc_t + desc_a + desc_v + desc_k,
            "mascaras": {
                "bananas": mascara_b,
                "troncos": mascara_t,
                "arbustos": mascara_a,
                "aviones": mascara_v,
                "kong": mascara_k,
            },
        }
