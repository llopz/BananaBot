# Informe de Instalacion

## 1. Descripcion general de la solucion

El proyecto implementa un bot autonomo para Banana Kong que funciona por vision por computador y reglas predefinidas. El flujo general es:

Captura de pantalla -> Deteccion de elementos -> Construccion de estado -> Decision por reglas -> Ejecucion de accion

La ejecucion se realiza en entorno local sobre un emulador Android (MuMu Player), sin acceso interno al juego.

### 1.1 Lenguajes y tecnologias utilizadas

- Python 3.13
- OpenCV
- numpy
- mss
- pygetwindow
- pyautogui
- keyboard
- MuMu Player (emulador Android)

### 1.2 Componentes de la solucion

- `core/main.py`: orquestador del ciclo principal.
- `core/vision/captura/captura.py`: captura del frame desde la ventana del emulador.
- `core/vision/detection/`: detectores por color y template matching.
- `core/rules/`: estado del juego y motor de reglas por prioridad.
- `core/control/acciones_click.py`: ejecucion de acciones en el emulador.
- `core/vision/visualizador/visualizador.py`: depuracion visual en tiempo real.
- `core/config/settings.py`: configuracion centralizada.

## 2. Requisitos previos

### 2.1 Software requerido

- Windows 10/11 (64-bit).
- Python 3.13 instalado y disponible en terminal.
- MuMu Player instalado.
- Banana Kong instalado en MuMu.

Recomendacion para facilitar instalacion del juego:

- Usar un APK local de Banana Kong para instalarlo directamente en MuMu 

### 2.2 Variables de entorno

Este proyecto no requiere variables de entorno obligatorias para correr en desarrollo local.

La configuracion operativa se maneja en `core/config/settings.py`.

## 3. Instalacion para ambiente de desarrollo

### 3.1 Desarrollo sin contenedores

#### 3.1.1 Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd banana_kong_bot
```

#### 3.1.2 Instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.1.3 Configurar variables de entorno

No aplica para este proyecto.

Ajustar configuracion en `core/config/settings.py`, especialmente:

- `EMULADOR_TITULO` (por defecto: `Android Device`).
- `EJECUTAR_ACCIONES` (recomendado `False` en primeras pruebas).
- Parametros de deteccion y debug segun escenario.

#### 3.1.4 Ejecutar servicios requeridos

No hay servicios externos (BD, cola, API) requeridos.

Solo se necesita:

- MuMu abierto.
- Banana Kong instalado y ejecutandose.
- Ventana del emulador visible y no minimizada.

Instalacion del APK en MuMu (recomendado):

1. Abrir MuMu.
2. Arrastrar `BananaKong.apk` a la ventana del emulador, o usar la opcion de instalar APK.
3. Esperar a que termine la instalacion y abrir el juego.

#### 3.1.5 Iniciar la aplicacion

Opcion recomendada con script:

```powershell
.\start_bot.ps1
```

Opcional (precalentar imports):

```powershell
.\start_bot.ps1 -Warmup
```

Ejecucion directa:

```powershell
.\.venv\Scripts\python.exe core\main.py
```

## 4. Verificacion de funcionamiento

Checklist minimo:

- El script inicia sin errores de import.
- Se abre la ventana de visualizacion del bot.
- Se detecta la ventana del emulador correctamente.
- Se dibujan detecciones en pantalla.
- Las teclas de control responden: SPACE, P, Q.
- Con `EJECUTAR_ACCIONES = False`, no se envian acciones reales.
- Con `EJECUTAR_ACCIONES = True`, el bot ejecuta acciones segun reglas.

## 5. Solucion de problemas frecuentes

- Error: no se encontro ventana del emulador.
  - Verificar `EMULADOR_TITULO` en `settings.py`.
  - Verificar que MuMu no este minimizado.

- Error: no se encontro `.venv` al ejecutar `start_bot.ps1`.
  - Crear entorno virtual e instalar dependencias.

- Deteccion inestable o pobre.
  - Ajustar HSV con `core/utils/ajuste_hsv.py`.
  - Revisar resolucion y brillo del emulador.

- No se ejecutan acciones.
  - Confirmar `EJECUTAR_ACCIONES = True`.
  - Verificar foco y permisos de control del sistema.

- El juego no esta instalado en MuMu.
  - Instalar desde APK local para acelerar puesta en marcha.

## 6. Mantenimiento y actualizacion

Recomendaciones:

- Mantener `requirements.txt` sincronizado con cambios reales.
- Versionar cambios de `settings.py` por escenario (resolucion/perfil).
- Validar en modo observacion antes de habilitar acciones.
- Mantener una copia local del APK usado para instalacion reproducible.
- Documentar cambios de reglas y umbrales en cada iteracion.

Flujo recomendado para actualizar version local:

1. Actualizar repositorio (`git pull`).
2. Reinstalar dependencias (`pip install -r requirements.txt`).
3. Ejecutar en modo observacion (`EJECUTAR_ACCIONES = False`).
4. Validar deteccion/reglas y luego habilitar acciones reales.


