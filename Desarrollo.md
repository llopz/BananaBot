# Manual de desarrollo

## 1. Propósito del documento

Este documento tiene como objetivo servir de guía técnica para comprender, mantener, extender y dar continuidad al desarrollo del proyecto. Está dirigido a futuros equipos de trabajo que necesiten familiarizarse rápidamente con la estructura del repositorio, la organización de la solución, los contenedores, los scripts, las variables de entorno y el flujo de trabajo del sistema.

## 2. Descripción general del proyecto desde la perspectiva de desarrollo

Bot autónomo para el videojuego **Banana Kong** ejecutado en un emulador Android (BlueStacks / MuMu Player). El bot captura la pantalla del emulador en tiempo real, detecta elementos del juego mediante visión por computador (color HSV + template matching), deduce el estado del juego con un modelo de carriles y aplica un motor de reglas por prioridad para decidir la acción a ejecutar (click de ratón).

```
Captura de pantalla → Detección → Estado del juego → Motor de reglas → Acción (clic)
```

### 2.1 Tecnologías principales (Pendiente)

- Python 3.x
- OpenCV (`cv2`)
- mss
- numpy
- pygetwindow
- pyautogui
- keyboard
- MuMu Player (Emulador Android)

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

- Configuración del emulador.
- Frecuencia de captura y detección.
- Rangos HSV para detección por color.
- Configuración de templates.
- Parámetros de debugging.
- Métricas de rendimiento.
- Evaluación de detección.
- Activación o desactivación de acciones reales.

Gracias a este enfoque, el comportamiento general del sistema puede modificarse sin alterar la lógica interna del código.

---

### Núcleo principal (`core/`)

El módulo `core` contiene el punto de entrada principal del proyecto (`main.py`) y coordina el funcionamiento general del bot.

Sus responsabilidades incluyen:

- Inicializar todos los módulos.
- Mantener estados globales del sistema.
- Ejecutar el loop principal.
- Coordinar captura, detección, reglas y acciones.
- Reutilizar detecciones entre frames para optimizar rendimiento.

También implementa mecanismos de optimización como la detección forzada cuando un obstáculo se encuentra demasiado cerca del personaje.

---

### Visión computacional (`vision/`)

El módulo de visión es responsable de toda la interacción visual con el juego y se divide en dos componentes principales.

**Captura (`vision/captura`)**

Encargado de capturar frames del emulador utilizando `mss`.

Además:

- Localiza automáticamente la ventana del emulador.
- Refresca periódicamente sus coordenadas.
- Permite congelar el último frame cuando el sistema se encuentra pausado.

---

**Detección (`vision/detection`)**

Implementa toda la lógica de detección de elementos del juego.

La arquitectura de detección se basa en:

- Una clase base reutilizable (`BaseDetector`).
- Detectores independientes por tipo de elemento.
- Un orquestador que ejecuta detectores en paralelo.

El sistema soporta dos métodos principales de detección:

- Detección por color HSV.
- Detección por template matching.

Cada detector se encuentra desacoplado en archivos independientes dentro de `detectors/`, lo que facilita agregar nuevos elementos sin modificar la arquitectura general.

---

### Motor de reglas (`rules/`)

El módulo de reglas implementa la lógica de toma de decisiones del bot.

Se compone de tres partes principales.

**Estado del juego (`game_state.py`)**

Construye una representación lógica del entorno mediante un sistema basado en carriles.

Este estado almacena información como:

- Suelo disponible.
- Obstáculos cercanos.
- Bananas cercanas.
- Disponibilidad de dash.

Toda la información detectada visualmente se transforma aquí en información utilizable por las reglas.

---

**Motor de reglas (`rule_engine.py`)**

Evalúa las reglas activas según prioridad y selecciona la primera acción válida.

Si ninguna regla aplica, el sistema retorna la acción `NADA`.

---

**Reglas (`rules.py`)**

Define el comportamiento del bot mediante reglas específicas, por ejemplo:

- Saltar obstáculos.
- Evitar huecos.
- Planear caídas.
- Recolectar bananas.
- Utilizar dash en situaciones críticas.

El diseño basado en prioridades permite extender fácilmente el comportamiento agregando nuevas reglas sin modificar el motor principal.

---

### Control (`control/`)

El módulo de control ejecuta las acciones físicas dentro del juego mediante automatización de entradas usando `pyautogui`.

Las acciones del sistema se abstraen mediante constantes como:

- `SALTAR`
- `PLANEAR`
- `DASH`
- `BAJAR`
- `NADA`

Cada acción se implementa utilizando clicks, arrastres o pulsaciones sostenidas sobre la ventana del emulador.

Además, el módulo incorpora:

- Cooldowns entre acciones.
- Estabilización de entradas.
- Liberación segura de clicks sostenidos.

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

### 6.3 Ejecución de pruebas y validaciones (P)

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

### 7.2 Convenciones de repositorio (Pendiente)

Documente prácticas relacionadas con el trabajo colaborativo.

Ejemplo:

- nombres de ramas;
- mensajes de commit;
- manejo de issues;
- versionado.

### 7.3 Convenciones de documentación (Pendiente)

Indique cómo debe mantenerse actualizada la documentación del proyecto.

## 8. Problemas frecuentes y recomendaciones (Pendiente)

Documente errores comunes, limitaciones conocidas, deuda técnica o advertencias importantes para futuros equipos.

### 8.1 Problemas frecuentes

Ejemplo:

- errores de puertos;
- variables de entorno faltantes;
- problemas de conexión a la base de datos;
- conflictos entre versiones;
- errores de permisos.

### 8.2 Deuda técnica conocida

Liste componentes incompletos, decisiones provisionales, refactors pendientes o limitaciones actuales del sistema.

### 8.3 Recomendaciones para continuidad

Indique sugerencias concretas para futuros grupos que deban continuar el proyecto.

## 9. Historial de decisiones técnicas relevantes (Pendiente)

Documente decisiones importantes tomadas durante el desarrollo y la razón detrás de ellas.

Ejemplo:

- elección de framework;
- cambio de base de datos;
- adopción o descarte de contenedores;
- reestructuración de módulos;
- cambio en estrategia de autenticación.

## 10. Referencias relacionadas
