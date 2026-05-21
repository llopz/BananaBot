# Manual de desarrollo

## 1. Propósito del documento

Este documento tiene como objetivo servir de guía técnica para comprender, mantener, extender y dar continuidad al desarrollo del proyecto. Está dirigido a futuros equipos de trabajo que necesiten familiarizarse rápidamente con la estructura del repositorio, la organización de la solución, los contenedores, los scripts, las variables de entorno y el flujo de trabajo del sistema.

## 2. Descripción general del proyecto desde la perspectiva de desarrollo

Bot autónomo para el videojuego **Banana Kong** ejecutado en un emulador Android (BlueStacks / MuMu Player). El bot captura la pantalla del emulador en tiempo real, detecta elementos del juego mediante visión por computador (color HSV + template matching), deduce el estado del juego con un modelo de carriles y aplica un motor de reglas por prioridad para decidir la acción a ejecutar (click de ratón).

```
Captura de pantalla → Detección → Estado del juego → Motor de reglas → Acción (clic)
```

### 2.1 Tecnologías principales

- Python 3.13
- OpenCV (`cv2`)
- mss
- numpy
- pygetwindow
- pyautogui
- keyboard
- MuMu Player / BlueStacks (Emulador Android)

## 3. Estructura del Proyecto

### 3.1 Árbol general del repositorio

```
banana_kong_bot/
├── core/
│   ├── main.py                   ← Punto de entrada del bot
│   ├── config/
│   │   └── settings.py           ← Todos los parámetros configurables
│   ├── control/
│   │   ├── acciones_click.py     ← Módulo de control activo (mouse clicks)
│   ├── metrics/
│   │   ├── bot_metrics.py        ← Métricas de rendimiento y evaluación
│   │   └── detection_metrics.py  ← Tracker de métricas de detección (F1, Precision…)
│   ├── rules/
│   │   ├── game_state.py         ← Modelo de estado del juego por carriles
│   │   ├── rule_engine.py        ← Motor de reglas por prioridad
│   │   ├── rules.py              ← Definición de reglas de decisión
│   ├── utils/                    ← Herramientas de desarrollo (calibración HSV, etc.)
│   └── vision/
│       ├── captura/
│       │   └── captura.py        ← Captura de pantalla del emulador (mss)
│       ├── detection/
│       │   ├── base_detector.py  ← Clase base con métodos de detección compartidos
│       │   ├── detector.py       ← Orquestador paralelo de todos los detectores
│       │   ├── detectors/        ← Un archivo por tipo de elemento detectado
│       │   └── plantillas/       ← Imágenes PNG usadas para template matching
│       └── visualizador/
│           └── visualizador.py   ← Dibuja detecciones y estado sobre el frame
├── diseno/                       ← Diagramas de arquitectura
├── reportes/                     ← CSVs de métricas de detección exportados
└── requirements.txt
```

### 3.2 Flujo de ejecución

```
main.py::main()
│
├─ Inicialización
│   ├── Capturador(título_ventana)       # localiza la ventana del emulador
│   ├── Detector(settings)               # instancia todos los detectores
│   ├── Visualizador(settings)
│   ├── ModuloAcciones()                 # control por click de ratón
│   └── RuleEngine(rules)
│
└─ Loop principal (while True)
    │
    ├── 1. CAPTURA    → Capturador.capturar_y_congelar()
    ├── 2. DETECCIÓN  → Detector.detectar_todos(frame)      ← paralelo en 2 hilos
    ├── 3. ESTADO     → GameState.actualizar(resultados)
    ├── 4. DECISIÓN   → RuleEngine.decide(estado)
    ├── 5. ACCIÓN     → ModuloAcciones.ejecutar(accion)     ← si EJECUTAR_ACCIONES=True
    ├── 6. VISUAL     → Visualizador.dibujar_todo(frame, resultados)
    └── 7. MÉTRICAS   → BotMetrics.log()
```

**Teclas durante la ejecución:**

