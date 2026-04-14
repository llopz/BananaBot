# ============================================================
# config/settings.py
# ============================================================

EMULADOR_TITULO         = "Android Device"
EMULADOR_REFRESCAR_CADA = 60

# ─── BANANAS ────────────────────────────────────────────────
BANANA_ESPACIO       = "HSV"
BANANA_RANGO_BAJO    = [18, 200, 200]
BANANA_RANGO_ALTO    = [38, 255, 255]
BANANA_AREA_MIN_PCT  = 0.00025
BANANA_AREA_MAX_PCT  = 0.003
BANANA_PROP_MIN      = 0.7
BANANA_PROP_MAX      = 1.6
BANANA_ZONA_Y_INICIO = 50
BANANA_ZONA_Y_FIN    = 580

# ─── TRONCO ─────────────────────────────────────────────────
TRONCO_ESPACIO      = "HSV"
TRONCO_RANGO_BAJO   = [0,  100, 150]
TRONCO_RANGO_ALTO   = [18, 255, 255]
TRONCO_AREA_MIN_PCT = 0.002
TRONCO_AREA_MAX_PCT = 0.008
TRONCO_PROP_MIN     = 0.5
TRONCO_PROP_MAX     = 1.5

# ─── ARBUSTO ────────────────────────────────────────────────
ARBUSTO_ESPACIO      = "HSV"
ARBUSTO_RANGO_BAJO   = [58, 155, 90]
ARBUSTO_RANGO_ALTO   = [70, 220, 240]
ARBUSTO_AREA_MIN_PCT = 0.005
ARBUSTO_AREA_MAX_PCT = 0.014
ARBUSTO_PROP_MIN     = 0.6
ARBUSTO_PROP_MAX     = 1.6

# ─── AVIÓN ──────────────────────────────────────────────────
AVION_ESPACIO      = "HSV"
AVION_RANGO_BAJO   = [83,  60, 200]
AVION_RANGO_ALTO   = [103, 255, 255]
AVION_AREA_MIN_PCT = 0.0003
AVION_AREA_MAX_PCT = 0.004
AVION_PROP_MIN     = 1.0
AVION_PROP_MAX     = 4.0

# === PLATAFORMAS ===
PLATAFORMA_RANGO_BAJO = [5, 50, 70]
PLATAFORMA_RANGO_ALTO = [25, 140, 190]
PLATAFORMA_ESPACIO = "HSV"
PLATAFORMA_AREA_MIN_PCT = 0.005
PLATAFORMA_AREA_MAX_PCT = 0.25
PLATAFORMA_PROP_MIN = 2.0
PLATAFORMA_PROP_MAX = 15.0
PLATAFORMA_ALTURA_STANDAR = 25  
PLATAFORMA_ZONAS_Y = [159, 257, 355, 458]
PLATAFORMA_DILATE_KERNEL = (3, 15)
PLATAFORMA_DILATE_ITER   = 3

# === PLATAFORMAS DE MADERA ===
PLATAFORMA_MADERA_RANGO_BAJO = [0,  100, 150]   
PLATAFORMA_MADERA_RANGO_ALTO = [18, 255, 255]   
PLATAFORMA_MADERA_ESPACIO = "HSV"
PLATAFORMA_MADERA_AREA_MIN_PCT = 0.001 
PLATAFORMA_MADERA_AREA_MAX_PCT = 0.01
PLATAFORMA_MADERA_PROP_MIN = 0.8  
PLATAFORMA_MADERA_PROP_MAX = 30.0
PLATAFORMA_MADERA_ALTURA_STANDAR = 25  
PLATAFORMA_MADERA_ZONAS_Y = [256, 359, 458, 556]  
PLATAFORMA_MADERA_DILATE_KERNEL = (3, 10)   
PLATAFORMA_MADERA_DILATE_ITER   = 3

