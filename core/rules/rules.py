from rules.rule_engine import Rule
from control.acciones_click import NADA, SALTAR, PLANEAR, BAJAR, DASH

# Definicion de reglas
obst_dist = {"tronco": (150, 50), "arbusto": (150, 50), "avion": (200, 50), "pared": (150, 50), "roca": (150, 50)}


def obstacle_rule(state):

    if state.obstacle is not None and state.obstacle_distance is not None:
        print(f"Evaluando regla de obstáculo: tipo={state.obstacle.tipo}")
        return (
            state.obstacle_distance[0] < obst_dist[state.obstacle.tipo][0]
            and state.obstacle_distance[1] < obst_dist[state.obstacle.tipo][1]
            and state.obstacle_distance[1] > -obst_dist[state.obstacle.tipo][1]
        )


def banana_rule_up(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] < -10:
            return True


def banana_rule_down(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] > 50:
            return True

# no implementadas

'''
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
        
'''

# Lista de reglas

rules = [
    Rule(name="saltar_obstaculo", condition=obstacle_rule, action=SALTAR, priority=1),
    Rule(name="recolectar_banana", condition=banana_rule_up, action=SALTAR, priority=2),
    Rule(
        name="recolectar_banana_abajo",
        condition=banana_rule_down,
        action=BAJAR,
        priority=3,
    ),
]
