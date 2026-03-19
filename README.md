# Bot autónomo para videojuego usando Visión por Computador y Reglas Predefinidas

## 1. Introducción

En los videojuegos modernos, la toma de decisiones ocurre en tiempo real y está basada en información visual presentada en pantalla. Automatizar la ejecución de un videojuego sin acceso interno al motor del juego representa un desafío técnico significativo, ya que el sistema debe interpretar el estado del juego únicamente a partir de los píxeles capturados en cada frame.

Este proyecto propone el diseño e implementación de un bot autónomo capaz de percibir el estado del juego mediante captura de pantalla en tiempo real, interpretar información relevante usando técnicas de visión por computador, tomar decisiones automáticamente mediante un sistema de reglas predefinidas, y ejecutar acciones simulando entradas de teclado.

El sistema opera bajo un enfoque black-box visual, es decir, sin acceso a memoria interna, sin modificación del cliente del juego y sin uso de APIs propietarias del mismo. El videojuego seleccionado es Banana Kong, un juego de plataformas móvil con desplazamiento lateral continuo, que presenta una estructura visual relativamente consistente y elementos claramente diferenciables por color y forma.

---

## 2. Planteamiento del problema

### 2.1 Contexto

La visión por computador clásica, basada en análisis de color, morfología y contornos, ha sido durante décadas el enfoque predominante para sistemas de percepción visual en tiempo real. A diferencia de los modelos de aprendizaje profundo, no requiere conjuntos de datos etiquetados ni entrenamiento previo, lo que la hace atractiva para entornos donde los recursos computacionales son limitados o donde se necesita una solución interpretable y ajustable.

Sin embargo, su principal limitación está bien documentada: la sensibilidad a variaciones en la escena. Cambios de iluminación, fondos complejos, oclusiones parciales y objetos en movimiento pueden degradar significativamente la precisión de detección. Evaluar estos límites en condiciones reales y controladas es relevante para determinar en qué contextos este enfoque es suficiente y en cuáles se requiere una alternativa más robusta.
Complementariamente, los sistemas de control autónomo basados en reglas predefinidas son ampliamente utilizados en automatización industrial y robótica por su bajo overhead computacional y su comportamiento predecible. No obstante, su efectividad depende críticamente de la calidad de la información percibida: reglas bien diseñadas sobre percepciones erróneas producen decisiones incorrectas.

El videojuego Banana Kong se utiliza en este proyecto como entorno de evaluación controlado. Sus características lo hacen adecuado para este propósito: presenta una escena visualmente compleja con fondo dinámico, múltiples elementos simultáneos de distintos colores y formas, variaciones de iluminación por zonas, y una dinámica de juego que exige reacción en tiempo real. Además, sus métricas de desempeño (puntaje, distancia recorrida) son objetivas, numéricas y reproducibles.

### 2.2 Problema

¿Qué tan efectiva es la combinación de técnicas de visión por computador clásica y un sistema de decisión basado en reglas para sostener el funcionamiento autónomo y continuo de un agente en un entorno visual dinámico y complejo?

**Este problema abarca los siguientes subproblemas técnicos:**

- Captura en tiempo real: obtener frames del emulador con latencia mínima manteniendo una tasa de actualización compatible con la dinámica del juego.
- Percepción visual: identificar y localizar elementos de interés en la escena usando técnicas de visión por computador clásica, sin recurrir a redes neuronales.
- Representación del entorno: construir una descripción estructurada del estado del juego a partir de las detecciones, suficiente para alimentar el módulo de decisión.
- Decisión basada en reglas: diseñar un conjunto de reglas predefinidas que traduzca el estado percibido en acciones concretas (saltar, planear, bajar) de forma efectiva y oportuna.
- Control del agente: simular entradas de teclado sobre el emulador con la precisión y sincronización necesarias para que las acciones tengan efecto en el juego.

### 2.3 Preguntas de Investigación

