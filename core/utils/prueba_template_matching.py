import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


CORE_DIR = Path(__file__).resolve().parents[1]
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

import config.settings as settings
from vision.detection.base_detector import BaseDetector


METODOS_TEMPLATE = {
    "ccoeff_normed": cv2.TM_CCOEFF_NORMED,
    "ccorr_normed": cv2.TM_CCORR_NORMED,
    "sqdiff_normed": cv2.TM_SQDIFF_NORMED,
}

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
ESCALA_TEMPLATE = 1.10
ANCHO_OBJETIVO = 960
ALTO_OBJETIVO = 540
ROI_PADDING = 12
UMBRAL_FLOR = 0.55
UMBRAL_PLATAFORMA_MADERA = 0.18
FLEX_HSV_DELTA = 0.12


def normalizar_tipo_base(tipo_base):
    return tipo_base.strip().replace(" ", "_").replace("-", "_")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prueba rapida de template matching sobre una imagen."
    )
    parser.add_argument(
        "--imagen",
        default="",
        help="Ruta de la imagen donde se va a detectar. Por defecto usa Game.png en la carpeta de plantillas.",
    )
    parser.add_argument(
        "--carpeta-plantillas",
        default="",
        help=(
            "Carpeta de plantillas. Si no se indica, usa core/vision/detection/plantillas."
        ),
    )
    parser.add_argument(
        "--metodo",
        default="ccoeff_normed",
        choices=METODOS_TEMPLATE.keys(),
        help="Metodo de cv2.matchTemplate.",
    )
    parser.add_argument(
        "--umbral",
        type=float,
        default=0.7,
        help=(
            "Umbral de confianza (0 a 1) aplicado al mapa de matchTemplate. "
            "Para sqdiff se invierte automaticamente (1 - score)."
        ),
    )
    parser.add_argument(
        "--iou-nms",
        type=float,
        default=0.3,
        help="Umbral IoU para eliminar duplicados (NMS).",
    )
    parser.add_argument(
        "--group-threshold",
        type=int,
        default=1,
        help="Parametro groupThreshold para cv2.groupRectangles. Por defecto 1.",
    )
    parser.add_argument(
        "--group-eps",
        type=float,
        default=0.5,
        help="Parametro eps para cv2.groupRectangles. Por defecto 0.5.",
    )
    parser.add_argument(
        "--gris",
        action="store_true",
        help="Convierte imagen y plantillas a escala de grises antes de detectar.",
    )
    parser.add_argument(
        "--thresh",
        default="ninguno",
        choices=["ninguno", "otsu", "binario", "adaptativo"],
        help=(
            "Thresholding antes de detectar. "
            "otsu=umbral automatico, binario=umbral fijo 127, "
            "adaptativo=umbral por zonas. Por defecto ninguno."
        ),
    )
    parser.add_argument(
        "--thresh-valor",
        type=int,
        default=127,
        help="Valor de umbral para --thresh binario (0-255). Por defecto 127.",
    )
    parser.add_argument(
        "--sin-ventana",
        action="store_true",
        help="No abre ventana de visualizacion.",
    )
    parser.add_argument(
        "--salida",
        default="",
        help="Ruta de salida para guardar imagen con detecciones.",
    )
    parser.add_argument(
        "--filtro",
        nargs="+",
        default=[],
        help="Nombres de plantillas a usar (sin extension). Si no se indica, usa todas.",
    )
    parser.add_argument(
        "--excluir",
        nargs="+",
        default=["Game"],
        help="Nombres de plantillas a excluir (sin extension). Por defecto excluye Game.",
    )
    parser.add_argument(
        "--sin-agrupado",
        action="store_true",
        help="No aplicar NMS; muestra todas las coincidencias (puede haber muchas superpuestas).",
    )
    parser.add_argument(
        "--mostrar-crudas",
        action="store_true",
        help="Muestra una ventana adicional con detecciones crudas antes del agrupado.",
    )
    parser.add_argument(
        "--topk-debug",
        type=int,
        default=5,
        help="Cantidad de mejores coincidencias a imprimir por plantilla para depuracion.",
    )
    return parser.parse_args()


