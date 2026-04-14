from rules.rule_engine import Rule
from control.acciones_click import NADA, SALTAR, PLANEAR, BAJAR, DASH

# Definicion de reglas
obst_dist = {
    "tronco": (170, 50),
    "arbusto": (160, 50),
    "avion": (200, 50),
    "pared": (160, 50),
    "roca": (260, 50),
    "cueva": (280, 50),
    "totem": (160, 50),
    "tubo": (280, 50),
}


def obstacle_rule(state):
    carril = state.carril_actual
    obst_data = state.carriles[carril]["obstaculo_cercano"]

    if obst_data:
        obstaculo, dx, dy = obst_data
        limites = obst_dist.get(obstaculo.tipo)

        if limites is None:
            print(f"[REGLAS] Obstáculo sin configuración: {obstaculo.tipo}")
            return False

        print(f"Obstáculo en carril {carril}: {obstaculo.tipo}")
        print(f"Distancia al obstáculo: dx={dx}, dy={dy}")

        return (
            dx < limites[0]
            and dy < limites[1]
            and dy > -limites[1]
        )

'''
def banana_rule_up(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] < -10:
            return True

def banana_rule_up(state):
    carril = state.carril_actual

    if carril < 4:
        data = state.carriles[carril + 1]["banana_cercana"]
        suelo = state.carriles[carril + 1]["suelo"]

        if data and suelo:
            banana, dx, dy = data

            if dx < 150:
                return True


def banana_rule_down(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] > 50:
            return True

def banana_rule_down(state):
    carril = state.carril_actual

    if carril > 0:
        data = state.carriles[carril - 1]["banana_cercana"]
        suelo = state.carriles[carril - 1]["suelo"]

        if data and suelo:
            banana, dx, dy = data

            if dx < 150:
                return True

# no implementadas


def banana_up_plataform_rule(state): # SALTAR
    if (
        state.banana
        and state.platform is not None
        and state.banana_distance is not None
        and state.platform_distance is not None
    ):
        if state.banana_distance[0] > 150 and state.banana_distance[1] < -10 and state.platform_distance[0] < 120:
            return True

def banana_down_plataform_rule(state): # SALTAR
    if (
        state.banana
        and state.platform is not None
        and state.banana_distance is not None
        and state.platform_distance is not None
    ):
        if state.banana_distance[0] > 150 and state.banana_distance[1] > 50 and state.platform_distance[0] < 120:
            return True
        
def falling_without_platform_rule(state): # PLANEAR
    if state.platform is not None and state.platform_distance is not None:
        if state.platform_distance[0] > 150:
            return True

def falling_without_platform_rule(state):
    carril = state.carril_actual

    if carril > 0:
        suelo_actual = state.carriles[carril]["suelo"]

        if not suelo_actual:
            print("Sin suelo → PLANEAR")
            return True
        
        
def dash_obstacle_rule(state): # DASH
    if state.obstacle is not None and state.obstacle_distance is not None:
        if state.obstacle_distance[0] < 80:
            return True

def dash_obstacle_rule(state):
    carril = state.carril_actual
    data = state.carriles[carril]["obstaculo_cercano"]

    if data:
        obstaculo, dx, dy = data

        if dx < 80:
            print("DASH por peligro cercano")
            return True
        
'''

# Lista de reglas

rules = [
    Rule(name="saltar_obstaculo", condition=obstacle_rule, action=SALTAR, priority=1),
    #Rule(name="recolectar_banana", condition=banana_rule_up, action=SALTAR, priority=2),
]
