import cv2
import keyboard
import time
import config.settings as settings
from vision.captura      import Capturador
from vision.detector     import Detector
from vision.visualizador import Visualizador
from control.acciones    import ModuloAcciones, NADA, SALTAR, PLANEAR, BAJAR


def main():
    print("=" * 55)
    print("  BANANA KONG BOT")
    print("=" * 55)
    print("  P = pausar / reanudar")
    print("  Q = salir")
    print("  Acciones automáticas en 15 segundos...")
    print()

    capturador   = Capturador(
        titulo_ventana=settings.EMULADOR_TITULO,
        refrescar_cada=settings.EMULADOR_REFRESCAR_CADA
    )
    detector     = Detector(settings)
    visualizador = Visualizador(settings)
    acciones     = ModuloAcciones()

    pausado          = False
    bot_activo       = False
    frame_congelado  = None
    tiempo_inicio    = time.time()
    ultimo_aviso     = -1

    resultados = {
        "bananas": [], "troncos": [], "arbustos": [], "aviones": [],
        "kong": [], "descartados": [], "mascaras": {}
    }

    with capturador:
        while True:

            # 1. ACTIVAR BOT después de 5 segundos
            if not bot_activo:
                transcurrido = time.time() - tiempo_inicio
                restantes    = int(5 - transcurrido)
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

            bananas     = resultados.get("bananas",     [])
            troncos     = resultados.get("troncos",     [])
            arbustos    = resultados.get("arbustos",    [])
            aviones     = resultados.get("aviones",     [])
            kong        = resultados.get("kong",        [])
            descartados = resultados.get("descartados", [])
            mascaras    = resultados.get("mascaras",    {})

            if settings.DEBUG and not pausado:
                total = len(bananas) + len(troncos) + len(arbustos) + len(aviones) + len(kong)
                if total > 0:
                    print(f"[VISION] bananas={len(bananas)} troncos={len(troncos)} arbustos={len(arbustos)} aviones={len(aviones)} kong={len(kong)}")

            # 4. ACTUAR
           # if bot_activo and not pausado:
            #    acciones.ejecutar(SALTAR)

            # 5. VISUALIZAR
            frame_debug = visualizador.dibujar_todo(
                frame_actual,
                {"bananas": bananas, "troncos": troncos, "arbustos": arbustos,
                 "aviones": aviones, "kong": kong},
                bot_activo=bot_activo,
                pausado=pausado,
                descartados=descartados
            )

            cv2.imshow("Banana Kong Bot", frame_debug)

            for nombre, mascara in mascaras.items():
                visualizador.mostrar_mascara(nombre, mascara)

            # 6. TECLAS
            if keyboard.is_pressed('q'):
                acciones.parar()
                break
            if keyboard.is_pressed('p'):
                pausado = not pausado
                print(f"[CONTROL] {'PAUSADO' if pausado else 'REANUDADO'}")
                time.sleep(0.2)

            cv2.waitKey(1)

    cv2.destroyAllWindows()
    print("Bot terminado.")


if __name__ == "__main__":
    main()