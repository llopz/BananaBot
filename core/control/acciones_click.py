import pyautogui
import time

NADA = "nada"
SALTAR = "saltar"
PLANEAR = "planear"
BAJAR = "bajar"
DASH = "dash"


class ModuloAcciones:

    def __init__(
        self,
    ):
        self.x = None
        self.y = None
        self.presionado = False
        self.ultimo_salto = 0
        self.cooldown = 0.25

    def actualizar_posicion(self, x, y):
        self.x = x
        self.y = y

    def ejecutar(self, accion):

        if accion == SALTAR:
            self.saltar()

        elif accion == PLANEAR:
            self.planear()

        elif accion == BAJAR:
            self.bajar()

        elif accion == DASH:
            self.dash()

        elif accion == NADA:
            self.soltar()

    def saltar(self):

        ahora = time.time()

        if ahora - self.ultimo_salto > self.cooldown:
            pyautogui.click()
            self.ultimo_salto = ahora

    def planear(self):

        if not self.presionado:
            pyautogui.mouseDown()
            self.presionado = True

    def soltar(self):

        if self.presionado:
            pyautogui.mouseUp()
            self.presionado = False

    def bajar(self):

        pyautogui.mouseDown()
        pyautogui.moveRel(0, 50, duration=0.1)
        pyautogui.mouseUp()
        pyautogui.moveRel(0, -50, duration=0.1)

    def dash(self):

        pyautogui.mouseDown(self.x, self.y)
        pyautogui.moveRel(20, 0, duration=0.1)
        pyautogui.mouseUp()
        pyautogui.moveRel(-20, 0, duration=0.1)

    def parar(self):
        pyautogui.mouseUp()