| Tecla   | Función                                   |
| ------- | ----------------------------------------- |
| `SPACE` | Iniciar / detener detección               |
| `P`     | Pausar / reanudar (congela el frame)      |
| `Q`     | Salir                                     |
| `N`     | Cambiar clase activa en evaluación        |
| `1`     | Etiquetar frame como positivo real (eval) |
| `2`     | Etiquetar frame como negativo real (eval) |
| `M`     | Mostrar métricas de la clase activa       |
| `E`     | Exportar métricas a CSV en `./reportes/`  |

---

## 4. Organización de la solución a nivel de código

### 4.1 Organización por módulos

El proyecto está diseñado siguiendo una arquitectura modular, donde cada módulo tiene una responsabilidad específica dentro del funcionamiento general del bot. Esta organización permite mantener el código desacoplado, facilitar el mantenimiento y simplificar la incorporación de nuevas funcionalidades.

La estructura del sistema se divide en cinco áreas principales:

- Configuración
- Núcleo principal
- Visión computacional
- Motor de reglas
- Control de acciones

### 4.2 Relación entre componentes del sistema y código fuente

### Configuración (`config/`)

El módulo de configuración centraliza todos los parámetros ajustables del sistema en el archivo `settings.py`.

Este archivo actúa como la única fuente de configuración del proyecto, evitando que existan valores definidos directamente dentro de detectores, reglas o módulos internos.

Entre los parámetros configurables se encuentran:

| Sección | Qué configura |
|---------|--------------|
| `EMULADOR_*` | Título de la ventana y frecuencia de refresco de coordenadas |
| `DETECCION_*` | Filtro X mínimo, umbral de forzar detección, frames cada N |
| `<TIPO>_RANGO_BAJO/ALTO` | Rango HSV del detector de color de ese tipo |
| `<TIPO>_AREA_MIN/MAX_PCT` | Porcentaje del área de frame permitido |
| `<TIPO>_PROP_MIN/MAX` | Rango de proporción ancho/alto del bounding box |
| `<TIPO>_TEMPLATE_*` | Archivo PNG, umbral de match y escala para detectores por template |
| `EJECUTAR_ACCIONES` | `False` = modo observación seguro (sin clics) |
| `DEBUG` | Muestra área/proporción de cada detección en pantalla |
| `DEBUG_REGLAS` | Imprime en consola qué regla se disparó en cada frame |
| `METRICAS_*` | Ventana de FPS y frecuencia de log |
| `EVAL_DETECCION_*` | Clases a evaluar, distancia máxima y carpeta de salida |


---

### Núcleo principal (`core/`)

Punto de entrada. Instancia todos los módulos, mantiene el estado del bot (`deteccion_activa`, `pausado`) y ejecuta el loop principal. El resultado del detector se guarda en `resultados` entre frames para reutilizar la última detección si no toca detectar (según `DETECTAR_CADA_N_FRAMES`).

**Detección forzada:** si hay un obstáculo a menos de `DETECCION_FORZAR_DX_UMBRAL` píxeles de Kong, se fuerza la detección aunque no haya llegado el frame N.

---

### Visión computacional (`vision/`)

El módulo de visión es responsable de toda la interacción visual con el juego y se divide en dos componentes principales.

**Captura (`vision/captura`)**

**`Capturador`** usa `mss` para capturar la región de la ventana del emulador. Localiza la ventana por título (`EMULADOR_TITULO`) y refresca sus coordenadas cada `EMULADOR_REFRESCAR_CADA` frames.

- `capturar()` → `np.ndarray` BGR
- `capturar_y_congelar(frame_congelado, pausado)` → devuelve el frame congelado si `pausado=True`


---

**Detección (`vision/detection`)**

Implementa toda la lógica de detección de elementos del juego.

#### `base_detector.py`

Clase base que expone dos métodos de detección reutilizables:

