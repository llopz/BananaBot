import mss as mss_lib
import numpy as np
import cv2
import pygetwindow as gw


class Capturador:

    def __init__(self, titulo_ventana: str, refrescar_cada: int = 60):
        self.titulo_ventana = titulo_ventana
        self.refrescar_cada = refrescar_cada
        self._sct = None
        self._region = None
        self._frames_contados = 0

        # Buscar la ventana al inicializar
        self._actualizar_region()

    def _actualizar_region(self) -> bool:
        ventanas = gw.getWindowsWithTitle(self.titulo_ventana)

        if not ventanas:
            print(f"[CAPTURA] No se encontró ventana '{self.titulo_ventana}'")
            return False

        ventana = ventanas[0]

        if ventana.width <= 0 or ventana.height <= 0:
            print(f"[CAPTURA] Ventana encontrada pero con tamaño inválido")
            return False

        self._region = {
            "top": ventana.top,
            "left": ventana.left,
            "width": ventana.width,
            "height": ventana.height,
        }

        return True

    def iniciar(self):
        self._sct = mss_lib.mss()

    def detener(self):
        if self._sct:
            self._sct.close()

    def capturar(self) -> np.ndarray:
        if self._sct is None:
            raise RuntimeError("Debes llamar a iniciar() antes de capturar()")

        # Refrescar coordenadas periódicamente
        self._frames_contados += 1
        if self._frames_contados % self.refrescar_cada == 0:
            self._actualizar_region()

        if self._region is None:
            raise RuntimeError(
                f"No se encontró la ventana '{self.titulo_ventana}'. ¿Está abierto el emulador?"
            )

        screenshot = self._sct.grab(self._region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

    def capturar_y_congelar(self, frame_congelado: np.ndarray, pausado: bool):
        if pausado and frame_congelado is not None:
            return frame_congelado.copy(), frame_congelado

        nuevo_frame = self.capturar()
        return nuevo_frame, nuevo_frame

    @property
    def ancho(self) -> int:
        return self._region["width"] if self._region else 0

    @property
    def alto(self) -> int:
        return self._region["height"] if self._region else 0

    def __enter__(self):
        self.iniciar()
        return self

    def __exit__(self, *args):
        self.detener()