- ¿Qué tan precisas y estables son las técnicas clásicas de visión por computador para detectar elementos en una escena con fondo dinámico, iluminación variable y objetos en movimiento o rotación?
- ¿Es suficiente un sistema de reglas predefinidas para generar un comportamiento autónomo efectivo cuando la información del entorno proviene únicamente de detección visual clásica?
- ¿Cómo afecta la latencia acumulada del pipeline percepción–decisión–acción al desempeño del agente en un entorno que exige reacción en tiempo real?
- ¿Cuáles son las principales fuentes de fallo del sistema y cómo se manifiestan en el desempeño medido por puntaje?

---

## 3. Restricciones y supuestos de diseño

### 3.1 Restricciones Técnicas

- El sistema no tendrá acceso a la memoria interna del juego ni a su motor.
- No se modificará el cliente del videojuego en ninguna forma.
- La interacción con el juego será exclusivamente mediante captura de pantalla (screen grabbing con mss) y simulación de entradas por teclado (pyautogui).
- El sistema debe cumplir restricciones de tiempo real, minimizando la latencia entre percepción y acción.
- Se trabajará con resolución fija de 960x540 píxeles en el emulador MuMu Player.
- La detección de elementos se basa exclusivamente en técnicas de visión por computador con OpenCV, sin uso de redes neuronales.

### 3.2 Restricciones Operativas y Éticas

- El juego seleccionado es offline y no cuenta con sistemas anti-cheat activos.
- No se utilizarán juegos online competitivos.
- Se respetan los términos de servicio del juego al ejecutarlo en un entorno controlado.
- El bot opera únicamente sobre la instancia local del emulador.

### 3.3 Supuestos

- El videojuego mantiene una estructura visual relativamente consistente entre sesiones.
- Los elementos del juego presentan características visuales suficientemente diferenciables para su detección mediante técnicas clásicas de visión por computador.
- La resolución del emulador se mantiene fija en 960x540 durante la ejecución.
- El emulador MuMu Player se ejecuta con el nombre de ventana Android Device.
- Los colores de los elementos del juego no varían significativamente entre dispositivos.

---

## 4. Alcance

### 4.1 Incluye

- Captura automática de pantalla del emulador mediante detección de ventana por nombre.
- Preprocesamiento de imagen y aplicación de técnicas de visión por computador clásica para la detección de elementos.
- Detección de elementos del juego: coleccionables, obstáculos y personaje principal, según sean relevantes para la toma de decisiones.
- Módulo de decisión basado en reglas predefinidas según el estado del entorno detectado.
- Módulo de acción para generación de entradas simuladas de teclado: salto (C), planeo (Space) y bajada (flecha abajo).
- Visualización de debug en tiempo real con rectángulos de color por tipo de elemento.
- Arquitectura modular con separación de responsabilidades entre percepción, decisión y acción.
- Configuración centralizada de parámetros de detección por elemento y configuración del emulador.
- Documentación técnica, pruebas experimentales y análisis de resultados.

### 4.2 No incluye

- Soporte para múltiples videojuegos.
- Modificación del cliente del juego o acceso a memoria interna.
- Uso de redes neuronales (YOLO, CNN, etc.) para detección de objetos.
- Jugabilidad en mundos alternativos del juego.
- Gestión de mejoras del personaje ni interacción con menús.
- Generalización automática a otros videojuegos u otras resoluciones.

---

## 5. Objetivo

### 5.1 Objetivo General

Diseñar e implementar un sistema autónomo que juegue el videojuego movil Banana Kong en tiempo real mediante el procesamiento de información visual capturada de la pantalla, tomando decisiones basadas en reglas predefinidas y ejecutando acciones a través de la simulación de controles de teclado, con el propósito de maximizar el puntaje obtenido como indicador principal de desempeño.

### 5.2 Objetivos Específicos

