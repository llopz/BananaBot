"""
ajuste_hsv.py
─────────────
Herramienta interactiva para calibrar rangos HSV en tiempo real.

Uso:
    python core/utils/ajuste_hsv.py
    python core/utils/ajuste_hsv.py --imagen ruta/a/imagen.png
    python core/utils/ajuste_hsv.py --imagen ruta/a/imagen.png --espacio HLS

Controles:
    ←/→  (A/D)  : cambiar imagen si se cargó una carpeta
    S           : guardar los valores actuales en la consola
    Q / ESC     : salir
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

CORE_DIR = Path(__file__).resolve().parents[1]
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

EXTENSIONES = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

ESPACIOS = {
    "HSV": cv2.COLOR_BGR2HSV,
    "HLS": cv2.COLOR_BGR2HLS,
}

# Nombres de los canales según espacio
CANALES = {
    "HSV": ("H", "S", "V"),
    "HLS": ("H", "L", "S"),
}

# Máximos de cada canal
MAXIMOS = {
    "HSV": (179, 255, 255),
    "HLS": (179, 255, 255),
}

VENTANA_CTRL   = "HSV Sliders"
VENTANA_ORIG   = "Original"
VENTANA_MASCARA = "Mascara"
VENTANA_RESULT = "Resultado (mascara aplicada)"


# ─── Valores de sliders (estado global compartido con callbacks) ───────────
_state = {
    "c0_lo": 0, "c0_hi": 179,
    "c1_lo": 0, "c1_hi": 255,
    "c2_lo": 0, "c2_hi": 255,
    "erode":  0,
    "dilate": 0,
}


def _noop(_):
    pass


def _crear_ventana_controles(espacio: str):
    nombres = CANALES[espacio]
    maximos = MAXIMOS[espacio]

    cv2.namedWindow(VENTANA_CTRL, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(VENTANA_CTRL, 600, 350)

    # Canal 0
    cv2.createTrackbar(f"{nombres[0]} bajo",  VENTANA_CTRL, _state["c0_lo"], maximos[0], lambda v: _state.update({"c0_lo": v}))
    cv2.createTrackbar(f"{nombres[0]} alto",  VENTANA_CTRL, _state["c0_hi"], maximos[0], lambda v: _state.update({"c0_hi": v}))
    # Canal 1
    cv2.createTrackbar(f"{nombres[1]} bajo",  VENTANA_CTRL, _state["c1_lo"], maximos[1], lambda v: _state.update({"c1_lo": v}))
    cv2.createTrackbar(f"{nombres[1]} alto",  VENTANA_CTRL, _state["c1_hi"], maximos[1], lambda v: _state.update({"c1_hi": v}))
    # Canal 2
    cv2.createTrackbar(f"{nombres[2]} bajo",  VENTANA_CTRL, _state["c2_lo"], maximos[2], lambda v: _state.update({"c2_lo": v}))
    cv2.createTrackbar(f"{nombres[2]} alto",  VENTANA_CTRL, _state["c2_hi"], maximos[2], lambda v: _state.update({"c2_hi": v}))
    # Morfología
    cv2.createTrackbar("Erode iter",   VENTANA_CTRL, _state["erode"],  10, lambda v: _state.update({"erode": v}))
    cv2.createTrackbar("Dilate iter",  VENTANA_CTRL, _state["dilate"], 10, lambda v: _state.update({"dilate": v}))


def _leer_sliders(espacio: str):
    nombres = CANALES[espacio]
    lo = np.array([
        cv2.getTrackbarPos(f"{nombres[0]} bajo", VENTANA_CTRL),
        cv2.getTrackbarPos(f"{nombres[1]} bajo", VENTANA_CTRL),
        cv2.getTrackbarPos(f"{nombres[2]} bajo", VENTANA_CTRL),
    ], dtype=np.uint8)
    hi = np.array([
        cv2.getTrackbarPos(f"{nombres[0]} alto", VENTANA_CTRL),
        cv2.getTrackbarPos(f"{nombres[1]} alto", VENTANA_CTRL),
        cv2.getTrackbarPos(f"{nombres[2]} alto", VENTANA_CTRL),
    ], dtype=np.uint8)
    erode  = cv2.getTrackbarPos("Erode iter",  VENTANA_CTRL)
    dilate = cv2.getTrackbarPos("Dilate iter", VENTANA_CTRL)
    return lo, hi, erode, dilate


def _aplicar_mascara(frame_bgr, espacio: str, lo, hi, erode, dilate):
    convertida = cv2.cvtColor(frame_bgr, ESPACIOS[espacio])
    mascara = cv2.inRange(convertida, lo, hi)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    if erode > 0:
        mascara = cv2.erode(mascara, kernel, iterations=erode)
    if dilate > 0:
        mascara = cv2.dilate(mascara, kernel, iterations=dilate)

    resultado = cv2.bitwise_and(frame_bgr, frame_bgr, mask=mascara)
    return mascara, resultado


def _imprimir_valores(espacio: str, lo, hi, nombre_imagen: str):
    nombres = CANALES[espacio]
    print("\n" + "=" * 50)
    print(f"  Imagen : {nombre_imagen}")
    print(f"  Espacio: {espacio}")
    print(f"  {nombres[0]} bajo/alto : {lo[0]}, {hi[0]}")
    print(f"  {nombres[1]} bajo/alto : {lo[1]}, {hi[1]}")
    print(f"  {nombres[2]} bajo/alto : {lo[2]}, {hi[2]}")
    print(f"\n  # settings.py")
    prefijo = "OBJETO"
    print(f"  {prefijo}_ESPACIO      = \"{espacio}\"")
    print(f"  {prefijo}_RANGO_BAJO   = [{lo[0]}, {lo[1]}, {lo[2]}]")
    print(f"  {prefijo}_RANGO_ALTO   = [{hi[0]}, {hi[1]}, {hi[2]}]")
    print("=" * 50 + "\n")


def _cargar_imagenes(ruta_arg: str) -> list:
    """Devuelve lista de paths de imagen a partir del argumento --imagen."""
    if ruta_arg:
        p = Path(ruta_arg)
        if p.is_dir():
            imgs = sorted(q for q in p.iterdir() if q.suffix.lower() in EXTENSIONES)
        elif p.is_file():
            imgs = [p]
        else:
            print(f"[ERROR] No se encontró: {ruta_arg}")
            sys.exit(1)
    else:
        # Intentar cargar Game.png de plantillas
        plantillas = CORE_DIR / "vision" / "detection" / "plantillas"
        game = plantillas / "Game.png"
        if game.exists():
            imgs = [game]
        else:
            # Tomar todas las imágenes de plantillas como fallback
            imgs = sorted(q for q in plantillas.iterdir() if q.suffix.lower() in EXTENSIONES)

    if not imgs:
        print("[ERROR] No se encontraron imágenes.")
        sys.exit(1)

    return imgs


def _redimensionar(frame, max_ancho=960, max_alto=600):
    h, w = frame.shape[:2]
    escala = min(max_ancho / w, max_alto / h, 1.0)
    if escala < 1.0:
        nuevo_w = int(w * escala)
        nuevo_h = int(h * escala)
        return cv2.resize(frame, (nuevo_w, nuevo_h), interpolation=cv2.INTER_AREA)
    return frame


def parse_args():
    parser = argparse.ArgumentParser(description="Calibrador de rangos HSV/HLS en tiempo real.")
    parser.add_argument(
        "--imagen", default="",
        help="Ruta de imagen o carpeta de imágenes. Sin argumento usa Game.png de plantillas.",
    )
    parser.add_argument(
        "--espacio", default="HSV", choices=["HSV", "HLS"],
        help="Espacio de color a usar (HSV o HLS). Por defecto HSV.",
    )
    parser.add_argument(
        "--lo", nargs=3, type=int, default=[0, 0, 0], metavar=("C0", "C1", "C2"),
        help="Valores iniciales del rango bajo (ej: --lo 18 200 200).",
    )
    parser.add_argument(
        "--hi", nargs=3, type=int, default=[179, 255, 255], metavar=("C0", "C1", "C2"),
        help="Valores iniciales del rango alto (ej: --hi 38 255 255).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    espacio = args.espacio

    # Valores iniciales
    _state["c0_lo"], _state["c1_lo"], _state["c2_lo"] = args.lo
    _state["c0_hi"], _state["c1_hi"], _state["c2_hi"] = args.hi

    imagenes = _cargar_imagenes(args.imagen)
    idx = 0

    cv2.namedWindow(VENTANA_ORIG,   cv2.WINDOW_NORMAL)
    cv2.namedWindow(VENTANA_MASCARA, cv2.WINDOW_NORMAL)
    cv2.namedWindow(VENTANA_RESULT, cv2.WINDOW_NORMAL)
    _crear_ventana_controles(espacio)

    print("\nControles de teclado:")
    print("  A / ←  : imagen anterior")
    print("  D / →  : imagen siguiente")
    print("  S      : imprimir valores actuales en consola")
    print("  Q/ESC  : salir\n")

    frame_orig = None
    ultimo_idx = -1

    while True:
        # Cargar imagen solo si cambia
        if idx != ultimo_idx:
            path = imagenes[idx]
            img = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if img is None:
                print(f"[WARN] No se pudo cargar: {path}")
                idx = (idx + 1) % len(imagenes)
                continue
            frame_orig = _redimensionar(img)
            ultimo_idx = idx
            print(f"[{idx + 1}/{len(imagenes)}] {path.name}")

        lo, hi, erode, dilate = _leer_sliders(espacio)
        mascara, resultado = _aplicar_mascara(frame_orig, espacio, lo, hi, erode, dilate)

        # Añadir texto con valores actuales sobre la ventana de máscara
        nombres = CANALES[espacio]
        texto = (
            f"{nombres[0]}:[{lo[0]}-{hi[0]}]  "
            f"{nombres[1]}:[{lo[1]}-{hi[1]}]  "
            f"{nombres[2]}:[{lo[2]}-{hi[2]}]"
        )
        mascara_bgr = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)
        cv2.putText(mascara_bgr, texto, (8, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow(VENTANA_ORIG,    frame_orig)
        cv2.imshow(VENTANA_MASCARA, mascara_bgr)
        cv2.imshow(VENTANA_RESULT,  resultado)

        key = cv2.waitKey(30) & 0xFF

        if key in (ord('q'), 27):  # Q o ESC
            break
        elif key in (ord('a'), 81, 2):  # A o ←
            idx = (idx - 1) % len(imagenes)
        elif key in (ord('d'), 83, 3):  # D o →
            idx = (idx + 1) % len(imagenes)
        elif key == ord('s'):
            _imprimir_valores(espacio, lo, hi, imagenes[idx].name)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
