import argparse
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from rules.game_state import GameState
from rules.rule_engine import RuleEngine
from rules.rules import rules
from rules.world_generator import SyntheticWorldGenerator


FPS_ASUMIDO = 60.0
CRITICAL_OBJECT_KEYS = ["cuevas", "rocas", "aguas", "paredes", "totems", "troncos", "aviones"]

# Colores para visualización (BGR)
COLORES = {
    "kong": (50, 120, 200),
    "banana": (0, 255, 255),
    "tronco": (100, 50, 0),
    "arbusto": (0, 150, 0),
    "avion": (200, 100, 0),
    "pared": (100, 100, 100),
    "plataforma_madera": (139, 69, 19),
    "roca": (180, 180, 180),
    "cueva": (50, 50, 50),
    "totem": (200, 50, 50),
    "tubo": (100, 100, 200),
    "agua": (255, 0, 0),
}


def _dibujar_frame(frame_dict: dict, step: int, width: int = 960, height: int = 540) -> np.ndarray:
    """Dibuja los objetos del frame en una imagen."""
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 200

    # Dibujar carril superior (tierra)
    cv2.line(canvas, (0, 520), (width, 520), (100, 200, 100), 3)

    # Dibujar obstáculos y objetos
    for key in ["troncos", "arbustos", "aviones", "paredes", "rocas", "cuevas", "totems", "tubos", "aguas", "plataformas_madera"]:
        for obj in frame_dict.get(key, []):
            color = COLORES.get(obj.tipo, (128, 128, 128))
            x1 = max(0, int(obj.x))
            y1 = max(0, int(obj.y))
            x2 = min(width, int(obj.x + obj.w))
            y2 = min(height, int(obj.y + obj.h))
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                canvas, obj.tipo[:3], (x1 + 2, y1 + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1
            )

    # Dibujar bananas
    for obj in frame_dict.get("bananas", []):
        cv2.circle(canvas, (int(obj.centro_x), int(obj.centro_y)), 8, COLORES["banana"], -1)

    # Dibujar Kong
    for obj in frame_dict.get("kong", []):
        x1 = max(0, int(obj.x))
        y1 = max(0, int(obj.y))
        x2 = min(width, int(obj.x + obj.w))
        y2 = min(height, int(obj.y + obj.h))
        cv2.rectangle(canvas, (x1, y1), (x2, y2), COLORES["kong"], 3)
        cv2.putText(canvas, "KONG", (x1 + 2, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORES["kong"], 2)

    # Info del frame
    cv2.putText(canvas, f"Step {step}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return canvas


def _actualizar_estado(estado: GameState, frame: dict) -> None:
    estado.actualizar(
        frame.get("kong", []),
        frame.get("bananas", []),
        frame.get("troncos", []),
        frame.get("arbustos", []),
        frame.get("aviones", []),
        frame.get("paredes", []),
        frame.get("plataformas_madera", []),
        frame.get("rocas", []),
        frame.get("aguas", []),
        frame.get("cuevas", []),
        frame.get("totems", []),
        frame.get("tubos", []),
    )


def _resumen_estado(estado: GameState) -> str:
    carril = estado.carril_actual
    obst = estado.carriles[carril]["obstaculo_cercano"]
    banana = estado.carriles[carril]["banana_cercana"]
    suelo = estado.carriles[carril]["suelo"]

    obst_str = "none"
    if obst:
        obj, dx, dy = obst
        obst_str = f"{obj.tipo}(dx={int(dx)},dy={int(dy)})"

    banana_str = "none"
    if banana:
        _, dx, dy = banana
        banana_str = f"(dx={int(dx)},dy={int(dy)})"

    return f"carril={carril} suelo={suelo} obst={obst_str} banana={banana_str}"


def _hay_colision_critica(frame: dict) -> tuple[bool, str | None]:
    kong_list = frame.get("kong", [])
    if not kong_list:
        return False, None

    kong = kong_list[0]

    for key in CRITICAL_OBJECT_KEYS:
        for obj in frame.get(key, []):
            # Dos cajas se cruzan si la distancia de centros en cada eje
            # es menor o igual a la suma de sus semianchos/semialtos.
            dx = abs(kong.centro_x - obj.centro_x)
            dy = abs(kong.centro_y - obj.centro_y)
            limite_x = (kong.w + obj.w) / 2.0
            limite_y = (kong.h + obj.h) / 2.0
            if dx <= limite_x and dy <= limite_y:
                return True, getattr(obj, "tipo", key)

    return False, None


def run_simulation(steps: int, seed: int | None = None, verbose: bool = False, output_dir: str | None = None, visualizar: bool = False) -> dict:
    generador = SyntheticWorldGenerator(seed=seed)
    estado = GameState()
    engine = RuleEngine(rules)

    # Crear carpeta de salida si se solicita
    out_path = None
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        print(f"[VIZ] Guardando frames en: {out_path}")

    acciones = defaultdict(int)
    collision_step = None
    collision_object = None
    frames_generados = []

    for i in range(1, steps + 1):
        frame = generador.generate_frame()
        _actualizar_estado(estado, frame)

        canvas = _dibujar_frame(frame, i)
        frames_generados.append((i, canvas, frame, estado))

        # Dibujar frame si se solicita
        if out_path:
            cv2.imwrite(str(out_path / f"frame_{i:04d}.png"), canvas)

        colision, tipo_colision = _hay_colision_critica(frame)
        if colision:
            collision_step = i
            collision_object = tipo_colision
            if verbose:
                print(f"[STEP {i:03d}] COLISION CRITICA con {tipo_colision}. Fin de simulacion.")
            break

        accion = engine.decide(estado)
        acciones[accion] += 1

        if verbose:
            print(f"[STEP {i:03d}] {_resumen_estado(estado)} -> accion={accion}")

    # Visualizar en ventana interactiva si se solicita
    if visualizar and frames_generados:
        _mostrar_ventana_interactiva(frames_generados)

    acciones_normalizadas = {str(accion): cantidad for accion, cantidad in acciones.items()}

    return {
        "steps": collision_step if collision_step is not None else steps,
        "seed": seed,
        "tiempo_segundos": (collision_step if collision_step is not None else steps) / FPS_ASUMIDO,
        "acciones": dict(sorted(acciones_normalizadas.items(), key=lambda x: x[0])),
        "terminated_by_collision": collision_step is not None,
        "collision_step": collision_step,
        "collision_object": collision_object,
    }


def _mostrar_ventana_interactiva(frames_generados: list) -> None:
    """Muestra los frames generados en una ventana interactiva."""
    if not frames_generados:
        print("[VIZ] No hay frames para visualizar")
        return
    
    print(f"[VIZ] Cargados {len(frames_generados)} frames")
    print("[VIZ] Presiona: SPACE=play/pausa | DERECHA=siguiente | IZQUIERDA=anterior | q=salir")
    
    idx_actual = 0
    pausado = True
    ventana_nombre = "Simulacion Banana Kong"
    
    try:
        cv2.namedWindow(ventana_nombre, cv2.WINDOW_AUTOSIZE)
        print("[VIZ] Ventana creada")
    except Exception as e:
        print(f"[ERROR] No se pudo crear ventana: {e}")
        return
    
    while True:
        step, canvas, frame, estado = frames_generados[idx_actual]
        
        # Dibujar información adicional
        canvas_copy = canvas.copy()
        cv2.putText(
            canvas_copy,
            f"Frame {idx_actual + 1}/{len(frames_generados)} {'(PAUSADO)' if pausado else '(REPRODUCIENDO)'}",
            (10, 540 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
        )
        
        try:
            cv2.imshow(ventana_nombre, canvas_copy)
        except Exception as e:
            print(f"[ERROR] No se pudo mostrar frame: {e}")
            break
        
        # Esperar 1/FPS_ASUMIDO o esperar tecla si está pausado
        delay = 1 if pausado else int(1000 / FPS_ASUMIDO)
        key = cv2.waitKey(delay) & 0xFF
        
        if key == ord('q'):
            print("[VIZ] Saliendo...")
            break
        elif key == ord(' '):
            pausado = not pausado
            print(f"[VIZ] {'Reproduciendo' if not pausado else 'Pausado'}")
        elif key == 83 or key == ord('d'):  # Flecha derecha o 'd'
            if idx_actual < len(frames_generados) - 1:
                idx_actual += 1
                pausado = True
        elif key == 81 or key == ord('a'):  # Flecha izquierda o 'a'
            if idx_actual > 0:
                idx_actual -= 1
                pausado = True
        elif not pausado:
            if idx_actual < len(frames_generados) - 1:
                idx_actual += 1
            else:
                pausado = True  # Al llegar al final, pausar
    
    try:
        cv2.destroyAllWindows()
    except:
        pass
    print("[VIZ] Ventana cerrada")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera un mundo sintético y prueba el motor de reglas con posiciones relativas."
    )
    parser.add_argument("--steps", type=int, default=120, help="Cantidad de frames simulados")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para escenarios reproducibles")
    parser.add_argument("--verbose", action="store_true", help="Muestra el detalle por frame")
    parser.add_argument("--output-dir", type=str, default=None, help="Carpeta para guardar frames visuales (PNG)")
    parser.add_argument("--visualizar", action="store_true", help="Muestra los frames en ventana interactiva")
    args = parser.parse_args()

    resultado = run_simulation(
        steps=max(1, args.steps),
        seed=args.seed,
        verbose=args.verbose,
        output_dir=args.output_dir,
        visualizar=args.visualizar
    )

    print("=" * 54)
    print("SIMULACION DE REGLAS - BANANA KONG")
    print("=" * 54)
    print(f"Frames simulados: {resultado['steps']}")
    print(f"Tiempo vivo: {resultado['tiempo_segundos']:.2f} segundos ({resultado['steps']} frames @ {FPS_ASUMIDO} FPS)")
    print(f"Semilla: {resultado['seed']}")
    if resultado["terminated_by_collision"]:
        print(
            "Fin: colision critica en "
            f"frame {resultado['collision_step']} con {resultado['collision_object']}"
        )
    else:
        print("Fin: sin colision critica")
    print("Acciones ejecutadas:")
    for accion, cantidad in resultado["acciones"].items():
        print(f"  - {accion}: {cantidad}")


if __name__ == "__main__":
    main()