- Implementar un módulo de captura de pantalla en tiempo real que se adapte automáticamente a la posición de la ventana del emulador.
- Desarrollar un pipeline de visión por computador clásica capaz de detectar los elementos relevantes del juego mediante las técnicas más adecuadas según las características visuales de cada elemento.
- Construir un módulo de decisión basado en reglas que determine la acción óptima a partir del estado visual detectado.
- Implementar un módulo de control que traduzca las decisiones en entradas de teclado simuladas sobre el emulador.
- Validar el sistema utilizando metricas de desempeño.

---

## 6. Estado del Arte / Soluciones Relacionadas

Esta sección presenta las soluciones existentes para automatización visual de videojuegos, analizando qué soluciones existen hoy, cómo abordan el problema y qué limitaciones presentan, con el fin de identificar el vacío técnico que justifica el presente proyecto.

### 6.1 Productos Comerciales

En el mercado existen herramientas comerciales orientadas a automatización de interfaces visuales que han sido adaptadas para videojuegos. AutoHotkey es ampliamente usado para automatizar acciones repetitivas en juegos mediante simulación de teclado y detención de color de píxel en coordenadas fijas. Su enfoque es puramente reactivo: ejecuta una acción cuando un píxel en una posición predefinida alcanza un color determinado. Sikuli renombrado posteriormente como SikuliX, permite automatizar interfaces gráficas mediante reconocimiento visual de imágenes capturadas de pantalla usando template matching.

#### ¿Cómo abordan el problema?

Ambas herramientas trabajan con coordenadas fijas o imágenes de referencia estáticas. AutoHotkey detecta un único píxel en una posición predeterminada; SikuliX busca una imagen capturada previamente dentro de la pantalla.

#### Limitaciones:

Ambas soluciones dependen de posiciones fijas en pantalla y no construyen una representación del entorno. Son frágiles ante cambios de resolución, escala o posición de ventana. No son capaces de detectar múltiples instancias de un mismo elemento ni de inferir distancias relativas entre objetos, lo que las hace inadecuadas para videojuegos dinámicos con múltiples elementos simultáneos.

### 6.2 Soluciones Open-Source

En el ecosistema open-source destacan tres soluciones relevantes. El bot para Chrome Dino [1], [6], [5] es el caso más documentado y comparable con este proyecto: usa mss para captura, OpenCV para detección de obstáculos y pyautogui para simulación de teclado. SerpentAI [2] es un framework genérico para bots de videojuegos con soporte para detección por color, template matching y modelos de ML, usado para automatizar títulos como Shovel Knight. MAA automatiza el juego móvil Arknights en emulador Android usando OpenCV con detección visual clásica y reglas, alcanzando tasas de decisión de 10–30 acciones por segundo.

#### ¿Cómo abordan el problema?

Todas siguen la misma arquitectura pipeline: captura (mss o dxcam) → percepción (OpenCV) → decisión (reglas o modelo) → acción (pyautogui o ADB). La detección se basa en técnicas clásicas: template matching, suma de píxeles o segmentación por color. Las decisiones son reglas codificadas manualmente según el estado detectado.

#### Limitaciones:

Estas soluciones están diseñadas para juegos específicos con poca variabilidad visual. Chrome Dino tiene un fondo blanco uniforme, lo que elimina la mayor parte del problema de segmentación. SerpentAI es genérico, pero no provee estrategias de detección para escenas con fondos complejos. MAA está construido sobre imágenes de referencia estáticas (templates), lo que lo hace sensible a cambios gráficos del juego. Ninguna de estas soluciones ha sido aplicada a juegos con fondos dinámicos de alta variabilidad visual como Banana Kong, donde el fondo en movimiento comparte rangos de color con los objetos de interés.

### 6.3 Arquitecturas y Enfoques Técnicos

Desde el punto de vista arquitectural, los sistemas de automatización visual de videojuegos pueden clasificarse en cuatro enfoques según su módulo de percepción y su módulo de decisión:

