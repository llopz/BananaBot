import cv2
import keyboard
import time
import config.settings as settings
from vision.captura import Capturador
from vision.detector import Detector
from vision.visualizador import Visualizador

from control.acciones_click import ModuloAcciones, SALTAR, PLANEAR, BAJAR, DASH
from rules.rule_engine import RuleEngine
from rules.rules import rules
from rules.game_state import GameState


def main():

    print("=" * 55)
    print("  BANANA KONG BOT")
    print("=" * 55)
    print("  P = pausar / reanudar")
    print("  Q = salir")
    print("  Acciones automáticas en 15 segundos...")
    print()

    capturador = Capturador(
        titulo_ventana=settings.EMULADOR_TITULO,
        refrescar_cada=settings.EMULADOR_REFRESCAR_CADA,
    )

    detector = Detector(settings)
    visualizador = Visualizador(settings)

    acciones = ModuloAcciones()
    engine = RuleEngine(rules)

    pausado = False
    bot_activo = False
    frame_congelado = None
    centro_calibrado = False

    tiempo_inicio = time.time()
    ultimo_aviso = -1

    bananas_relevantes = []
    banana_objetivo = None
    banana_objetivo_distance = None
    objects_relevantes = []
    nearest_object = None
    nearest_object_distance = None

    resultados = {
        "bananas": [],
        "troncos": [],
        "arbustos": [],
        "aviones": [],
        "kong": [],
        "descartados": [],
        "mascaras": {},
    }

    with capturador:
        while True:

            # 1. ACTIVAR BOT después de 5 segundos
            if not bot_activo:
                transcurrido = time.time() - tiempo_inicio
                restantes = int(5 - transcurrido)
                if transcurrido >= 5:
                    bot_activo = True
                    print("[BOT] ACTIVADO - ejecutando acciones automáticamente")
                elif restantes != ultimo_aviso:
                    print(f"[BOT] Iniciando en {restantes}s...")
                    ultimo_aviso = restantes

            # 2. CAPTURAR
            frame_actual, frame_congelado = capturador.capturar_y_congelar(
                frame_congelado, pausado
            )

            # 3. DETECTAR
            if not pausado:
                resultados = detector.detectar_todos(frame_actual)

            bananas = resultados.get("bananas", [])
            troncos = resultados.get("troncos", [])
            arbustos = resultados.get("arbustos", [])
            aviones = resultados.get("aviones", [])
            kong = resultados.get("kong", [])
            descartados = resultados.get("descartados", [])
            mascaras = resultados.get("mascaras", {})

            """if settings.DEBUG and not pausado:
                total = (
                    len(bananas)
                    + len(troncos)
                    + len(arbustos)
                    + len(aviones)
                    + len(kong)
                )
                if total > 0:
                    print(
                        f"[VISION] bananas={len(bananas)} troncos={len(troncos)} arbustos={len(arbustos)} aviones={len(aviones)} kong={len(kong)}"
                    )"""

            # CREAR ESTADO DE JUEGO
            bananas_relevantes = []
            banana_objetivo = None
            banana_objetivo_distance = None
            objects_relevantes = []
            nearest_object = None
            nearest_object_distance = None

            
            if kong:

                kong_x = kong[0].centro_x
                Kong_y = kong[0].centro_y

                if bananas:

                    for banana in bananas:

                        dx = banana.centro_x - kong_x

                        if 0 < dx < 200:
                            bananas_relevantes.append(banana)

                if bananas_relevantes:
                    banana_objetivo = min(bananas_relevantes, key=lambda b: b.centro_x)
                    banana_objetivo_distance = [
                        banana_objetivo.centro_x - kong_x,
                        banana_objetivo.centro_y - Kong_y,
                    ]

                if objects := troncos + arbustos + aviones:
                    
                    objects_relevantes = [
                        obj
                        for obj in objects
                        if 0 < obj.centro_x - kong[0].centro_x < 200
                    ]

                if objects_relevantes:
                    nearest_object = min(objects_relevantes, key=lambda o: o.centro_x)
                    nearest_object_distance = [
                        nearest_object.centro_x - kong[0].centro_x,
                        nearest_object.centro_y - kong[0].centro_y,
                    ]
            
            print(f"nearest_object_distance: {nearest_object_distance}, banana_objetivo_distance: {banana_objetivo_distance}")

            estado_juego = GameState(
                obstacle_ahead=nearest_object is not None,
                obstacle_distance=nearest_object_distance if nearest_object else None,
                banana=banana_objetivo is not None,
                banana_distance=banana_objetivo_distance if banana_objetivo else None,
            )

            # 4. DECIDIR ACCION

            if bot_activo and not pausado:

                accion = engine.decide(estado_juego)

                acciones.ejecutar(accion)

            # 5. VISUALIZAR
            frame_debug = visualizador.dibujar_todo(
                frame_actual,
                {
                    "bananas": bananas,
                    "troncos": troncos,
                    "arbustos": arbustos,
                    "aviones": aviones,
                    "kong": kong,
                },
                bot_activo=bot_activo,
                pausado=pausado,
                descartados=descartados,
            )

            cv2.imshow("Banana Kong Bot", frame_debug)

            for nombre, mascara in mascaras.items():
                visualizador.mostrar_mascara(nombre, mascara)

            # 6. TECLAS
            if keyboard.is_pressed("q"):
                acciones.parar()
                break
            if keyboard.is_pressed("p"):
                pausado = not pausado
                print(f"[CONTROL] {'PAUSADO' if pausado else 'REANUDADO'}")
                time.sleep(0.2)

            cv2.waitKey(1)

    cv2.destroyAllWindows()
    print("Bot terminado.")


if __name__ == "__main__":
    main()
