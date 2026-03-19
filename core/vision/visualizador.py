import cv2
import numpy as np
from typing import List
from vision.detector import Elemento

# Colores en formato BGR (OpenCV usa BGR, no RGB)
<<<<<<< HEAD:test/vision/visualizador.py
COLOR_BANANA     = (0, 255, 0)      # verde
COLOR_TRONCO     = (0, 140, 255)    # naranja
COLOR_ARBUSTO    = (0, 200, 100)    # verde oscuro
COLOR_AVION      = (255, 200, 0)    # celeste
COLOR_KONG       = (0, 255, 255)    # amarillo
COLOR_PARED      = (180, 180, 180)  # gris
COLOR_AGUA       = (200, 200, 0)    # amarillo verdoso
COLOR_OBSTACULO  = (0, 0, 255)      # rojo
COLOR_ZONA       = (255, 255, 0)    # amarillo
COLOR_PERSONAJE  = (255, 0, 255)    # magenta
COLOR_CENTRO     = (0, 0, 255)      # rojo (punto central)
COLOR_TEXTO_ON   = (0, 255, 0)      # verde (bot activo)
COLOR_TEXTO_OFF  = (0, 0, 255)      # rojo (bot inactivo)
=======
COLOR_BANANA = (0, 255, 0)  # verde
COLOR_TRONCO = (0, 140, 255)  # naranja
COLOR_ARBUSTO = (0, 200, 100)  # verde oscuro
COLOR_AVION = (255, 200, 0)  # celeste
COLOR_KONG = (0, 255, 255)  # amarillo
COLOR_OBSTACULO = (0, 0, 255)  # rojo
COLOR_ZONA = (255, 255, 0)  # amarillo
COLOR_PERSONAJE = (255, 0, 255)  # magenta
COLOR_CENTRO = (0, 0, 255)  # rojo (punto central)
COLOR_TEXTO_ON = (0, 255, 0)  # verde (bot activo)
COLOR_TEXTO_OFF = (0, 0, 255)  # rojo (bot inactivo)
>>>>>>> origin/main:core/vision/visualizador.py
COLOR_REFERENCIA = (100, 100, 255)  # azul claro (línea de referencia)


class Visualizador:

    def __init__(self, config):
        self.config = config

    def dibujar_descartados(self, frame: np.ndarray, descartados: list) -> np.ndarray:
<<<<<<< HEAD:test/vision/visualizador.py
        for (x, y, w, h, razon) in descartados:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.putText(frame, razon, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        return frame

    def dibujar_elementos(self, frame: np.ndarray, elementos: List[Elemento]) -> np.ndarray:
=======
        """
        Dibuja en ROJO los elementos que fueron descartados por los filtros.
        Muestra la razón por la que fue descartado.
        Útil para calibrar los filtros.
        """
        for x, y, w, h, razon in descartados:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
            cv2.putText(
                frame, razon, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1
            )
        return frame

    def dibujar_elementos(
        self, frame: np.ndarray, elementos: List[Elemento]
    ) -> np.ndarray:
        """
        Dibuja un rectángulo y punto central sobre cada elemento detectado.
        """
>>>>>>> origin/main:core/vision/visualizador.py
        for el in elementos:
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
            elif el.tipo == "agua":
                color = COLOR_AGUA
            else:
                color = COLOR_OBSTACULO

<<<<<<< HEAD:test/vision/visualizador.py
            cv2.rectangle(
                frame,
                (el.x, el.y),
                (el.x + el.w, el.y + el.h),
                color, 2
            )
=======
            # Rectángulo alrededor del elemento
            cv2.rectangle(frame, (el.x, el.y), (el.x + el.w, el.y + el.h), color, 2)

            # Punto en el centro
>>>>>>> origin/main:core/vision/visualizador.py
            cv2.circle(frame, (el.centro_x, el.centro_y), 4, COLOR_CENTRO, -1)

            if self.config.DEBUG:
                cv2.putText(
                    frame,
                    f"a={int(el.area)} p={el.proporcion}",
                    (el.x, el.y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    color,
                    1,
                )

        return frame

    def dibujar_zonas(self, frame: np.ndarray) -> np.ndarray:
        cfg = self.config
        alto, ancho = frame.shape[:2]

        if cfg.MOSTRAR_PERSONAJE:
            x_personaje = int(ancho * cfg.PERSONAJE_X_RATIO)
            cv2.line(frame, (x_personaje, 0), (x_personaje, alto), COLOR_PERSONAJE, 1)

        if cfg.MOSTRAR_ZONA:
            cv2.line(
                frame,
                (0, cfg.BANANA_ZONA_Y_INICIO),
                (ancho, cfg.BANANA_ZONA_Y_INICIO),
                COLOR_ZONA,
                1,
            )
            cv2.line(
                frame,
                (0, cfg.BANANA_ZONA_Y_FIN),
                (ancho, cfg.BANANA_ZONA_Y_FIN),
                COLOR_ZONA,
                1,
            )

        cv2.line(frame, (0, alto // 2), (ancho, alto // 2), COLOR_REFERENCIA, 1)

        return frame

<<<<<<< HEAD:test/vision/visualizador.py
    def dibujar_estado(self, frame: np.ndarray, bot_activo: bool, pausado: bool, conteos: dict) -> np.ndarray:
=======
    def dibujar_estado(
        self, frame: np.ndarray, bot_activo: bool, pausado: bool, conteos: dict
    ) -> np.ndarray:
        """
        Dibuja el estado general del bot en la esquina superior izquierda.
        """
        # Estado del bot
>>>>>>> origin/main:core/vision/visualizador.py
        if pausado:
            texto_estado = "PAUSADO"
            color = (0, 165, 255)
        elif bot_activo:
            texto_estado = "BOT: ON"
            color = COLOR_TEXTO_ON
        else:
            texto_estado = "BOT: OFF"
            color = COLOR_TEXTO_OFF

        cv2.putText(
            frame, texto_estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
        )

        y = 55
        for tipo, cantidad in conteos.items():
<<<<<<< HEAD:test/vision/visualizador.py
            cv2.putText(frame, f"{tipo}: {cantidad}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
=======
            texto = f"{tipo}: {cantidad}"
            cv2.putText(
                frame, texto, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
>>>>>>> origin/main:core/vision/visualizador.py
            y += 20

        return frame

    def dibujar_todo(
        self,
        frame: np.ndarray,
        elementos_por_tipo: dict,
        bot_activo: bool,
        pausado: bool,
        descartados: list = None,
    ) -> np.ndarray:
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
        frame = self.dibujar_estado(frame, bot_activo, pausado, conteos)

        return frame

    def mostrar_mascara(self, nombre: str, mascara: np.ndarray, escala: float = 0.5):
        pass  # desactivado