#### Visión clásica + Reglas (este proyecto):

Segmentación HSV, template matching u operaciones morfológicas para percepción; árboles de decisión o máquinas de estados para acción. Sin entrenamiento, bajo costo computacional, comportamiento determinista e interpretable. Sensible a variaciones visuales del entorno; requiere calibración manual por juego [3], [7].

#### Detección con redes neuronales + Reglas:

Modelos como YOLO para percepción; reglas para decisión. Alta precisión de detección, robusto ante variaciones visuales. Requiere dataset etiquetado y entrenamiento previo; mayor costo computacional en inferencia [9].

#### Visión clásica + Aprendizaje por Refuerzo:

Percepción clásica como preprocesamiento; agente RL para aprender la política. Combina eficiencia de percepción con aprendizaje automático de estrategias. Requiere largo entrenamiento y diseño cuidadoso de la función de recompensa.

#### End-to-end Deep RL (píxeles a acciones):

El agente recibe píxeles crudos y aprende directamente la política óptima [8]. Potencialmente más capaz pero con altísimo costo computacional y de entrenamiento; impracticable en recursos académicos estándar.

### 6.4 Comparación de Soluciones

La siguiente tabla compara las soluciones revisadas según los criterios más relevantes para el contexto de este proyecto:

#### AutoHotkey / SikuliX:

Funcionalidad limitada (píxel único o template fijo). Sin representación del entorno. Costo nulo. Fácil de usar, pero rígido. Limitación técnica crítica: no apto para escenas dinámicas.

#### Bot Chrome Dino / SerpentAI:

Percepción visual clásica con detección de múltiples elementos. Open-source y adaptable. Probado solo en fondos simples (fondo blanco uniforme). Limitación técnica: no validado en escenas con fondo dinámico complejo.

#### YOLO + Reglas:

Alta precisión de detección, robusto ante variabilidad visual. Requiere dataset etiquetado y GPU para entrenamiento. Escalable a otros juegos. Limitación técnica: costo de entrenamiento prohibitivo para prototipo académico.

#### Deep RL (DQN/PPO):

Aprende estrategias óptimas automáticamente. Alta escalabilidad. Requiere miles de episodios de entrenamiento y capacidad computacional significativa. Comportamiento no interpretable. Limitación técnica: impracticable en hardware académico estándar sin GPU de alto rendimiento.

### 6.5 Vacío Identificado y Justificación de la Solución Propuesta

Del análisis anterior se identifican dos vacíos no resueltos por las soluciones existentes:

- **Vacío de percepción:** Las soluciones open-source documentadas (Chrome Dino, SerpentAI) funcionan en escenas visualmente simples con fondo uniforme. No existe evidencia publicada de que la visión clásica (sin redes neuronales) sea suficientemente robusta para detectar múltiples elementos simultáneos en un fondo dinámico y complejo como el de Banana Kong, donde el fondo en movimiento comparte rangos de color con los objetos de interés.

- **Vacío de decisión:** No existen trabajos que evalúen empíricamente la efectividad de un sistema de reglas predefinidas cuando la información del entorno proviene exclusivamente de percepción visual clásica en una escena dinámica. Se desconoce si los errores de percepción se acumulan de forma que degraden las decisiones por encima de un umbral crítico.

Estos vacíos justifican la necesidad de este proyecto: no se trata simplemente de implementar un bot, sino de evaluar empíricamente hasta dónde llegan las técnicas clásicas de visión por computador combinadas con un sistema de decisiones basado en reglas en un entorno visualmente desafiante, usando el puntaje del juego como métrica objetiva de desempeño del sistema completo.

---

## 7. Propuesta de solución

El sistema sigue un pipeline estructurado en 7 etapas que se ejecutan en tiempo real en cada frame del juego:

**1. Captura de pantalla:** La librería mss captura el contenido de la ventana del emulador directamente desde la memoria de video. La ventana se detecta automáticamente por nombre usando pygetwindow, refrescando las coordenadas cada 60 frames para adaptarse si el usuario mueve la ventana.

**2. Preprocesamiento:** el frame capturado se convierte al espacio de representación más adecuado según la técnica de detección a aplicar. Se realizan operaciones de limpieza y acondicionamiento de la imagen para mejorar la precisión de las detecciones.

**3. Limpieza de máscara:** Se aplica erosión morfológica para eliminar píxeles de ruido sueltos, seguida de dilatación para restaurar el tamaño original de los objetos reales. Esto reduce significativamente los falsos positivos sin afectar los elementos de interés.

**4. Extracción de características:** Se detectan contornos en la máscara binaria resultante. Para cada contorno se calcula su área, bounding box, proporción ancho/alto y posición en el frame. Los elementos se filtran por área relativa al tamaño del frame (independiente de la resolución), proporción y zona Y.

**5. Construcción del estado:** Los elementos que pasan los filtros se clasifican por tipo (coleccionables, obstáculos, personaje). Esta información constituye la representación del estado del entorno para el módulo de decisión.

**6. Módulo de decisión:** Un sistema de reglas predefinidas analiza el estado actual y determina la acción a ejecutar en el siguiente ciclo. Las reglas consideran la posición relativa de obstáculos respecto al personaje y la presencia de bananas en altura.

**7. Ejecución de acción:** El módulo de control traduce la decisión en una entrada de teclado simulada mediante pyautogui: salto, planeo, bajada o embestida. Las acciones se envían al emulador independientemente de qué ventana tenga el foco.

---

## 8. Requerimientos preliminares

### 8.1 Requerimientos Funcionales

- Captura automática y continua de la pantalla del videojuego a través del emulador.
- Detección en tiempo real de coleccionables, obstáculos y personaje principal relevantes para la navegación autónoma.
- Clasificación de elementos detectados por tipo para construir el estado del entorno.
- Toma de decisiones automática mediante reglas predefinidas basadas en el estado.
- Simulación de entradas de teclado (salto, planeo, bajada, embestida) sobre el emulador.
- Ejecución autónoma sin intervención humana tras el período de gracia inicial.
- Visualización de debug en tiempo real con indicadores visuales por tipo de elemento.

### 8.2 Requerimientos No Funcionales

- Operación en tiempo real con latencia mínima entre captura y ejecución de acción.
- Arquitectura modular con separación percepción–decisión–acción.
- Uso exclusivo de información visual (enfoque black-box).
- Parámetros de detección por elemento configurables de forma independiente sin modificar el código fuente.
- Detección independiente de la resolución mediante áreas relativas al tamaño del frame.
- Adaptación automática a cambios de posición de la ventana del emulador.

---

## 9. Criterios de Aceptación Iniciales

- Captura de pantalla estable y continua durante toda la ejecución del juego.
- Detección correcta del personaje Kong y obstáculos principales en tiempo real.
- Respuesta automática del bot ante obstáculos detectados sin intervención humana.
- Ejecución correcta de las cuatro entradas simuladas: salto, planeo, bajada y embestida.
- Ciclo percepción–decisión–acción sin bloqueos ni retrasos críticos que afecten el juego.
- Metricas de exito: Se obtiene un resultado satiscatorio referente a las metricas de desempeño (elementos identificados, tiempo de supervivencia, puntaje obtenido, etc).
- Resultados reproducibles en múltiples ejecuciones bajo condiciones similares.

---

## 10. Stack Tecnológico

**Python 3.x:** Lenguaje principal del proyecto.

**OpenCV (cv2):** Procesamiento de imágenes y visión por computador: conversión de espacios de color, operaciones morfológicas, detección de contornos.

**mss:** Captura de pantalla de alto rendimiento (~1-2ms por frame) con acceso directo a la memoria de video.

**numpy:** Manipulación eficiente de matrices de imágenes.