**`_detectar_elemento(...)`** — Detección por color:
1. Convierte el frame al espacio de color indicado (con caché por frame para evitar reconversiones).
2. Aplica `cv2.inRange` para crear una máscara binaria.
3. Aplica erosión y dilatación opcional.
4. Extrae blobs con `connectedComponentsWithStats`.
5. Filtra por área, proporción y zona Y.
6. Devuelve `(elementos, descartados, mascara)`.

**`_detectar_por_template(...)`** — Detección por template matching:
1. Convierte la ROI a gris.
2. Aplica `cv2.matchTemplate` con `TM_CCOEFF_NORMED`.
3. Agrupa detecciones solapadas con `cv2.groupRectangles`.
4. Devuelve `(elementos, descartados, mascara)`.

La clase `Elemento` (dataclass) contiene: `x, y, w, h, centro_x, centro_y, area, proporcion, tipo`.

#### `detector.py`

Orquestador que divide los detectores en dos grupos y los ejecuta en paralelo usando `ThreadPoolExecutor`. Tras la ejecución aplica `_aplicar_filtro_x_minimo` para descartar detecciones a la izquierda de `DETECCION_X_MIN` (excepto kong y barras potenciadoras).

#### `detectors/`

Un archivo por tipo de elemento. Todos heredan de `BaseDetector` e implementan `detectar(frame) → (elementos, descartados, mascara)`.

| Detector | Método | Notas |
|----------|--------|-------|
| `BananaDetector` | color HSV | Zona Y limitada |
| `TroncoDetector` | color HSV | |
| `ArbustoDetector` | color HSV | |
| `AvionDetector` | color HSV | Expande bounding box un 50%/60% para cubrir cola |
| `KongDetector` | color HSV | No aplica filtro X mínimo |
| `ParedDetector` | color HSV | |
| `RocaDetector` | color HSV | |
| `AguaDetector` | color HSV | Solo franja inferior; doble dilatación H+V |
| `PlataformaMaderaDetector` | color HSV | Zona Y muy restringida; altura normalizada |
| `CuevaDetector` | template PNG | Zona Y inferior |
| `BarraPotenciadoraDetector` | template PNG | Filtro por posición fija en pantalla |
| `TotemDetector` | color HSV | Dilatación fuerte para unir fragmentos |
| `TuboDetector` | color HSV | Extensión izquierda del bounding box |


---

### Motor de reglas (`rules/`)

El módulo de reglas implementa la lógica de toma de decisiones del bot.

Se compone de tres partes principales.

**Estado del juego (`game_state.py`)**

`GameState` mantiene un modelo de 5 carriles (`0` = suelo, `4` = más alto). Cada carril almacena:

- `suelo` (bool): hay plataforma sólida en ese carril frente a Kong.
- `banana_cercana`: tupla `(Elemento, dx, dy)` de la banana más próxima en ese carril.
- `obstaculo_cercano`: tupla `(Elemento, dx, dy)` del obstáculo más próximo en ese carril.
- `dash_disponible` (bool): se activa al detectar barra potenciadora y se consume al ejecutar DASH.

El método `actualizar()` se llama cada frame con las listas de detecciones y recalcula todo el estado. También recibe `barras_potenciadoras` para habilitar el estado de dash. El mapping `Y → carril` está en `_obtener_carril()`.

**Para modificar la lógica de carriles** (p.ej. cambiar los rangos de Y), editar `_obtener_carril()` en `game_state.py` y la zona de plataformas de madera (`PLATAFORMA_MADERA_ZONA_Y_INICIO` y `PLATAFORMA_MADERA_ZONA_Y_FIN`) en `settings.py`.

---

**Motor de reglas (`rule_engine.py`)**

`RuleEngine` ordena las reglas por prioridad (menor número = mayor prioridad) y devuelve la acción de la primera regla cuya condición sea `True`. Si ninguna regla aplica, devuelve `NADA`.

#### `rules.py`

Define las funciones de condición y la tabla de reglas activas:

