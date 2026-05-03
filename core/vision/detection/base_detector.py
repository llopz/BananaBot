import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import List, Tuple, Optional


ESPACIOS_COLOR = {
    "HSV":   cv2.COLOR_BGR2HSV,
    "YUV":   cv2.COLOR_BGR2YUV,
    "LAB":   cv2.COLOR_BGR2LAB,
    "HLS":   cv2.COLOR_BGR2HLS,
    "YCrCb": cv2.COLOR_BGR2YCrCb,
    "LUV":   cv2.COLOR_BGR2LUV,
    "XYZ":   cv2.COLOR_BGR2XYZ,
}


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


class BaseDetector:
    _frame_cache_lock = Lock()
    _frame_cache_id = None
    _frame_cache_convertida = {}

    def __init__(self, config):
        self.config = config
        self._templates = {}

    def _cargar_template(self, nombre_archivo, escala=1.0, gris=False):
        cache_key = (nombre_archivo, float(escala), bool(gris))
        if cache_key in self._templates:
            return self._templates[cache_key]

        plantillas_dir = Path(__file__).resolve().parent / "plantillas"
        path = plantillas_dir / nombre_archivo
        flag = cv2.IMREAD_GRAYSCALE if gris else cv2.IMREAD_COLOR
        template = cv2.imread(str(path), flag)
        if template is None:
            raise FileNotFoundError(f"No se pudo cargar template: {path}")

        if abs(float(escala) - 1.0) > 1e-9:
            nuevo_w = max(1, int(round(template.shape[1] * float(escala))))
            nuevo_h = max(1, int(round(template.shape[0] * float(escala))))
            template = cv2.resize(template, (nuevo_w, nuevo_h), interpolation=cv2.INTER_LINEAR)

        self._templates[cache_key] = template
        return template

    def _detectar_por_template(
        self,
        frame,
        template_nombre,
        tipo,
        threshold=0.7,
        escala_template=1.0,
        metodo=cv2.TM_CCOEFF_NORMED,
        zona_x_inicio=0,
        zona_x_fin=None,
        zona_y_inicio=0,
        zona_y_fin=None,
        extension_izquierda=0,
    ):
        alto, ancho = frame.shape[:2]
        if zona_x_fin is None:
            zona_x_fin = ancho
        if zona_y_fin is None:
            zona_y_fin = alto

        x_min_global = int(getattr(self.config, "DETECCION_X_MIN", 0))
        tipos_sin_filtro_x = {"kong", "barra_potenciadora", "barras_potenciadoras"}
        if tipo not in tipos_sin_filtro_x and zona_x_inicio < x_min_global:
            zona_x_inicio = x_min_global

        zona_x_inicio = max(0, int(zona_x_inicio))
        zona_x_fin = min(ancho, int(zona_x_fin))
        zona_y_inicio = max(0, int(zona_y_inicio))
        zona_y_fin = min(alto, int(zona_y_fin))

        frame_roi = frame[zona_y_inicio:zona_y_fin, zona_x_inicio:zona_x_fin]
        frame_gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
        template = self._cargar_template(template_nombre, escala=escala_template, gris=True)
        th, tw = template.shape[:2]
        if th > frame_gray.shape[0] or tw > frame_gray.shape[1]:
            mascara = np.zeros((alto, ancho), dtype=np.uint8)
            return [], [(0, 0, 0, 0, f"{tipo} template fuera de rango")], mascara

        score_map = cv2.matchTemplate(frame_gray, template, metodo)
        if metodo in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
            locations = np.where(score_map <= threshold)
            score_at = lambda y, x: 1.0 - float(score_map[y, x])
        else:
            locations = np.where(score_map >= threshold)
            score_at = lambda y, x: float(score_map[y, x])
        locations = list(zip(*locations[::-1]))

        rects = []
        for x, y in locations:
            rect = [int(x + zona_x_inicio), int(y + zona_y_inicio), int(tw), int(th)]
            rects.append(rect)
            rects.append(rect)

        grouped, weights = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)
        elementos = []
        mascara = np.zeros((alto, ancho), dtype=np.uint8)
        descartados = []

        for idx, rect in enumerate(grouped):
            x, y, w, h = [int(v) for v in rect]
            if extension_izquierda > 0:
                nuevo_x = max(0, x - int(extension_izquierda))
                w = min(ancho - nuevo_x, w + (x - nuevo_x))
                x = nuevo_x
            centro_x = x + w // 2
            centro_y = y + h // 2
            elementos.append(Elemento(
                x=x,
                y=y,
                w=w,
                h=h,
                centro_x=centro_x,
                centro_y=centro_y,
                area=float(w * h),
                proporcion=round(w / h, 2) if h > 0 else 0.0,
                tipo=tipo,
            ))
            cv2.rectangle(mascara, (x, y), (x + w, y + h), 255, -1)

        if not elementos and locations:
            for x, y in locations:
                descartados.append((int(x), int(y + zona_y_inicio), int(tw), int(th), f"{tipo} match sin agrupar"))
        elif not elementos:
            descartados.append((0, 0, 0, 0, f"{tipo} sin coincidencias template"))

        return elementos, descartados, mascara

    def _crear_mascara(
        self,
        frame,
        rango_bajo,
        rango_alto,
        espacio="HSV",
        erode_kernel=(3, 3),
        erode_iter=1,
        dilate_kernel=(3, 3),
        dilate_iter=1,
    ):
        codigo = ESPACIOS_COLOR.get(espacio, cv2.COLOR_BGR2HSV)

        frame_id = id(frame)
        with BaseDetector._frame_cache_lock:
            if BaseDetector._frame_cache_id != frame_id:
                BaseDetector._frame_cache_id = frame_id
                BaseDetector._frame_cache_convertida = {}
            convertida = BaseDetector._frame_cache_convertida.get(codigo)

        if convertida is None:
            nueva_convertida = cv2.cvtColor(frame, codigo)
            with BaseDetector._frame_cache_lock:
                convertida = BaseDetector._frame_cache_convertida.get(codigo)
                if convertida is None:
                    BaseDetector._frame_cache_convertida[codigo] = nueva_convertida
                    convertida = nueva_convertida

        mascara = cv2.inRange(convertida, np.array(rango_bajo), np.array(rango_alto))

        erode_kernel = tuple(int(v) for v in erode_kernel)
        dilate_kernel = tuple(int(v) for v in dilate_kernel)
        erode_iter = int(erode_iter)
        dilate_iter = int(dilate_iter)

        if erode_iter > 0 and dilate_iter > 0 and erode_kernel == dilate_kernel and erode_iter == dilate_iter:
            kernel = np.ones(erode_kernel, np.uint8)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel, iterations=erode_iter)
        else:
            if erode_iter > 0:
                kernel_erode = np.ones(erode_kernel, np.uint8)
                mascara = cv2.erode(mascara, kernel_erode, iterations=erode_iter)
            if dilate_iter > 0:
                kernel_dilate = np.ones(dilate_kernel, np.uint8)
                mascara = cv2.dilate(mascara, kernel_dilate, iterations=dilate_iter)

        return mascara, convertida

    def _detectar_elemento(self, frame, rango_bajo, rango_alto,
                        area_min_pct, area_max_pct,
                        prop_min, prop_max, tipo,
                        zona_y_inicio=0, zona_y_fin=None,
                        espacio="HSV",
                        erode_kernel=(3, 3), erode_iter=1,
                        dilate_kernel=(3, 3), dilate_iter=1):

        alto, ancho = frame.shape[:2]
        area_total = alto * ancho
        area_min = area_total * area_min_pct
        area_max = area_total * area_max_pct
        if zona_y_fin is None:
            zona_y_fin = alto

        mascara, _ = self._crear_mascara(
            frame, rango_bajo, rango_alto, espacio,
            erode_kernel=erode_kernel, erode_iter=erode_iter,
            dilate_kernel=dilate_kernel, dilate_iter=dilate_iter,
        )

        # connectedComponentsWithStats devuelve directamente
        # x, y, w, h y área de cada blob sin calcular polígonos
        num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(
            mascara, connectivity=8
        )

        elementos   = []
        descartados = []

        # label 0 es el fondo, se empieza desde 1
        for i in range(1, num_labels):
            x    = int(stats[i, cv2.CC_STAT_LEFT])
            y    = int(stats[i, cv2.CC_STAT_TOP])
            w    = int(stats[i, cv2.CC_STAT_WIDTH])
            h    = int(stats[i, cv2.CC_STAT_HEIGHT])
            area = float(stats[i, cv2.CC_STAT_AREA])
            centro_x = int(centroids[i, 0])
            centro_y = int(centroids[i, 1])
            proporcion = w / h if h > 0 else 0

            if area < area_min:
                descartados.append((x, y, w, h, f"{tipo} area pequeña"))
                continue
            if area > area_max:
                descartados.append((x, y, w, h, f"{tipo} area grande"))
                continue
            if proporcion < prop_min or proporcion > prop_max:
                descartados.append((x, y, w, h, f"{tipo} proporción rara"))
                continue
            if centro_y < zona_y_inicio or centro_y > zona_y_fin:
                descartados.append((x, y, w, h, f"{tipo} fuera de zona Y"))
                continue

            elementos.append(Elemento(
                x=x, y=y, w=w, h=h,
                centro_x=centro_x, centro_y=centro_y,
                area=area,
                proporcion=round(proporcion, 2),
                tipo=tipo
            ))

        return elementos, descartados, mascara