**pygetwindow:** Detección automática de la ventana del emulador por nombre y obtención de coordenadas.

**pyautogui:** Simulación de entradas de teclado sobre el emulador.

**keyboard:** Detección global de teclas de control (pausar, salir) independientemente de qué ventana tenga el foco.

**MuMu Player (Android):** Emulador Android que ejecuta Banana Kong a resolución 960x540.

---

## 11. Plan de Trabajo

**Fase 1 — Captura y preprocesamiento:** Implementación del módulo de captura con detección automática de ventana. Conversión de espacios de color y limpieza morfológica de máscara.

**Fase 2 — Detección de elementos:** Calibración de parámetros de detección para cada elemento del juego. Validación con capturas estáticas.

**Fase 3 — Módulo de control:** Implementación de simulación de teclado sobre el emulador. Validación de las cuatro acciones disponibles (salto, planeo, bajada, embestida).

**Fase 4 — Módulo de decisión:** Diseño e implementación de reglas predefinidas basadas en el estado visual. Pruebas de respuesta ante obstáculos y coleccionables.

**Fase 5 — Integración y pruebas:** Integración del pipeline completo percepción–decisión–acción. Ajuste fino de parámetros. Medición del puntaje en múltiples ejecuciones.

**Fase 6 — Documentación:** Redacción del informe técnico, análisis de resultados y preparación de la presentación.

---

## 12. Cronograma de Prototipos

**Duración:** 7 semanas · **5 prototipos**  
**Enfoque:** desarrollo iterativo de los módulos de **captura, percepción y reglas**, validando el sistema completo en cada ciclo.

---

### Resumen

| Prototipo   | Semana(s) | Enfoque                     | Entregable                                                |
| ----------- | --------- | --------------------------- | --------------------------------------------------------- |
| Prototipo 1 | S7        | Pipeline mínimo             | Sistema captura → detección → acción funcionando          |
| Prototipo 2 | S8        | Percepción y reglas básicas | Bot esquiva obstáculos principales                        |
| Prototipo 3 | S9        | Sistema de supervivencia    | Bot maneja múltiples obstáculos                           |
| Prototipo 4 | S10–S11   | Estrategia completa         | Bot incorpora preferencia de trayectoria y mejora puntaje |
| Prototipo 5 | S12–14    | Ajuste y validación         | Sistema estable y evaluación final                        |

---

### Prototipo 1: Pipeline mínimo

| componente     | Descripción                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Hipótesis**  | Es posible ejecutar el pipeline completo en tiempo real.                                                                 |
| **Construir**  | - Integrar captura, detección, reglas y acciones.<br>- Detectar al menos un obstáculo y reaccionar con una regla simple. |
| **Medir**      | - Latencia del pipeline.<br>- Tiempo de supervivencia en varias ejecuciones.                                             |
| **Aprender**   | - Validar si la detección y reacción ocurren a tiempo.                                                                   |
| **Entregable** | Bot funcional mínimo.                                                                                                    |

---

### Prototipo 2: Percepción completa y set de reglas básicas

| componente     | Descripción                                                                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hipótesis**  | Los elementos del juego se detectan con menos del 20% de falsos positivos de forma simultánea y la supervivencia mejora debido a un set de reglas básicas. |
| **Construir**  | - Incorporar nuevos obstáculos al módulo de percepción.<br>- Definir reglas básicas para esquivarlos.                                                      |
| **Medir**      | - Tiempo de supervivencia promedio.<br>- Tasa de esquive por obstáculo.                                                                                    |
| **Aprender**   | - Identificar detecciones inestables o reglas insuficientes.                                                                                               |
| **Entregable** | Bot que sobrevive consistentemente más que sin automatización.                                                                                             |

---

### Prototipo 3: Sistema de supervivencia

