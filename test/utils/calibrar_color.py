# ============================================================
# utils/calibrar_color.py
# Utilidad para encontrar los valores HSV de cualquier elemento
# ============================================================
#
# Ejecuta este script cuando:
# - Quieres detectar un elemento nuevo (obstáculos, barriles, etc.)
# - La detección actual tiene muchos falsos positivos
# - El juego actualizó sus colores
#
# Cómo usarlo:
#   python utils/calibrar_color.py
#
# Luego haz click sobre el elemento que quieres detectar
# en la ventana que se abre.
# ============================================================

import mss
import numpy as np
import cv2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

# ─── Estado del click ────────────────────────────────────────
click_x, click_y = -1, -1
click_nuevo = False
historial = []  # guarda todos los clicks para comparar


def cuando_hago_click(evento, x, y, flags, param):
    global click_x, click_y, click_nuevo
    if evento == cv2.EVENT_LBUTTONDOWN:
        click_x, click_y = x, y
        click_nuevo = True


def calibrar():
    global click_nuevo

    print("=" * 55)
    print("  CALIBRADOR DE COLOR HSV")
    print("=" * 55)
    print()
    print("Haz click sobre el elemento que quieres detectar.")
    print("Haz click en varios puntos del mismo elemento para")
    print("ver si el color es consistente.")
    print()
    print("Presiona Q para salir.")
    print()

    cv2.namedWindow("Calibrador")
    cv2.setMouseCallback("Calibrador", cuando_hago_click)

    with mss.mss() as sct:
        while True:
            screenshot = sct.grab(settings.REGION)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            if click_nuevo:
                click_nuevo = False

                # Leer el píxel exacto donde hizo click
                pixel_bgr = img[click_y, click_x]
                b, g, r = pixel_bgr

                # Convertir ese píxel a HSV
                pixel_para_hsv = np.uint8([[[b, g, r]]])
                pixel_hsv = cv2.cvtColor(pixel_para_hsv, cv2.COLOR_BGR2HSV)
                h, s, v = pixel_hsv[0][0]

                # Guardar en historial
                historial.append((h, s, v))

                # Calcular rango sugerido con margen
                h_bajo = max(0,   h - 10)
                h_alto = min(180, h + 10)
                s_bajo = max(0,   s - 40)
                v_bajo = max(0,   v - 40)

                print(f"Click #{len(historial)} en ({click_x}, {click_y})")
                print(f"  BGR : B={b}  G={g}  R={r}")
                print(f"  HSV : H={h}  S={s}  V={v}")
                print(f"  Rango sugerido para settings.py:")
                print(f"    _HSV_BAJO = [{h_bajo}, {s_bajo}, {v_bajo}]")
                print(f"    _HSV_ALTO = [{h_alto}, 255, 255]")

                # Si hay varios clicks, mostrar el rango que los cubre a todos
                if len(historial) > 1:
                    h_vals = [c[0] for c in historial]
                    s_vals = [c[1] for c in historial]
                    v_vals = [c[2] for c in historial]
                    print(f"  Rango que cubre todos los clicks:")
                    print(f"    _HSV_BAJO = [{max(0, min(h_vals)-10)}, {max(0, min(s_vals)-40)}, {max(0, min(v_vals)-40)}]")
                    print(f"    _HSV_ALTO = [{min(180, max(h_vals)+10)}, 255, 255]")

                print()

                # Marcar el punto en la imagen
                cv2.circle(img, (click_x, click_y), 6, (0, 255, 255), -1)
                cv2.circle(img, (click_x, click_y), 7, (0, 0, 0), 1)

                # Mostrar muestra de color
                muestra = np.zeros((50, 150, 3), dtype=np.uint8)
                muestra[:] = (b, g, r)
                cv2.putText(muestra, f"H={h} S={s} V={v}", (5, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                cv2.imshow("Color del pixel", muestra)

            # Dibujar marcas de clicks anteriores
            for i, (hx, sx, vx) in enumerate(historial):
                pass  # los círculos se borran con cada frame nuevo

            cv2.imshow("Calibrador", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

    if historial:
        h_vals = [c[0] for c in historial]
        s_vals = [c[1] for c in historial]
        v_vals = [c[2] for c in historial]
        print("=" * 55)
        print("  RANGO FINAL (basado en todos tus clicks)")
        print("=" * 55)
        print(f"  _HSV_BAJO = [{max(0, min(h_vals)-10)}, {max(0, min(s_vals)-40)}, {max(0, min(v_vals)-40)}]")
        print(f"  _HSV_ALTO = [{min(180, max(h_vals)+10)}, 255, 255]")


if __name__ == "__main__":
    calibrar()