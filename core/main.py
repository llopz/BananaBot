import cv2
import keyboard
import time
import config.settings as settings
from vision.captura import Capturador
from vision.detection.detector import Detector
from vision.visualizador import Visualizador

from control.acciones_click import ModuloAcciones, SALTAR, PLANEAR, BAJAR, DASH
from rules.rule_engine import RuleEngine
from rules.rules import rules
from rules.game_state import GameState


def main():

    print("=" * 55)
    print("  BANANA KONG BOT")
    print("=" * 55)
    print("  SPACE = iniciar detección")
    print("  P     = pausar / reanudar")
    print("  Q     = salir")
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
    deteccion_activa = False       # ← nueva bandera
    frame_congelado = None

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
        "aguas":        [],
        "descartados":  [],
        "mascaras":     {},
    }

    with capturador:
        while True:

            # 1. CAPTURAR (siempre, para mostrar video)
            frame_actual, frame_congelado = capturador.capturar_y_congelar(
                frame_congelado, pausado
            )

            # 2. DETECTAR (solo si la detección está activa y no pausado)
            if deteccion_activa and not pausado:
                resultados = detector.detectar_todos(frame_actual)

            bananas      = resultados.get("bananas",     [])
            troncos      = resultados.get("troncos",     [])
            arbustos     = resultados.get("arbustos",    [])
            aviones      = resultados.get("aviones",     [])
            kong         = resultados.get("kong",        [])
            paredes      = resultados.get("paredes",     [])
            plataformas  = resultados.get("plataformas", [])
            rocas        = resultados.get("rocas",       [])
            aguas        = resultados.get("aguas",       [])
            descartados  = resultados.get("descartados", [])
            mascaras     = resultados.get("mascaras",    {})

            # 3. ACTUALIZAR ESTADO DEL JUEGO
            estado_juego.actualizar(kong, bananas, troncos, arbustos, aviones, plataformas, paredes, rocas, aguas)

            # 4. DECIDIR ACCIÓN
            if bot_activo and deteccion_activa and not pausado:
                accion = engine.decide(estado_juego)
                acciones.ejecutar(accion)

            # 5. VISUALIZAR
            frame_debug = visualizador.dibujar_todo(
                frame_actual,
                {k: v for k, v in resultados.items() if k not in ("descartados", "mascaras")},
                bot_activo=deteccion_activa,
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