# ============================================================
# config/settings.py
# ============================================================

EMULADOR_TITULO = "Android Device"
EMULADOR_REFRESCAR_CADA = 60

# ─── BANANAS ────────────────────────────────────────────────
BANANA_HSV_BAJO = [13, 180, 180]
BANANA_HSV_ALTO = [43, 255, 255]
BANANA_AREA_MIN_PCT = 0.00015
BANANA_AREA_MAX_PCT = 0.0008
BANANA_PROP_MIN = 0.6
BANANA_PROP_MAX = 1.6
BANANA_ZONA_Y_INICIO = 50
BANANA_ZONA_Y_FIN = 540

# ─── TRONCO ─────────────────────────────────────────────────
TRONCO_HSV_BAJO = [0, 100, 150]
TRONCO_HSV_ALTO = [18, 255, 255]
TRONCO_AREA_MIN_PCT = 0.002
TRONCO_AREA_MAX_PCT = 0.008
TRONCO_PROP_MIN = 0.5
TRONCO_PROP_MAX = 1.5

# ─── ARBUSTO ────────────────────────────────────────────────
# Verde brillante H=50, S=157, V=219
ARBUSTO_HSV_BAJO = [58, 155, 90]
ARBUSTO_HSV_ALTO = [70, 220, 240]
ARBUSTO_AREA_MIN_PCT = 0.005
ARBUSTO_AREA_MAX_PCT = 0.014
ARBUSTO_PROP_MIN = 0.6
ARBUSTO_PROP_MAX = 1.6

# ─── AVIÓN ──────────────────────────────────────────────────
AVION_HSV_BAJO = [83, 60, 200]
AVION_HSV_ALTO = [103, 255, 255]
AVION_AREA_MIN_PCT = 0.0003
AVION_AREA_MAX_PCT = 0.004
AVION_PROP_MIN = 1.0
AVION_PROP_MAX = 4.0

# ─── KONG ───────────────────────────────────────────────────
KONG_HSV_BAJO = [7, 140, 100]
KONG_HSV_ALTO = [20, 210, 255]
KONG_AREA_MIN_PCT = 0.002
KONG_AREA_MAX_PCT = 0.008
KONG_PROP_MIN = 0.6
KONG_PROP_MAX = 2.0

# ─── PERSONAJE ──────────────────────────────────────────────
PERSONAJE_X_RATIO = 0.30

# ─── VISUALIZACIÓN ──────────────────────────────────────────
MOSTRAR_MASCARA = True
MOSTRAR_ZONA = True
MOSTRAR_PERSONAJE = True

# ─── DEBUG ──────────────────────────────────────────────────
DEBUG = True
