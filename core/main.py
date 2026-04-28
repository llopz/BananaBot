import cv2
import keyboard
import time
from collections import deque
import config.settings as settings
from vision.captura import Capturador
from vision.detection.detector import Detector
from vision.visualizador import Visualizador

from control.acciones_click import ModuloAcciones, SALTAR, PLANEAR, BAJAR, DASH
from rules.rule_engine import RuleEngine
from rules.rules import rules
from rules.game_state import GameState
from vision.detection.base_detector import Elemento


def main():

    def clonar_elementos(lista):
        return [
            Elemento(
                x=e.x,
                y=e.y,
                w=e.w,
                h=e.h,
                centro_x=e.centro_x,
                centro_y=e.centro_y,
                area=e.area,
                proporcion=e.proporcion,
                tipo=e.tipo,
            )
            for e in lista
        ]

    def calcular_velocidades_x(prev, curr, frames):
        if frames <= 0:
            return []
        prev_ord = sorted(prev, key=lambda e: e.centro_x)
        curr_ord = sorted(curr, key=lambda e: e.centro_x)
        velocidades = []
        for i, el in enumerate(curr_ord):
            if i < len(prev_ord):
                velocidades.append((el.centro_x - prev_ord[i].centro_x) / frames)
            else:
                velocidades.append(0.0)
        return velocidades

    def aplicar_prediccion_x(lista, velocidades, ancho, max_delta):
        ordenados = sorted(lista, key=lambda e: e.centro_x)
        for i, el in enumerate(ordenados):
            dx = velocidades[i] if i < len(velocidades) else 0.0
            if dx > max_delta:
                dx = max_delta
            elif dx < -max_delta:
                dx = -max_delta

            nuevo_x = int(round(el.x + dx))
            max_x = max(0, ancho - el.w)
            el.x = max(0, min(max_x, nuevo_x))
            el.centro_x = el.x + el.w // 2

    print("=" * 55)
    print("  BANANA KONG BOT")
    print("=" * 55)
    print("  SPACE = iniciar detección")
    print("  P     = pausar / reanudar")
    print("  Q     = salir")
    if not settings.EJECUTAR_ACCIONES:
        print("  MODO SEGURO: acciones automáticas desactivadas")
    print()

    capturador = Capturador(
        titulo_ventana=settings.EMULADOR_TITULO,
        refrescar_cada=settings.EMULADOR_REFRESCAR_CADA,
    )

    detector     = Detector(settings)
    visualizador = Visualizador(settings)
    acciones     = ModuloAcciones()
    engine       = RuleEngine(rules)

    pausado         = False
    bot_activo      = False
    deteccion_activa = False      
    frame_congelado = None
    ultimo_debug_log = 0.0
    debug_interval_seg = 0.5

    # ── Métricas ──────────────────────────────────────────────
    VENTANA_METRICAS = 60          # muestras para calcular promedios
    ts_frames        = deque(maxlen=VENTANA_METRICAS)   # timestamps de cada frame
    tiempos_captura  = deque(maxlen=VENTANA_METRICAS)
    tiempos_detec    = deque(maxlen=VENTANA_METRICAS)
    tiempos_estado   = deque(maxlen=VENTANA_METRICAS)
    tiempos_accion   = deque(maxlen=VENTANA_METRICAS)
    tiempos_ciclo    = deque(maxlen=VENTANA_METRICAS)   # tiempo total por iteración
    ultimo_ts_ciclo  = time.perf_counter()
    ultimo_metricas_log = 0.0
    metricas_interval_seg = 1.0
    contador_frames = 0

    tipos_prediccion_x = [
        "bananas", "troncos", "arbustos", "aviones",
        "paredes", "rocas", "cuevas", "totems", "tubos", "aguas",
    ]
    velocidades_x_por_tipo = {t: [] for t in tipos_prediccion_x}
    ultimo_resultado_real = {t: [] for t in tipos_prediccion_x}
    tipos_obstaculos = ["troncos", "arbustos", "aviones", "paredes", "rocas", "cuevas", "totems", "tubos"]

    estado_juego = GameState()

    resultados = {
        "bananas":      [],
        "troncos":      [],
        "arbustos":     [],
        "aviones":      [],
        "kong":         [],
        "paredes":      [],
        "plataformas":  [],
        "plataformas_madera": [],
        "rocas":        [],
        "cuevas":       [],
        "totems":       [],
        "tubos":        [],
        "aguas":        [],
        "descartados":  [],
        "mascaras":     {},
    }

    with capturador:
        while True:

            # ── Δt entre frames ───────────────────────────────
            ahora_frame = time.perf_counter()
            if ts_frames:
                tiempos_ciclo.append(ahora_frame - ultimo_ts_ciclo)
            ultimo_ts_ciclo = ahora_frame
            ts_frames.append(ahora_frame)

            # 1. CAPTURAR (siempre, para mostrar video)
            t0 = time.perf_counter()
            frame_actual, frame_congelado = capturador.capturar_y_congelar(
                frame_congelado, pausado
            )
            tiempos_captura.append(time.perf_counter() - t0)

            # 2. DETECTAR (solo si la detección está activa y no pausado)
            contador_frames += 1
            t0 = time.perf_counter()
            detectar_cada = max(1, int(getattr(settings, "DETECTAR_CADA_N_FRAMES", 1)))
            umbral_dx_forzar = float(getattr(settings, "DETECCION_FORZAR_DX_UMBRAL", 180))

            kong_ref = resultados.get("kong", [])
            obstaculo_cercano = False
            if kong_ref:
                kong_x_ref = kong_ref[0].centro_x
                for tipo_obs in tipos_obstaculos:
                    for obj in resultados.get(tipo_obs, []):
                        dx_ref = obj.centro_x - kong_x_ref
                        if 0 < dx_ref < umbral_dx_forzar:
                            obstaculo_cercano = True
                            break
                    if obstaculo_cercano:
                        break

            ejecutar_deteccion = (
                deteccion_activa
                and not pausado
                and ((contador_frames % detectar_cada == 0) or obstaculo_cercano)
            )

            if deteccion_activa and not pausado:
                if ejecutar_deteccion:
                    resultados = detector.detectar_todos(frame_actual)
                    for tipo in tipos_prediccion_x:
                        actuales = resultados.get(tipo, [])
                        previos = ultimo_resultado_real.get(tipo, [])
                        if previos and actuales:
                            velocidades_x_por_tipo[tipo] = calcular_velocidades_x(
                                previos, actuales, detectar_cada
                            )
                        else:
                            velocidades_x_por_tipo[tipo] = []
                        ultimo_resultado_real[tipo] = clonar_elementos(actuales)
                else:
                    ancho_frame = frame_actual.shape[1]
                    max_delta = float(getattr(settings, "PREDICCION_X_MAX"))
                    for tipo in tipos_prediccion_x:
                        aplicar_prediccion_x(
                            resultados.get(tipo, []),
                            velocidades_x_por_tipo.get(tipo, []),
                            ancho_frame,
                            max_delta,
                        )
            tiempos_detec.append(time.perf_counter() - t0)

            bananas      = resultados.get("bananas",     [])
            troncos      = resultados.get("troncos",     [])
            arbustos     = resultados.get("arbustos",    [])
            aviones      = resultados.get("aviones",     [])
            kong         = resultados.get("kong",        [])
            paredes      = resultados.get("paredes",     [])
            plataformas  = resultados.get("plataformas", [])
            rocas        = resultados.get("rocas",       [])
            cuevas       = resultados.get("cuevas",      [])
            totems       = resultados.get("totems",      [])
            tubos        = resultados.get("tubos",       [])
            aguas        = resultados.get("aguas",       [])
            descartados  = resultados.get("descartados", [])
            mascaras     = resultados.get("mascaras",    {})

            # 3. ACTUALIZAR ESTADO DEL JUEGO
            t0 = time.perf_counter()
            estado_juego.actualizar(kong, bananas, troncos, arbustos, aviones, paredes, plataformas, rocas, aguas, cuevas, totems, tubos)
            tiempos_estado.append(time.perf_counter() - t0)

            # 4. DECIDIR ACCIÓN
            t0 = time.perf_counter()
            if bot_activo and deteccion_activa and not pausado and settings.EJECUTAR_ACCIONES:
                accion = engine.decide(estado_juego)
                acciones.ejecutar(accion)
            tiempos_accion.append(time.perf_counter() - t0)

            # 5. VISUALIZAR
            frame_debug = visualizador.dibujar_todo(
                frame_actual,
                {k: v for k, v in resultados.items() if k not in ("descartados", "mascaras")},
                bot_activo=deteccion_activa,
                pausado=pausado,
                descartados=descartados,
            )

            cv2.imshow("Banana Kong Bot", frame_debug)

            #for nombre, mascara in mascaras.items():
            #  visualizador.mostrar_mascara(nombre, mascara)

            if deteccion_activa and settings.DEBUG:
                ahora = time.time()
                if ahora - ultimo_debug_log >= debug_interval_seg:
                    resumen = []
                    for tipo, lista in resultados.items():
                        if tipo in ("descartados", "mascaras"):
                            continue
                        cantidad = len(lista)
                        if cantidad > 0:
                            resumen.append(f"{tipo}={cantidad}")

                    if resumen:
                        print("[DEBUG] Detectados -> " + ", ".join(resumen))
                    else:
                        print("[DEBUG] Detectados -> ninguno")

                    ultimo_debug_log = ahora

            # ── Log de métricas ───────────────────────────────
            ahora = time.time()
            if ahora - ultimo_metricas_log >= metricas_interval_seg:
                if len(ts_frames) >= 2:
                    deltas = [ts_frames[i] - ts_frames[i-1] for i in range(1, len(ts_frames))]
                    fps      = 1.0 / (sum(deltas) / len(deltas)) if deltas else 0.0
                    fps_min  = 1.0 / max(deltas) if deltas else 0.0
                    fps_max  = 1.0 / min(deltas) if deltas else 0.0
                else:
                    fps = fps_min = fps_max = 0.0

                def ms(col): return f"{(sum(col)/len(col)*1000):.1f}" if col else "—"

                print(
                    f"[MÉTRICAS] "
                    f"FPS={fps:.1f} (min={fps_min:.1f} max={fps_max:.1f}) | "
                    f"captura={ms(tiempos_captura)}ms  "
                    f"detección={ms(tiempos_detec)}ms  "
                    f"estado={ms(tiempos_estado)}ms  "
                    f"acción={ms(tiempos_accion)}ms  "
                    f"ciclo={ms(tiempos_ciclo)}ms"
                )
                ultimo_metricas_log = ahora

            # 6. TECLAS
            if keyboard.is_pressed("q"):
                acciones.parar()
                break

            if keyboard.is_pressed("space"):
                deteccion_activa = not deteccion_activa
                bot_activo = deteccion_activa
                print(f"[BOT] Detección {'INICIADA' if deteccion_activa else 'DETENIDA'}")
                time.sleep(0.2)

            if keyboard.is_pressed("p") and deteccion_activa:
                pausado = not pausado
                print(f"[CONTROL] {'PAUSADO' if pausado else 'REANUDADO'}")
                time.sleep(0.2)

            cv2.waitKey(1)

    cv2.destroyAllWindows()
    print("Bot terminado.")


if __name__ == "__main__":
    main()