# ─── PARED / ROCA ───────────────────────────────────────────
PARED_ESPACIO      = "HSV"
PARED_RANGO_BAJO   = [5,  40,  60]
PARED_RANGO_ALTO   = [25, 110, 255]
PARED_AREA_MIN_PCT = 0.002
PARED_AREA_MAX_PCT = 0.08
PARED_PROP_MIN     = 0.3
PARED_PROP_MAX     = 0.7

# ─── AGUA ───────────────────────────────────────────────────
AGUA_ESPACIO       = "XYZ"
AGUA_RANGO_BAJO    = [0,   0,  17]
AGUA_RANGO_ALTO    = [255, 255, 78]
AGUA_ZONA_Y_INICIO = 460   
AGUA_PIXELES_MIN   = 200
AGUA_DILATE_KERNEL_H = (3, 60)
AGUA_DILATE_ITER_H   = 3
AGUA_DILATE_KERNEL_V = (10, 1)
AGUA_DILATE_ITER_V   = 2
# ─── KONG ───────────────────────────────────────────────────
KONG_ESPACIO      = "HSV"
KONG_RANGO_BAJO   = [7,  140, 100]
KONG_RANGO_ALTO   = [20, 210, 255]
KONG_AREA_MIN_PCT = 0.002
KONG_AREA_MAX_PCT = 0.008
KONG_PROP_MIN     = 0.6
KONG_PROP_MAX     = 2.0

# ─── ROCA ───────────────────────────────────────────────────
ROCA_ESPACIO      = "HSV"
ROCA_RANGO_BAJO   = [5,  40,  60]
ROCA_RANGO_ALTO   = [25, 110, 255]
ROCA_AREA_MIN_PCT = 0.008
ROCA_AREA_MAX_PCT = 0.11
ROCA_PROP_MIN     = 0.8
ROCA_PROP_MAX     = 2.8

# ─── CUEVA ───────────────────────────────────────────────────
CUEVA_ESPACIO      = "HSV"
CUEVA_RANGO_BAJO   = [5,  40,  60]
CUEVA_RANGO_ALTO   = [25, 110, 255]
CUEVA_AREA_MIN_PCT = 0.008
CUEVA_AREA_MAX_PCT = 0.12
CUEVA_PROP_MIN     = 2.0           
CUEVA_PROP_MAX     = 3.6           
CUEVA_ZONA_Y_INICIO = 458
CUEVA_EXTENSION_IZQUIERDA = 73

# ─── TOTEM ───────────────────────────────────────────────────
TOTEM_ESPACIO      = "HSV"
TOTEM_RANGO_BAJO   = [10, 170, 140]
TOTEM_RANGO_ALTO   = [22, 255, 220]
TOTEM_AREA_MIN_PCT = 0.003      # mucho más bajo para capturar fragmentos
TOTEM_AREA_MAX_PCT = 0.04
TOTEM_PROP_MIN     = 0.3       # más flexible para fragmentos
TOTEM_PROP_MAX     = 0.6        # más flexible para fragmentos
TOTEM_DILATE_KERNEL = (10, 5)
TOTEM_DILATE_ITER   = 2

# ─── TUBO ───────────────────────────────────────────────────
TUBO_ESPACIO      = "HSV"
TUBO_RANGO_BAJO   = [18, 200, 180]
TUBO_RANGO_ALTO   = [30, 255, 255]
TUBO_AREA_MIN_PCT = 0.003
TUBO_AREA_MAX_PCT = 0.04
TUBO_PROP_MIN     = 0.5
TUBO_PROP_MAX     = 1.5
TUBO_EXTENSION_IZQUIERDA = 20


# ─── PERSONAJE ──────────────────────────────────────────────
PERSONAJE_X_RATIO = 0.30

# ─── CONTROL DEL BOT ────────────────────────────────────────
EJECUTAR_ACCIONES = True

# ─── VISUALIZACIÓN ──────────────────────────────────────────
MOSTRAR_MASCARA   = True
MOSTRAR_ZONA      = True
MOSTRAR_PERSONAJE = True

# ─── DEBUG ──────────────────────────────────────────────────
DEBUG = True