import cv2
import numpy as np
from typing import List
from ..detection.base_detector import Elemento

COLOR_BANANA     = (0, 255, 0)
COLOR_TRONCO     = (0, 140, 255)
COLOR_ARBUSTO    = (0, 200, 100)
COLOR_AVION      = (255, 200, 0)
COLOR_KONG       = (0, 255, 255)
COLOR_PARED      = (180, 180, 180)
COLOR_ROCA       = (80, 80, 80)
COLOR_CUEVA      = (255, 0, 255)
COLOR_TOTEM      = (0, 165, 255)
COLOR_PLATAFORMA = (255, 0, 0)  
COLOR_PLATAFORMA_MADERA = (139, 69, 19)  
COLOR_AGUA       = (200, 200, 0)
COLOR_OBSTACULO  = (0, 0, 255)
COLOR_ZONA       = (255, 255, 0)
COLOR_PERSONAJE  = (255, 0, 255)
COLOR_CENTRO     = (0, 0, 255)
COLOR_TEXTO_ON   = (0, 255, 0)
COLOR_TEXTO_OFF  = (0, 0, 255)
COLOR_REFERENCIA = (100, 100, 255)


class Visualizador:

    def __init__(self, config):
        self.config = config

    def dibujar_descartados(self, frame: np.ndarray, descartados: list) -> np.ndarray:
        for (x, y, w, h, razon) in descartados:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.putText(frame, razon, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        return frame

    def dibujar_elementos(self, frame: np.ndarray, elementos: List[Elemento]) -> np.ndarray:
        for el in elementos:
            if el.tipo == "agua":
                continue
            if el.tipo == "banana":
                color = COLOR_BANANA
            elif el.tipo == "tronco":
                color = COLOR_TRONCO
            elif el.tipo == "arbusto":
                color = COLOR_ARBUSTO
            elif el.tipo == "avion":
                color = COLOR_AVION
            elif el.tipo == "kong":
                color = COLOR_KONG
            elif el.tipo == "pared":
                color = COLOR_PARED
            elif el.tipo == "roca":
                color = COLOR_ROCA
            elif el.tipo == "cueva":
                color = COLOR_CUEVA
            elif el.tipo == "totem":
                color = COLOR_TOTEM
            elif el.tipo == "plataforma":
                color = COLOR_PLATAFORMA
            elif el.tipo == "plataforma_madera":
                color = COLOR_PLATAFORMA_MADERA
            else:
                color = COLOR_OBSTACULO

            cv2.rectangle(frame, (el.x, el.y), (el.x + el.w, el.y + el.h), color, 2)
            cv2.circle(frame, (el.centro_x, el.centro_y), 4, COLOR_CENTRO, -1)

            if self.config.DEBUG:
                cv2.putText(frame, f"a={int(el.area)} p={el.proporcion}",
                            (el.x, el.y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        return frame

    def dibujar_zonas(self, frame: np.ndarray) -> np.ndarray:
        cfg = self.config
        alto, ancho = frame.shape[:2]

        if cfg.MOSTRAR_PERSONAJE:
            x_personaje = int(ancho * cfg.PERSONAJE_X_RATIO)
            cv2.line(frame, (x_personaje, 0), (x_personaje, alto), COLOR_PERSONAJE, 1)

        if cfg.MOSTRAR_ZONA:
            cv2.line(frame, (0, cfg.BANANA_ZONA_Y_INICIO), (ancho, cfg.BANANA_ZONA_Y_INICIO), COLOR_ZONA, 1)
            cv2.line(frame, (0, cfg.BANANA_ZONA_Y_FIN),    (ancho, cfg.BANANA_ZONA_Y_FIN),    COLOR_ZONA, 1)

        cv2.line(frame, (0, alto // 2), (ancho, alto // 2), COLOR_REFERENCIA, 1)

        return frame

    def dibujar_estado(self, frame: np.ndarray, bot_activo: bool, pausado: bool, conteos: dict) -> np.ndarray:
        if pausado:
            texto_estado = "PAUSADO"
            color = (0, 165, 255)
        elif bot_activo:
            texto_estado = "BOT: ON"
            color = COLOR_TEXTO_ON
        else:
            texto_estado = "BOT: OFF"
            color = COLOR_TEXTO_OFF

        cv2.putText(frame, texto_estado, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        y = 55
        for tipo, cantidad in conteos.items():
            cv2.putText(frame, f"{tipo}: {cantidad}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20

        return frame

    def dibujar_todo(self, frame: np.ndarray, elementos_por_tipo: dict,
                     bot_activo: bool, pausado: bool,
                     descartados: list = None) -> np.ndarray:
        frame = frame.copy()

        frame = self.dibujar_zonas(frame)

        # if descartados:
        #     frame = self.dibujar_descartados(frame, descartados)

        todos_los_elementos = []
        conteos = {}
        for tipo, lista in elementos_por_tipo.items():
            if tipo in ("mascaras", "descartados"):
                continue
            todos_los_elementos.extend(lista)
            conteos[tipo] = len(lista)

        frame = self.dibujar_elementos(frame, todos_los_elementos)
        #frame = self.dibujar_estado(frame, bot_activo, pausado, conteos)

        return frame

    def mostrar_mascara(self, nombre: str, mascara: np.ndarray, escala: float = 0.3):
        if mascara is None:
            return
        pequeña = cv2.resize(mascara, (0, 0), fx=0.7, fy=0.7)
        cv2.imshow(f"mascara_{nombre}", pequeña)