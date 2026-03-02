# Bot autónomo para videojuego usando Visión por Computador y Reglas Predefinidas

## 1. Introducción

En los videojuegos modernos, la toma de decisiones ocurre en tiempo real
y está basada principalmente en información visual presentada en
pantalla. Automatizar la ejecución de un videojuego sin acceso interno
al motor representa un desafío significativo, ya que el sistema debe
interpretar la escena únicamente a partir de los píxeles capturados.

Este proyecto propone el diseño e implementación de un bot autónomo
capaz de percibir el estado del juego mediante captura de pantalla,
interpretar información relevante usando técnicas de visión por
computador, tomar decisiones automáticamente y ejecutar acciones
mediante simulación de teclado.

El sistema operará bajo un enfoque black-box visual, es decir, sin
acceso a memoria interna ni modificación del cliente del juego.

---

## 2. Planteamiento del problema

Muchos videojuegos requieren percepción visual compleja y decisiones en
milisegundos. Automatizar este proceso sin acceso a APIs internas ni
datos estructurados del juego implica resolver múltiples desafíos
técnicos:

- Extraer información relevante desde la imagen del juego.
- Construir una representación del estado del entorno.
- Diseñar una estrategia de decisión eficiente.
- Garantizar desempeño en tiempo real.

El problema central del proyecto es diseñar un sistema autónomo capaz de
jugar un videojuego en tiempo real utilizando únicamente información
visual capturada desde pantalla y ejecutando acciones mediante
simulación de entradas.

---

## 3. Restricciones y supuestos de diseño

### Restricciones técnicas

- El sistema no tendrá acceso a la memoria interna del juego.
- No se modificará el cliente del videojuego.
- La interacción será exclusivamente mediante captura de pantalla (screen grabbing) y simulación de entradas por teclado.
- El sistema debe cumplir restricciones de tiempo real, minimizando la latencia entre percepción y acción.
- Se trabajará con un único videojuego para acotar el alcance del proyecto.

### Restricciones operativas y éticas

- No se utilizarán juegos online competitivos con sistemas anti-cheat
  activos.
- Se priorizarán juegos offline, open-source o entornos controlados.
- Se respetarán los términos de servicio del juego seleccionado.

### Supuestos

- El videojuego mantiene una estructura visual relativamente
  consistente.
- Es posible identificar información relevante como HUD, personaje,
  enemigos u obstáculos mediante técnicas de visión por computador.
- Se contará con recursos computacionales suficientes para pruebas y,
  en caso necesario, entrenamiento de modelos de aprendizaje por
  refuerzo.

---

## 4. Alcance

### Incluye

- Selección del videojuego objetivo y definición de métricas de éxito de manera conjunta entre los grupos.
- Desarrollo del módulo de captura y preprocesamiento de imagen.
- Desarrollo del módulo de percepción para extracción del estado del entorno a partir de la imagen, utilizando técnicas definidas en OpenCV y/o redes (YOLO/segmentación).
- Desarrollo del módulo de decisión (estrategia basada en reglas).
- Desarrollo del módulo de acción para generación de entradas simuladas.
- Diseño de arquitectura del sistema.
- Documentación técnica, pruebas experimentales, análisis de resultados y validación del desempeño.

### No incluye

- Soporte para múltiples videojuegos.
- Juegos online competitivos con sistemas anti-cheat.
- Modificación del cliente del juego.
- Acceso a memoria interna del juego.
- Generalización automática a otros videojuegos.

### Delimitaciones especificas del videojuego

- Se excluye la jugabilidad en mundos alternativos.
- Se excluye la gestión de mejoras del personaje.

---

## 5. Objetivo

Diseñar e implementar un sistema autónomo que juegue un videojuego en tiempo real
(especificamente el videojuego móvil Banana Kong) usando únicamente información
visual capturada de la pantalla, que tome decisiones basadas en reglas
predefinidas y que ejecute acciones mediante simulación de controles por teclado,
con el fin de maximizar el puntaje obtenido como métrica principal de desempeño.

---

<!--
## 6. Estado del Arte y Soluciones Relacionadas

---
--->

## 7. Propuesta de solución

El sistema seguirá un pipeline estructurado compuesto por las siguientes
etapas:

- Captura de pantalla.
- Preprocesamiento de imagen.
- Extracción de características.
- Construcción del estado del entorno.
- Módulo de decisión.
- Generación de acción.
- Ejecución de entrada simulada.

---

## 8. Requerimientos preliminares

### Requerimientos Funcionales

- Captura automática de pantalla del videojuego.
- Preprocesamiento de imágenes para análisis visual.
- Detección de elementos del juego (personaje y obstáculos).
- Seguimiento del estado del entorno en tiempo real.
- Toma de decisiones mediante reglas predefinidas.
- Simulación automática de entradas de teclado.
- Ejecución autónoma sin intervención humana.
- Registro de puntaje y resultados de ejecución.

### Requerimientos No Funcionales

- Operación en tiempo real con baja latencia.
- Arquitectura modular (percepción–decisión–acción).
- Uso exclusivo de información visual (enfoque black-box).
- Ejecución reproducible bajo mismas condiciones.
- Documentación técnica del sistema y configuración.

---

## 9. Criterios de Aceptación Iniciales

- Captura de pantalla estable durante la ejecución del juego.
- Detección correcta del personaje y obstáculos en tiempo real.
- Respuesta automática ante obstáculos detectados.
- Ejecución correcta de entradas de teclado simuladas.
- Funcionamiento autónomo sin intervención humana.
- Ciclo percepción–decisión–acción sin bloqueos ni retrasos críticos.
- Métrica de éxito específica: Alcance de un puntaje mayor o igual a 6000 puntos.
- Resultados reproducibles en múltiples ejecuciones bajo condiciones similares.

---

<!--

## 10. Plan de trabajo

---

## 11. Referencias

--->
