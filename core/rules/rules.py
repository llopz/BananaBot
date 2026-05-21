from rules.rule_engine import Rule
from control.acciones_click import NADA, SALTAR, PLANEAR, BAJAR, DASH

# Definicion de reglas
obst_dist = {
    "tronco": (200, 40),
    "arbusto": (200, 50),
    "avion": (220, 50),
    "pared": (200, 50),
    "roca": (280, 40),
    "cueva": (280, 50),
    "totem": (200, 50),
    "tubo": (220, 50),
    "barril": (200, 50),
}

# Prueba

def prueba(state):
    return True

# Reglas de supervivencia

# Regla : SALTAR si hay un obstáculo cercano

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

# Regla: SALTAR si hay un vacío (falta de suelo) cercano

def gap_rule(state):
    carril = state.carril_actual
    if carril != 0:
        return False
    else:
        suelo_actual = state.carriles[carril]["suelo"]

        if not suelo_actual:
                return True
    
# Regla: PLANEAR si no hay suelo debajo y el carril es el 0 (evitar caer al vacío)

def dangerous_falling(state): 
    
    carril = state.carril_actual
    suelo_actual = state.carriles[carril]["suelo"]
    
    if carril > 0:
        suelo_abajo = state.carriles[carril - 1]["suelo"]
        obstaculo = state.carriles[carril - 1]["obstaculo_cercano"]
    else:
        suelo_abajo = False
    
    if not suelo_actual and (not suelo_abajo):
            return True

# Regla: DASH si el dash está disponible y hay un obstáculo peligroso o un vacío cercano debajo del kong

def dash(state): 
    if state.Dash == False:
        return False
    
    if dash_obstacle_rule(state):
        return True
    
    if dash_gap_under_kong(state):
        return True

# Regla: DASH si hay un obstáculo peligroso demasiado cerca

def dash_obstacle_rule(state): 
    
    carril = state.carril_actual
    data = state.carriles[carril]["obstaculo_cercano"]

    if data:
        obstaculo, dx, dy = data

        if dx < 80:
            print("DASH por peligro cercano")
            return True

# Regla: DASH si hay un vacío cercano debajo del kong (evitar caer al vacío)

def dash_gap_under_kong(state):
    if state.Dash == False:
        return False
    
    carril = state.carril_actual
    suelo_actual = state.carriles[carril]["suelo"]

    if not suelo_actual and carril == 0 : #añadir estado planeando
        print("DASH por vacío cercano")
        return True
    
# def dash_avalanche(state): - por implementar | falta detectar la avalancha

        
# Funcion auxiliar: True si hay un obstáculo peligroso, False si no hay obstáculo o es seguro

def obstacle(obst_data): 

    if obst_data:
        obstaculo, dx, dy = obst_data
        limites = obst_dist.get(obstaculo.tipo)

        if limites is None:
            print(f"[REGLAS] Obstáculo sin configuración: {obstaculo.tipo}")
            return False

        return (
            (dx + 10) < limites[0]
        )

# Reglas de recolección

# Regla: SALTAR para recolectar una banana que está en el carril superior y no hay obstáculo peligroso

def banana_rule_up(state):
    carril = state.carril_actual

    data = state.carriles[carril + 1]["banana_cercana"]

    if data and not obstacle(state.carriles[carril + 1]["obstaculo_cercano"]):
        banana, dx, dy = data
        return dx < 160

# Regla: PLANEAR para recolectar una banana que está en el mismo carril y no hay obstáculo peligroso

def banana_rule_glide(state):
    carril = state.carril_actual
    data = state.carriles[carril]["banana_cercana"]
    suelo = state.carriles[carril]["suelo"]

    if data and not suelo:
        banana, dx, dy = data

        if dx < 50 and 10< dy < 10:
            return True

# Regla: BAJAR para recolectar una banana que está en el carril inferior y no hay obstáculo peligroso
'''
def banana_rule_down(state):
    carril = state.carril_actual

    if carril > 0:
        data = state.carriles[carril - 1]["banana_cercana"]
        suelo = state.carriles[carril - 1]["suelo"]

        if data and suelo:
            banana, dx, dy = data

            if dx < 150:
                return True
'''

# Reglas de movilidad
def plataforma (state):
    
    carril = state.carril_actual
    if carril < 4:
        suelo_arriba = state.carriles[carril + 1]["suelo"]
        obstaculo = state.carriles[carril + 1]["obstaculo_cercano"]
    else:
        return False

    if suelo_arriba and not obstacle(obstaculo):
        return True


'''
def safe_falling(state):
    
    carril = state.carril_actual
    suelo_actual = state.carriles[carril]["suelo"]
    obstaculo = state.carriles[carril]["obstaculo_cercano"]
    
    if carril == 0 and suelo_actual and not obstacle(obstaculo) :
            return True


# no implementadas

def banana_rule_down(state):
    if state.banana and state.banana_distance is not None:
        if state.banana_distance[0] < 150 and state.banana_distance[1] > 50:
            return True


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
        
'''

# Lista de reglas

rules = [
    Rule(name="dash", condition=dash, action=DASH, priority=0),
    Rule(name="saltar_obstaculo", condition=obstacle_rule, action=SALTAR, priority=1),
    Rule(name="saltar_vacio", condition=gap_rule, action=SALTAR, priority=2),
    Rule(name="caida_peligrosa", condition=dangerous_falling, action=PLANEAR, priority=3),
    Rule(name="recolectar_banana", condition=banana_rule_up, action=SALTAR, priority=4),
    #Rule(name="caida_segura", condition=safe_falling, action=BAJAR, priority=5),
    #Rule(name="recolectar_banana_planear", condition=banana_rule_2, action=PLANEAR, priority=6),
    #Rule(name="plataforma", condition=plataforma, action=SALTAR, priority=7),
]

#Rule(name="Prueba de movilidad", condition=prueba, action=DASH, priority=0), #Regla de prueba