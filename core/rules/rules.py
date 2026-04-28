from rules.rule_engine import Rule
from control.acciones_click import NADA, SALTAR, PLANEAR, BAJAR, DASH

# Definicion de reglas
obst_dist = {
    "tronco": (170, 40),
    "arbusto": (160, 50),
    "avion": (200, 50),
    "pared": (180, 50),
    "roca": (260, 50),
    "cueva": (280, 50),
    "totem": (190, 50),
    "tubo": (200, 50),
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

def banana_rule_up(state):
    carril = state.carril_actual

    if carril < 4:
        data = state.carriles[carril + 1]["banana_cercana"]
        suelo = state.carriles[carril + 1]["suelo"]

        if data:
            banana, dx, dy = data

            return dx < 150 
    elif carril == 4:
        data = state.carriles[carril]["banana_cercana"]
        suelo = state.carriles[carril]["suelo"]

        if data:
            banana, dx, dy = data

            if dx < 150:
                return True

def banana_rule_2(state):
    carril = state.carril_actual
    data = state.carriles[carril]["banana_cercana"]
    suelo = state.carriles[carril]["suelo"]

    if data and not suelo:
        banana, dx, dy = data

        if dx < 50 and 10< dy < 10:
            return True
            
def plataforma (state):
    
    carril = state.carril_actual
    if carril < 4:
        suelo_arriba = state.carriles[carril + 1]["suelo"]

    if suelo_arriba:
        return True
    
def gap_rule(state):
    carril = state.carril_actual
    if carril == 0:
        suelo_actual = state.carriles[carril]["suelo"]

        if not suelo_actual:
                return True
    
def dangerous_falling(state):
    
    carril = state.carril_actual
    suelo_actual = state.carriles[carril]["suelo"]
    
    if carril > 0:
        suelo_abajo = state.carriles[carril - 1]["suelo"]
        obstaculo = state.carriles[carril - 1]["obstaculo_cercano"]
    else:
        suelo_abajo = False
    
    if not suelo_actual and (not suelo_abajo or obstaculo ):
            return True

    
'''

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
    Rule(name="saltar_obstaculo", condition=obstacle_rule, action=SALTAR, priority=0),
    #Rule(name="saltar_vacio", condition=gap_rule, action=SALTAR, priority=1),
    Rule(name="caida_peligrosa", condition=dangerous_falling, action=PLANEAR, priority=2),
    Rule(name="recolectar_banana", condition=banana_rule_up, action=SALTAR, priority=3),
    #Rule(name="recolectar_banana_planear", condition=banana_rule_2, action=PLANEAR, priority=5),
    #Rule(name="plataforma", condition=plataforma, action=SALTAR, priority=5),
]
