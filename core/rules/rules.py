from rules.rule_engine import Rule
from control.acciones_click import NADA, SALTAR, PLANEAR, BAJAR, DASH

# Definicion de reglas


def obstacle_rule(state):

    if state.obstacle_ahead and state.obstacle_distance is not None:
        return state.obstacle_distance[0] < 120 and state.obstacle_distance[1] < 50


def banana_rule_up(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] < -10:
            return True


def banana_rule_down(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] > 50:
            return True


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