def cargar_imagen(path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar imagen: {path}")
    return img


def obtener_carpeta_plantillas(arg_carpeta):
    if arg_carpeta:
        carpeta = Path(arg_carpeta)
    else:
        raiz_core = Path(__file__).resolve().parents[1]
        carpeta = raiz_core / "vision" / "detection" / "plantillas"

    if not carpeta.exists() or not carpeta.is_dir():
        raise FileNotFoundError(
            f"Carpeta de plantillas no encontrada: {carpeta}. "
            "Crea la carpeta y coloca tus imagenes ahi."
        )

    return carpeta


def listar_plantillas(carpeta, filtro=None, excluir=None):
    plantillas = sorted(
        p
        for p in carpeta.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES_IMAGEN
    )
    if filtro:
        filtro_set = {n.lower() for n in filtro}
        plantillas = [p for p in plantillas if p.stem.lower() in filtro_set]
    if excluir:
        excluir_set = {n.lower() for n in excluir}
        plantillas = [p for p in plantillas if p.stem.lower() not in excluir_set]
    if not plantillas:
        raise FileNotFoundError(
            f"No hay plantillas en {carpeta}. "
            "Agrega imagenes .png/.jpg/.jpeg/.bmp/.webp"
        )
    return plantillas


def preprocesar(img_gris, modo, thresh_valor):
    if modo == "ninguno":
        return img_gris
    if modo == "otsu":
        _, resultado = cv2.threshold(
            img_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return resultado
    if modo == "binario":
        _, resultado = cv2.threshold(
            img_gris, thresh_valor, 255, cv2.THRESH_BINARY
        )
        return resultado
    if modo == "adaptativo":
        resultado = cv2.adaptiveThreshold(
            img_gris, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )
        return resultado
    return img_gris


def iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter_area

    if union <= 0:
        return 0.0
    return inter_area / union


def nms(detecciones, iou_threshold):
    if not detecciones:
        return []

    detecciones = sorted(detecciones, key=lambda d: d["score"], reverse=True)
    filtradas = []

    for det in detecciones:
        mantener = True
        for keep in filtradas:
            if det["label"] != keep["label"]:
                continue
            if iou(det["box"], keep["box"]) > iou_threshold:
                mantener = False
                break
        if mantener:
            filtradas.append(det)

    return filtradas


def agrupar_con_group_rectangles(detecciones, group_threshold, eps):
    agrupadas = []
    if not detecciones:
        return agrupadas

    labels = sorted({d["label"] for d in detecciones})
    for label in labels:
        subset = [d for d in detecciones if d["label"] == label]
        rects = []
        for d in subset:
            x1, y1, x2, y2 = d["box"]
            w = max(1, x2 - x1)
            h = max(1, y2 - y1)
            rect = [int(x1), int(y1), int(w), int(h)]
            rects.append(rect)
            rects.append(rect)

        if not rects:
            continue

        rects_grouped, weights = cv2.groupRectangles(
            rects,
            groupThreshold=max(0, int(group_threshold)),
            eps=float(eps),
        )

        for i, rect in enumerate(rects_grouped):
            x, y, w, h = [int(v) for v in rect]
            x2 = x + w
            y2 = y + h
            cx = x + w // 2
            cy = y + h // 2

            score = 0.0
            for d in subset:
                dx1, dy1, dx2, dy2 = d["box"]
                dcx = (dx1 + dx2) // 2
                dcy = (dy1 + dy2) // 2
                if x <= dcx <= x2 and y <= dcy <= y2:
                    score = max(score, d["score"])

            if score <= 0.0:
                score = max((d["score"] for d in subset), default=0.0)

            agrupadas.append(
                {
                    "label": label,
                    "score": float(score),
                    "box": (x, y, x2, y2),
                    "click": (cx, cy),
                    "weight": int(weights[i]) if i < len(weights) else 0,
                }
            )

    return agrupadas


def find_click_positions_from_detecciones(detecciones, group_threshold=1, eps=0.5):
    agrupadas = agrupar_con_group_rectangles(detecciones, group_threshold, eps)
    return [d["click"] for d in agrupadas]


def findClickPositions(
    needle_img_path,
    haystack_img_path,
    threshold=0.5,
    debug_mode=None,
    method=cv2.TM_CCOEFF_NORMED,
    group_threshold=1,
    eps=0.5,
):
    haystack_img = cv2.imread(str(haystack_img_path), cv2.IMREAD_UNCHANGED)
    needle_img = cv2.imread(str(needle_img_path), cv2.IMREAD_UNCHANGED)

    if haystack_img is None:
        raise FileNotFoundError(f"No se pudo cargar haystack: {haystack_img_path}")
    if needle_img is None:
        raise FileNotFoundError(f"No se pudo cargar needle: {needle_img_path}")

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]
    result = cv2.matchTemplate(haystack_img, needle_img, method)

    if method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
        locations = np.where(result <= threshold)
    else:
        locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), int(needle_w), int(needle_h)]
        # Truco del tutorial: duplicar para conservar detecciones aisladas.
        rectangles.append(rect)
        rectangles.append(rect)

    rectangles, _weights = cv2.groupRectangles(
        rectangles,
        groupThreshold=max(0, int(group_threshold)),
        eps=float(eps),
    )

    points = []
    if len(rectangles):
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS

        for (x, y, w, h) in rectangles:
            center_x = x + int(w / 2)
            center_y = y + int(h / 2)
            points.append((center_x, center_y))

            if debug_mode == "rectangles":
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                cv2.rectangle(
                    haystack_img,
                    top_left,
                    bottom_right,
                    color=line_color,
                    lineType=line_type,
                    thickness=2,
                )
            elif debug_mode == "points":
                cv2.drawMarker(
                    haystack_img,
                    (center_x, center_y),
                    color=marker_color,
                    markerType=marker_type,
                    markerSize=40,
                    thickness=2,
                )

        if debug_mode in ("rectangles", "points"):
            cv2.imshow("Matches", haystack_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    return points


def obtener_mapa_confianza(score_map, metodo):
    if metodo == cv2.TM_SQDIFF_NORMED:
        return 1.0 - score_map
    return score_map


def topk_confianzas(confidence_map, k):
    if k <= 0:
        return []
    flat = confidence_map.ravel()
    if flat.size == 0:
        return []
    k = min(k, flat.size)
    idxs = np.argpartition(flat, -k)[-k:]
    idxs = idxs[np.argsort(flat[idxs])[::-1]]
    puntos = []
    ancho = confidence_map.shape[1]
    for idx in idxs:
        y = int(idx // ancho)
        x = int(idx % ancho)
        puntos.append((x, y, float(flat[idx])))
    return puntos


def extraer_detecciones(score_map, template_w, template_h, threshold, label, metodo):
    detecciones = []
    confidence_map = obtener_mapa_confianza(score_map, metodo)

    # np.where devuelve primero Y y luego X; invertimos para tener (X, Y).
    locations = np.where(confidence_map >= threshold)
    locations = list(zip(*locations[::-1]))

    for x, y in locations:
        x1 = int(x)
        y1 = int(y)
        x2 = int(x + template_w)
        y2 = int(y + template_h)
        detecciones.append(
            {
                "label": label,
                "score": float(confidence_map[y, x]),
                "box": (x1, y1, x2, y2),
            }
        )

    return detecciones


def extraer_detecciones_en_roi(
    score_map,
    template_w,
    template_h,
    threshold,
    label,
    metodo,
    offset_x,
    offset_y,
):
    detecciones = extraer_detecciones(
        score_map=score_map,
        template_w=template_w,
        template_h=template_h,
        threshold=threshold,
        label=label,
        metodo=metodo,
    )
    for det in detecciones:
        x1, y1, x2, y2 = det["box"]
        det["box"] = (x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y)
    return detecciones


def construir_hsv_config(tipo_base):
    prefix = normalizar_tipo_base(tipo_base).upper()
    required = [
        f"{prefix}_RANGO_BAJO",
        f"{prefix}_RANGO_ALTO",
        f"{prefix}_AREA_MIN_PCT",
        f"{prefix}_AREA_MAX_PCT",
        f"{prefix}_PROP_MIN",
        f"{prefix}_PROP_MAX",
    ]
    if not all(hasattr(settings, name) for name in required):
        return None

    return {
        "rango_bajo": getattr(settings, f"{prefix}_RANGO_BAJO"),
        "rango_alto": getattr(settings, f"{prefix}_RANGO_ALTO"),
        "area_min_pct": getattr(settings, f"{prefix}_AREA_MIN_PCT"),
        "area_max_pct": getattr(settings, f"{prefix}_AREA_MAX_PCT"),
        "prop_min": getattr(settings, f"{prefix}_PROP_MIN"),
        "prop_max": getattr(settings, f"{prefix}_PROP_MAX"),
        "espacio": getattr(settings, f"{prefix}_ESPACIO", "HSV"),
        "zona_y_inicio": getattr(settings, f"{prefix}_ZONA_Y_INICIO", 0),
        "zona_y_fin": getattr(settings, f"{prefix}_ZONA_Y_FIN", None),
        "erode_kernel": getattr(settings, f"{prefix}_ERODE_KERNEL", (3, 3)),
        "erode_iter": getattr(settings, f"{prefix}_ERODE_ITER", 1),
        "dilate_kernel": getattr(settings, f"{prefix}_DILATE_KERNEL", (3, 3)),
        "dilate_iter": getattr(settings, f"{prefix}_DILATE_ITER", 1),
    }


def detectar_candidatos_hsv(frame, tipo_base):
    cfg = construir_hsv_config(tipo_base)
    if cfg is None:
        return [], None

    detector_base = BaseDetector(settings)
    elementos, _descartados, mascara = detector_base._detectar_elemento(
        frame,
        cfg["rango_bajo"],
        cfg["rango_alto"],
        cfg["area_min_pct"],
        cfg["area_max_pct"],
        cfg["prop_min"],
        cfg["prop_max"],
        tipo_base.lower(),
        zona_y_inicio=cfg["zona_y_inicio"],
        zona_y_fin=cfg["zona_y_fin"],
        espacio=cfg["espacio"],
        erode_kernel=cfg["erode_kernel"],
        erode_iter=cfg["erode_iter"],
        dilate_kernel=cfg["dilate_kernel"],
        dilate_iter=cfg["dilate_iter"],
    )
    return elementos, mascara


def calcular_resize_desde_settings(plantilla_base, tipo_base):
    cfg = construir_hsv_config(tipo_base)
    if cfg is None:
        return None

    area_frame = ANCHO_OBJETIVO * ALTO_OBJETIVO
    area_min = cfg["area_min_pct"] * area_frame
    area_max = cfg["area_max_pct"] * area_frame
    area_objetivo = (area_min + area_max) / 2.0

    ratio_template = plantilla_base.shape[1] / max(1, plantilla_base.shape[0])
    ratio_objetivo = min(
        max(ratio_template, cfg["prop_min"]),
        cfg["prop_max"],
    )

    nuevo_w = max(1, int(round((area_objetivo * ratio_objetivo) ** 0.5)))
    nuevo_h = max(1, int(round((area_objetivo / ratio_objetivo) ** 0.5)))
    return nuevo_w, nuevo_h


def main():
    args = parse_args()

    carpeta_plantillas = obtener_carpeta_plantillas(args.carpeta_plantillas)
    if args.imagen:
        imagen_path = Path(args.imagen)
    else:
        imagen_path = carpeta_plantillas / "Game.png"
        if not imagen_path.exists():
            raise FileNotFoundError(
                "No se especifico --imagen y no se encontro Game.png en la carpeta de plantillas."
            )
    plantilla_paths = listar_plantillas(carpeta_plantillas, filtro=args.filtro, excluir=args.excluir)

    imagen = cargar_imagen(imagen_path)
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    usar_gris = args.gris or args.thresh != "ninguno"
    if usar_gris:
        imagen_proc = preprocesar(imagen_gris, args.thresh, args.thresh_valor)
    else:
        imagen_proc = imagen.copy()

    metodo = METODOS_TEMPLATE[args.metodo]
    threshold = min(max(args.umbral, 0.0), 1.0)

    detecciones = []
    print(f"Escala fija activa: {ESCALA_TEMPLATE:.2f}")
    mascaras_hsv = {}

    for path_plantilla in plantilla_paths:
        tipo_base = path_plantilla.stem
        tipo_normalizado = normalizar_tipo_base(tipo_base).lower()
        threshold_plantilla = threshold
        if tipo_base.lower() == "flor":
            threshold_plantilla = min(threshold_plantilla, UMBRAL_FLOR)
            print(
                f"[INFO] Umbral especial para Flor: {threshold_plantilla:.2f} "
                f"(umbral base={threshold:.2f})"
            )
        if tipo_normalizado == "plataforma_madera":
            threshold_plantilla = min(threshold_plantilla, UMBRAL_PLATAFORMA_MADERA)
            print(
                f"[INFO] Umbral especial para Plataforma madera: {threshold_plantilla:.2f} "
                f"(umbral base={threshold:.2f})"
            )

        # Para el flujo guiado por HSV, usamos un umbral ligeramente mas flexible.
        threshold_hsv = max(0.0, threshold_plantilla - FLEX_HSV_DELTA)
        plantilla = cargar_imagen(path_plantilla)
        if usar_gris:
            plantilla_gris = cv2.cvtColor(plantilla, cv2.COLOR_BGR2GRAY)
            plantilla_base = preprocesar(plantilla_gris, args.thresh, args.thresh_valor)
        else:
            plantilla_base = plantilla

        ih, iw = imagen_proc.shape[:2]
        resize_settings = calcular_resize_desde_settings(plantilla_base, tipo_base)
        if tipo_normalizado in ("cueva", "plataforma_madera"):
            resize_settings = None
        if resize_settings is not None:
            nuevo_w, nuevo_h = resize_settings
            escala_info = f"settings-{tipo_base.lower()} {nuevo_w}x{nuevo_h}"
        else:
            nuevo_w = max(1, int(round(plantilla_base.shape[1] * ESCALA_TEMPLATE)))
            nuevo_h = max(1, int(round(plantilla_base.shape[0] * ESCALA_TEMPLATE)))
            escala_info = f"escala={ESCALA_TEMPLATE:.2f}"
        if tipo_normalizado in ("cueva", "plataforma_madera"):
            candidatos_hsv, mascara_hsv = [], None
            print(f"[INFO] HSV desactivado para {tipo_base}")
        else:
            candidatos_hsv, mascara_hsv = detectar_candidatos_hsv(imagen, tipo_base)
        if mascara_hsv is not None:
            mascaras_hsv[tipo_base] = mascara_hsv
            print(f"[HSV] {tipo_base}: candidatos={len(candidatos_hsv)}")

        if candidatos_hsv:
            mejor_score_global = 0.0
            for idx, candidato in enumerate(candidatos_hsv, start=1):
                roi_x1 = max(0, candidato.x - ROI_PADDING)
                roi_y1 = max(0, candidato.y - ROI_PADDING)
                roi_x2 = min(iw, candidato.x + candidato.w + ROI_PADDING)
                roi_y2 = min(ih, candidato.y + candidato.h + ROI_PADDING)

                roi = imagen_proc[roi_y1:roi_y2, roi_x1:roi_x2]
                if roi.size == 0:
                    continue

                plantilla_roi = cv2.resize(
                    plantilla_base,
                    (max(1, candidato.w), max(1, candidato.h)),
                    interpolation=cv2.INTER_LINEAR,
                )
                th, tw = plantilla_roi.shape[:2]
                if th > roi.shape[0] or tw > roi.shape[1] or th < 2 or tw < 2:
                    continue

                score_map = cv2.matchTemplate(roi, plantilla_roi, metodo)
                confidence_map = obtener_mapa_confianza(score_map, metodo)
                mejor_score = float(np.max(confidence_map)) if confidence_map.size else 0.0
                mejor_score_global = max(mejor_score_global, mejor_score)

                print(
                    f"[DEBUG] {tipo_base} hsv_roi={idx} size={candidato.w}x{candidato.h}: "
                    f"mejor_confianza={mejor_score:.4f}"
                )
                for rank, (px, py, pscore) in enumerate(
                    topk_confianzas(confidence_map, args.topk_debug), start=1
                ):
                    print(f"  top{rank}: score={pscore:.4f} en (x={px + roi_x1}, y={py + roi_y1})")

                label_con_escala = f"{tipo_base}@hsv-{candidato.w}x{candidato.h}"
                detecciones.extend(
                    extraer_detecciones_en_roi(
                        score_map=score_map,
                        template_w=tw,
                        template_h=th,
                        threshold=threshold_hsv,
                        label=label_con_escala,
                        metodo=metodo,
                        offset_x=roi_x1,
                        offset_y=roi_y1,
                    )
                )

            print(f"[DEBUG] {tipo_base} hsv-guided: mejor_global={mejor_score_global:.4f}")
            continue

        plantilla_proc = cv2.resize(
            plantilla_base,
            (nuevo_w, nuevo_h),
            interpolation=cv2.INTER_LINEAR,
        )

        th, tw = plantilla_proc.shape[:2]
        if th > ih or tw > iw or th < 2 or tw < 2:
            print(f"[WARN] Plantilla fuera de rango tras ajuste {escala_info}: {path_plantilla}")
            continue

        score_map = cv2.matchTemplate(imagen_proc, plantilla_proc, metodo)
        confidence_map = obtener_mapa_confianza(score_map, metodo)
        mejor_score = float(np.max(confidence_map)) if confidence_map.size else 0.0

        print(
            f"[DEBUG] {tipo_base} {escala_info}: "
            f"mejor_confianza={mejor_score:.4f}"
        )
        for i, (px, py, pscore) in enumerate(
            topk_confianzas(confidence_map, args.topk_debug), start=1
        ):
            print(f"  top{i}: score={pscore:.4f} en (x={px}, y={py})")

        label_con_escala = f"{tipo_base}@{nuevo_w}x{nuevo_h}"
        detecciones.extend(
            extraer_detecciones(
                score_map=score_map,
                template_w=tw,
                template_h=th,
                threshold=threshold_plantilla,
                label=label_con_escala,
                metodo=metodo,
            )
        )

    detecciones_crudas = detecciones
    if args.sin_agrupado:
        detecciones_finales = []
        for d in detecciones_crudas:
            x1, y1, x2, y2 = d["box"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            d2 = dict(d)
            d2["click"] = (cx, cy)
            d2["weight"] = 1
            detecciones_finales.append(d2)
    else:
        detecciones_finales = agrupar_con_group_rectangles(
            detecciones_crudas,
            args.group_threshold,
            args.group_eps,
        )

    click_points = find_click_positions_from_detecciones(
        detecciones_crudas,
        group_threshold=args.group_threshold,
        eps=args.group_eps,
    ) if not args.sin_agrupado else [d["click"] for d in detecciones_finales]

    imagen_debug = imagen.copy()
    for det in detecciones_finales:
        x1, y1, x2, y2 = det["box"]
        score = det["score"]
        label = det["label"]
        cx, cy = det["click"]

        cv2.rectangle(imagen_debug, (x1, y1), (x2, y2), (0, 220, 0), 2)
        cv2.circle(imagen_debug, (cx, cy), 3, (0, 0, 255), -1)
        cv2.putText(
            imagen_debug,
            f"{label} {score:.2f}",
            (x1, max(16, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (30, 30, 30),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            imagen_debug,
            f"{label} {score:.2f}",
            (x1, max(16, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    print(f"Plantillas usadas: {len(plantilla_paths)}")
    print(f"Detecciones crudas (threshold): {len(detecciones_crudas)}")
    if args.sin_agrupado:
        print("Agrupado: desactivado")
    else:
        print(f"Detecciones finales (groupRectangles): {len(detecciones_finales)}")
    print(f"Click points: {len(click_points)}")
    for i, (cx, cy) in enumerate(click_points, start=1):
        print(f"  click[{i}] = (x={cx}, y={cy})")
    for i, det in enumerate(detecciones_finales, start=1):
        x1, y1, x2, y2 = det["box"]
        print(
            f"[{i}] {det['label']} score={det['score']:.3f} "
            f"bbox=({x1},{y1})-({x2},{y2}) weight={det['weight']}"
        )

    if args.salida:
        salida = Path(args.salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(salida), imagen_debug)
        print(f"Imagen de salida guardada en: {salida}")

    if not args.sin_ventana:
        cv2.imshow("Template Matching - Resultado", imagen_debug)
        if args.mostrar_crudas and not args.sin_agrupado:
            imagen_cruda = imagen.copy()
            for det in detecciones_crudas:
                x1, y1, x2, y2 = det["box"]
                cv2.rectangle(imagen_cruda, (x1, y1), (x2, y2), (0, 180, 255), 1)
            cv2.imshow("Template Matching - Crudas (sin agrupar)", imagen_cruda)
        if args.thresh != "ninguno":
            cv2.imshow(f"Threshold ({args.thresh})", imagen_proc)
        for nombre, mascara in mascaras_hsv.items():
            cv2.imshow(f"HSV {nombre}", mascara)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