| Nombre | Condición | Acción | Prioridad |
|--------|-----------|--------|-----------|
| `dash` | Dash disponible y peligro inmediato (obstáculo o hueco) | DASH | 0 |
| `saltar_obstaculo` | Obstáculo peligroso en carril actual | SALTAR | 1 |
| `saltar_vacio` | Carril 0 sin suelo bajo Kong | SALTAR | 2 |
| `caida_peligrosa` | Carril actual y carril inferior sin suelo | PLANEAR | 3 |
| `recolectar_banana` | Banana cercana en carril superior sin peligro inmediato arriba | SALTAR | 4 |

Las distancias de reacción por tipo de obstáculo se configuran en el dict `OBST_DIST` al inicio de `rules.py`.
La disponibilidad de dash se consume dentro de la regla `dash` (`dash_rule`) para evitar usos repetidos del mismo power-up.

`plataforma_rule` sigue implementada como regla auxiliar, pero no forma parte de la tabla activa por prioridad.

**Para agregar una regla nueva:** ver sección [Agregar una nueva regla](#agregar-una-nueva-regla).

---

### Control (`control/`)

#### `acciones_click.py` (activo)

`ModuloAcciones` controla el juego mediante clicks de ratón sobre la ventana del emulador usando `pyautogui`.

| Constante | Valor | Acción |
|-----------|-------|--------|
| `NADA` | `"nada"` | Suelta el botón si estaba presionado |
| `SALTAR` | `"saltar"` | Click simple (salto) |
| `PLANEAR` | `"planear"` | Mantiene click presionado |
| `BAJAR` | `"bajar"` | Arrastra hacia abajo |
| `DASH` | `"dash"` | Arrastra horizontalmente |

El módulo tiene un cooldown configurable en `self.cooldown` para evitar saltos repetidos demasiado rápidos.
Además, el módulo usa `pyautogui.PAUSE = 0.05` para estabilizar entradas y en `dash()` suelta primero cualquier click sostenido antes de ejecutar el arrastre.


---

### Flujo general del sistema

El funcionamiento completo del bot sigue el siguiente flujo:

1. Se captura un frame del emulador.
2. Los detectores identifican elementos del entorno.
3. El estado del juego transforma detecciones en información lógica.
4. El motor de reglas decide la acción más adecuada.
5. El módulo de control ejecuta la acción dentro del juego.

---

### Ventajas de la arquitectura modular

La organización modular del proyecto ofrece múltiples ventajas:

- Separación clara de responsabilidades.
- Facilidad de mantenimiento.
- Escalabilidad.
- Reutilización de componentes.
- Facilidad para realizar pruebas.
- Incorporación sencilla de nuevos detectores o reglas.
- Menor acoplamiento entre módulos.

## 5. Archivos de configuración

El archivo principal de configuración es:

`config/settings.py`

Todos los módulos leen directamente de este archivo y no definen parámetros internos por defecto.

## 6. Flujo de trabajo de desarrollo

Describa el proceso recomendado para trabajar sobre el proyecto.

### 6.1 Preparación del entorno

Pasos recomendados para iniciar el entorno de desarrollo:

- Clonar el repositorio.
- Instalar las dependencias desde requirements.txt.
- Instalar y configurar un emulador Android compatible (BlueStacks o MuMu Player).
- Ajustar los parámetros necesarios en config/settings.py.

### 6.2 Desarrollo de nuevas funcionalidades

### Agregar un nuevo detector

1. **Crear el archivo** `core/vision/detection/detectors/nuevo_detector.py`:

```python
from ..base_detector import BaseDetector

class NuevoDetector(BaseDetector):
    def detectar(self, frame):
        cfg = self.config
        return self._detectar_elemento(
            frame,
            cfg.NUEVO_RANGO_BAJO, cfg.NUEVO_RANGO_ALTO,
            cfg.NUEVO_AREA_MIN_PCT, cfg.NUEVO_AREA_MAX_PCT,
            cfg.NUEVO_PROP_MIN, cfg.NUEVO_PROP_MAX,
            "nuevo",
            espacio=cfg.NUEVO_ESPACIO,
        )
```

2. **Añadir parámetros** en `config/settings.py` (sección con el nombre del tipo).

3. **Exportar** el detector en `core/vision/detection/detectors/__init__.py`.

4. **Registrar** en `Detector._registrar_detectores()` (`detector.py`):

```python
self._registrar("nuevo", NuevoDetector(self.config).detectar)
```

5. **Añadir al `resultados` inicial** en `main.py` y extraer con `.get("nuevo", [])`.

6. **Añadir un color** en `visualizador.py` (dict de colores y bloque `if el.tipo == "nuevo":`).

7. Opcionalmente, añadir el tipo a `tipos_obstaculos` en `main.py` si debe influir en la detección forzada.

## Configuración de detectores

Todos los parámetros de detección están en `config/settings.py`. La convención de nombres es:

```
<TIPO>_ESPACIO           → espacio de color ("HSV")
<TIPO>_RANGO_BAJO        → [H_min, S_min, V_min]
<TIPO>_RANGO_ALTO        → [H_max, S_max, V_max]
<TIPO>_AREA_MIN_PCT      → porcentaje mínimo del frame (e.g. 0.002 = 0.2%)
<TIPO>_AREA_MAX_PCT      → porcentaje máximo del frame
<TIPO>_PROP_MIN          → w/h mínimo
<TIPO>_PROP_MAX          → w/h máximo
<TIPO>_TEMPLATE_ARCHIVO  → nombre del PNG en vision/detection/plantillas/
<TIPO>_TEMPLATE_UMBRAL   → score mínimo de matchTemplate [0–1]
<TIPO>_TEMPLATE_ESCALA   → escala del template antes de matching
```

**Herramientas de calibración** (en `core/utils/`):
- `ajuste_hsv.py`: abre la pantalla del emulador con trackbars para ajustar rangos HSV en tiempo real.

---

### Agregar una nueva regla

1. **Definir la función de condición** en `rules/rules.py`:

```python
def mi_regla(state: GameState) -> bool:
    # state.carril_actual, state.carriles[i]["suelo"], etc.
    ...
```

2. **Añadirla a la tabla** `rules` con la prioridad deseada (menor = más urgente):

```python
Rule(name="mi_regla", condition=mi_regla, action=SALTAR, priority=5),
```

3. Probar en ejecución real con `EJECUTAR_ACCIONES = False` antes de habilitar acciones automáticas.

## Sistema de carriles

El juego se divide verticalmente en 5 carriles basados en la coordenada Y:

```
Carril 4  →  y < 149      (plataformas altas)
Carril 3  →  149 < y ≤ 250
Carril 2  →  250 < y ≤ 350
Carril 1  →  350 < y ≤ 450
Carril 0  →  y > 450      (suelo)
```

Kong siempre tiene un carril actual. Las reglas consultan el estado del carril actual y los carriles adyacentes (+1 arriba, -1 abajo) para decidir la acción.

El mapping está en `GameState._obtener_carril(y)`. Si los rangos de Y del juego cambian (p.ej. en una resolución diferente), hay que actualizar tanto `_obtener_carril()` como `PLATAFORMA_ZONAS_Y` en `settings.py`.

---


### 6.3 Ejecución de pruebas y validaciones

Checklist mínimo de validación técnica:

- Ejecutar `./start_bot.ps1` y confirmar inicio sin excepciones.
- Verificar detección de ventana del emulador (`EMULADOR_TITULO` correcto).
- Confirmar funcionamiento de teclas de control (`SPACE`, `P`, `Q`).
- Probar modo seguro con `EJECUTAR_ACCIONES=False`.
- Probar modo activo con `EJECUTAR_ACCIONES=True` solo después de validar detección.
- Verificar que la detección forzada responda ante obstáculos cercanos.
- Activar evaluación (`EVAL_DETECCION_HABILITADA=True`) y registrar muestras con `1/2`.
- Exportar métricas con `E` y validar creación de CSV en `./reportes/`.

### 6.4 Integración de cambios

Se recomienda:

- Desarrollar nuevas funcionalidades en ramas separadas;
- Mantener la estructura modular existente;
- Probar detectores y reglas en modo observación antes de habilitar acciones automáticas;
- Documentar cualquier nuevo detector o regla agregado al sistema.

## 7. Convenciones del proyecto

Describa las convenciones usadas para mantener consistencia en el desarrollo.

### 7.1 Convenciones de código

| Elemento                            | Convención                                                   |
| ----------------------------------- | ------------------------------------------------------------ |
| Variables y funciones               | `snake_case`                                                 |
| Clases                              | `PascalCase`                                                 |
| Constantes / settings               | `SCREAMING_SNAKE_CASE`                                       |
| Tipos de elemento (`Elemento.tipo`) | singular en minúsculas: `"tronco"`, `"banana"`               |
| Claves del dict `resultados`        | plural: `"troncos"`, `"bananas"`                             |
| Parámetros de settings              | prefijo del tipo + sufijo descriptivo: `TRONCO_AREA_MIN_PCT` |

### 7.2 Convenciones de repositorio

Documente prácticas relacionadas con el trabajo colaborativo.

- Ramas: usar prefijos `feat/`, `fix/`, `docs/`, `refactor/`.
- Commits: seguir prefijos semánticos (`feat:`, `fix:`, `docs:`, `refactor:`).
- Pull requests: incluir resumen técnico, archivos impactados y evidencia de validación.
- Alcance por commit: evitar mezclar refactor, documentación y cambios funcionales en un solo commit.
- Integración: hacer merge solo después de validar ejecución local del loop principal.

### 7.3 Convenciones de documentación

Indique cómo debe mantenerse actualizada la documentación del proyecto.

- Si se agrega o elimina un detector, actualizar árbol de proyecto, módulo de detección y tabla de detectores.
- Si se agrega o modifica una regla, actualizar secciones de `rules/` y el flujo de decisión.
- Mantener sincronizados este manual, `README.md` e `INFORME_FINAL_PROYECTO.md`.
- Registrar decisiones técnicas en la sección 9.
- Mantener ejemplos de ejecución en entorno Windows.

## 8. Problemas frecuentes y recomendaciones

Documente errores comunes, limitaciones conocidas, deuda técnica o advertencias importantes para futuros equipos.

### 8.1 Problemas frecuentes

- El bot no detecta la ventana del emulador:
  - Revisar `EMULADOR_TITULO` y confirmar que la ventana no esté minimizada.
- Detecciones inestables:
  - Recalibrar HSV usando `core/utils/ajuste_hsv.py`.
- No se ejecutan acciones:
  - Verificar foco del emulador y estado de `EJECUTAR_ACCIONES`.
- Latencia alta o FPS bajo:
  - Ajustar `DETECTAR_CADA_N_FRAMES` y carga del equipo.

### 8.2 Deuda técnica conocida

- Dependencia de calibración visual manual ante cambios de escena o resolución.
- Sensibilidad a cambios de UI entre versiones del emulador.
- Falta de perfiles de configuración por entorno (resolución/equipo).

### 8.3 Recomendaciones para continuidad

- Crear perfiles de `settings.py` por resolución y emulador.
- Mantener set de capturas etiquetadas para regresión de detección.
- Evitar incorporar lógica nueva sin actualizar este manual en la misma tarea.

## 9. Historial de decisiones técnicas relevantes

Documente decisiones importantes tomadas durante el desarrollo y la razón detrás de ellas.

- Se consolidó `acciones_click.py` como módulo de control activo para simplificar la capa de ejecución.
- Se eliminó detección de barriles y plataformas normales para reducir ruido y complejidad del sistema.
- Se mantuvo enfoque de visión clásica (HSV + template matching) por costo computacional bajo y alta interpretabilidad.
- Se incorporó estado `dash_disponible` y regla `dash` de prioridad máxima para respuesta en peligros inmediatos.
- Se centralizó configuración en `settings.py` para evitar valores mágicos dispersos.

## 10. Referencias relacionadas



