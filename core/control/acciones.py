# ============================================================
# control/acciones.py
# Módulo de acciones para Banana Kong en MuMu Player
# ============================================================
# Teclas configuradas en MuMu:
#     C         → salto normal (tap)
#     SPACE     → planear (mantener presionado)
#     DOWN      → bajar
#
# Acciones:
#     0 - NADA    : no hacer nada
#     1 - SALTAR  : tap C
#     2 - PLANEAR : mantener SPACE
#     3 - BAJAR   : tap flecha abajo

import pyautogui
import pygetwindow as gw
import time
import signal
import sys

pyautogui.FAILSAFE = False

TECLA_SALTAR = "c"
TECLA_PLANEAR = "space"
TECLA_BAJAR = "down"

NADA = 0
SALTAR = 1
PLANEAR = 2
BAJAR = 3
N_ACCIONES = 4

TITULO_VENTANA = "Android Device"


class ModuloAcciones:

    def __init__(self):
        self.ventana = None
        self._planeando = False
        self._actualizar_ventana()
        signal.signal(signal.SIGINT, self._parada_emergencia)
        print("Módulo de acciones listo")
        print("  C=saltar | SPACE=planear | DOWN=bajar")

    def _parada_emergencia(self, sig=None, frame=None):
        """Suelta todas las teclas y sale limpio."""
        pyautogui.keyUp(TECLA_PLANEAR)
        self._planeando = False
        print("\n[CONTROL] Parada de emergencia")
        sys.exit(0)

    def parar(self):
        self._parada_emergencia()

    def _actualizar_ventana(self):
        ventanas = gw.getWindowsWithTitle(TITULO_VENTANA)
        if ventanas:
            self.ventana = ventanas[0]
            return True
        print(f"[CONTROL] No se encontró ventana '{TITULO_VENTANA}'")
        return False

    def _enfocar_ventana(self):
        if self.ventana is None:
            self._actualizar_ventana()
        try:
            self.ventana.activate()
        except Exception:
            pass

    def ejecutar(self, accion: int):
        self._enfocar_ventana()

        # Si venía planeando y la nueva acción es distinta → soltar SPACE
        if self._planeando and accion != PLANEAR:
            pyautogui.keyUp(TECLA_PLANEAR)
            self._planeando = False

        if accion == NADA:
            pass

        elif accion == SALTAR:
            pyautogui.press(TECLA_SALTAR)

        elif accion == PLANEAR:
            if not self._planeando:
                pyautogui.keyDown(TECLA_PLANEAR)
                self._planeando = True

        elif accion == BAJAR:
            pyautogui.press(TECLA_BAJAR)

    def probar(self):
        """Modo prueba manual para verificar que cada acción funciona."""
        print("=== PRUEBA DE ACCIONES ===")
        print("  1 → SALTAR | 2 → PLANEAR (mantén) | 3 → BAJAR | q → salir")
        print("Tienes 3 segundos para enfocar MuMu...")
        time.sleep(3)

        import keyboard

        print("Listo.")

        try:
            while True:
                if keyboard.is_pressed("1"):
                    print("[TEST] SALTAR")
                    self.ejecutar(SALTAR)
                    time.sleep(0.3)

                elif keyboard.is_pressed("2"):
                    self.ejecutar(PLANEAR)
                    time.sleep(0.05)

                elif keyboard.is_pressed("3"):
                    print("[TEST] BAJAR")
                    self.ejecutar(BAJAR)
                    time.sleep(0.3)

                elif keyboard.is_pressed("q"):
                    break

                else:
                    self.ejecutar(NADA)
                    time.sleep(0.05)

        finally:
            pyautogui.keyUp(TECLA_PLANEAR)
            print("Prueba terminada.")


if __name__ == "__main__":
    modulo = ModuloAcciones()
    modulo.probar()