| componente     | Descripción                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------------- |
| **Hipótesis**  | Reglas basadas en distancia y prioridad mejoran el comportamiento del agente.                            |
| **Construir**  | - Refinar detecciones existentes.<br>- Implementar lógica basada en proximidad y prioridad entre reglas. |
| **Medir**      | - Tiempo de supervivencia promedio.<br>- Principales causas de fallo.                                    |
| **Aprender**   | - Determinar qué situaciones requieren nuevas reglas o ajustes.                                          |
| **Entregable** | Bot que maneja múltiples obstáculos de forma consistente.                                                |

---

### Prototipo 4: Estrategia completa

| componente     | Descripción                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hipótesis**  | Integrar una trayectoria preferencial hacia las bananas permite aumentar el puntaje sin afectar la supervivencia.                                       |
| **Construir**  | - Implementar una preferencia de trayectoria hacia bananas cuando no exista riesgo inmediato.<br>- Definir prioridad entre supervivencia y recolección. |
| **Medir**      | - Puntaje promedio en múltiples ejecuciones.<br>- Conflictos entre reglas.                                                                              |
| **Aprender**   | - Ajustar reglas para optimizar el desempeño.                                                                                                           |
| **Entregable** | Bot con sistema de decisión completo.                                                                                                                   |

---

### Prototipo 5: Ajuste y validación final

| componente     | Descripción                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| **Hipótesis**  | Ajustes basados en fallos observados permiten estabilizar el sistema.                       |
| **Construir**  | - Ajustar parámetros de detección y activación de reglas.<br>- Ejecutar batería de pruebas. |
| **Medir**      | - Puntaje y estabilidad en múltiples ejecuciones.                                           |
| **Aprender**   | - Identificar las limitaciones del enfoque basado en visión clásica y reglas.               |
| **Entregable** | Sistema validado y métricas finales.                                                        |

---

## 13. Diagramas

<p align="center">
  <img src="diseno/diagramas/DiagramaArquitectura.png" alt="Diagrama Arquitectura" width="700">
</p>

<p align="center">
  <img src="diseno/diagramas/DiagramaInteraccionEntreModulos.png" alt="Diagrama Interacción entre Módulos" width="700">
</p>

<p align="center">
  <img src="diseno/diagramas/SecuenciaTomadeDecision.png" alt="Secuencia Toma de Decisión" width="700">
</p>

<p align="center">
  <img src="diseno/diagramas/SecuenciaDeteccion.png" alt="Secuencia Detección" width="700">
</p>

## 14. Referencias

[1] arturfog, “Chrome Dino game bot using OpenCV and mss,” GitHub, 2021. [Online]. Available https://github.com/arturfog/dino

[2] N. Bergeron, “SerpentAI — Game Agent Framework,” GitHub, 2017. [Online]. Available: https://github.com/SerpentAI/SerpentAI

[3] G. Bradski and A. Kaehler, Learning OpenCV: Computer Vision with the OpenCV Library. Sebastopol, CA: O’Reilly Media, 2008.

[4] T. Butnaru, “mss — An ultra-fast cross-platform multiple screenshots module in pure Python,” 2019. [Online]. Available: https://python-mss.readthedocs.io/

[5] GeeksforGeeks, “Building a Chrome Dino bot using Python and OpenCV,” 2023. [Online]. Available: https://www.geeksforgeeks.org/python/automate-chrome-dino-game-using-python/

[6] LearnOpenCV, “Chrome Dino Game Bot with OpenCV and Python,” 2022. [Online]. Available: https://learnopencv.com/tag/chrome-dino-game-bot/

[7] I. Millington and J. Funge, Artificial Intelligence for Games, 2nd ed. Burlington, MA: Morgan Kaufmann, 2009.

[8] V. Mnih et al., “Human-level control through deep reinforcement learning,” Nature, vol. 518, pp. 529–533, Feb. 2015.

[9] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, “You only look once: Unified, real-time object detection,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), Las Vegas, NV, 2016, pp. 779–788.
