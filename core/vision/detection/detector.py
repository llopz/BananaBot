from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Callable, List, Tuple
from .base_detector import Elemento
from .detectors import (
    BananaDetector, TroncoDetector, ArbustoDetector, AvionDetector,
    KongDetector, ParedDetector, AguaDetector,
    PlataformaMaderaDetector, RocaDetector, CuevaDetector, BarraPotenciadoraDetector, GameOverDetector, TotemDetector, TuboDetector
)


class Detector:

    def __init__(self, config):
        self.config = config
        self._registry: Dict[str, Callable] = {}
        workers = int(getattr(self.config, "DETECTORES_WORKERS", 2))
        self._executor = ThreadPoolExecutor(max_workers=max(1, workers))
        self._registrar_detectores()


    def _registrar_detectores(self):
        """Registra todos los detectores."""
        self._registrar("bananas",     BananaDetector(self.config).detectar)
        self._registrar("troncos",     TroncoDetector(self.config).detectar)
        self._registrar("arbustos",    ArbustoDetector(self.config).detectar)
        self._registrar("aviones",     AvionDetector(self.config).detectar)
        self._registrar("kong",        KongDetector(self.config).detectar)
        self._registrar("paredes",     ParedDetector(self.config).detectar)
        self._registrar("aguas",       AguaDetector(self.config).detectar)
        self._registrar("plataformas_madera", PlataformaMaderaDetector(self.config).detectar)
        self._registrar("rocas",       RocaDetector(self.config).detectar)
        self._registrar("cuevas",      CuevaDetector(self.config).detectar)
        self._registrar("barras_potenciadoras", BarraPotenciadoraDetector(self.config).detectar)
        self._registrar("game_over",   GameOverDetector(self.config).detectar)
        self._registrar("totems",      TotemDetector(self.config).detectar)
        self._registrar("tubos",       TuboDetector(self.config).detectar)

    def _registrar(self, nombre: str, metodo: Callable):
        self._registry[nombre] = metodo

    def _ejecutar_grupo(self, grupo: List[Tuple[str, Callable]], frame):
        resultados = {}
        descartados = []
        mascaras = {}

        for nombre, detector_func in grupo:
            elementos, descartados_local, mascara = detector_func(frame)

            resultados[nombre] = elementos
            descartados.extend(descartados_local)
            mascaras[nombre] = mascara

        return resultados, descartados, mascaras

    def _aplicar_filtro_x_minimo(self, resultados: Dict[str, List[Elemento]]):
        x_min = int(getattr(self.config, "DETECCION_X_MIN", 160))
        excluidos = {"kong", "barras_potenciadoras", "aguas", "plataformas_madera"}

        for nombre, elementos in resultados.items():
            if nombre in excluidos:
                continue
            resultados[nombre] = [e for e in elementos if int(e.x) >= x_min]

    # ====================== DETECTAR TODOS  ======================
    def detectar_todos(self, frame) -> dict:
        items = list(self._registry.items())
        mitad = (len(items) + 1) // 2
        grupo_1 = items[:mitad]
        grupo_2 = items[mitad:]

        resultados = {}
        todos_descartados = []
        mascaras = {}

        if grupo_2:
            f1 = self._executor.submit(self._ejecutar_grupo, grupo_1, frame)
            f2 = self._executor.submit(self._ejecutar_grupo, grupo_2, frame)

            res_1, desc_1, mas_1 = f1.result()
            res_2, desc_2, mas_2 = f2.result()

            resultados.update(res_1)
            resultados.update(res_2)
            todos_descartados.extend(desc_1)
            todos_descartados.extend(desc_2)
            mascaras.update(mas_1)
            mascaras.update(mas_2)
        else:
            res_1, desc_1, mas_1 = self._ejecutar_grupo(grupo_1, frame)
            resultados.update(res_1)
            todos_descartados.extend(desc_1)
            mascaras.update(mas_1)

        self._aplicar_filtro_x_minimo(resultados)

        return {
            "bananas":     resultados.get("bananas", []),
            "troncos":     resultados.get("troncos", []),
            "arbustos":    resultados.get("arbustos", []),
            "aviones":     resultados.get("aviones", []),
            "kong":        resultados.get("kong", []),
            "paredes":     resultados.get("paredes", []),
            "aguas":       resultados.get("aguas", []),
            "plataformas_madera": resultados.get("plataformas_madera", []),
            "rocas":       resultados.get("rocas", []),
            "cuevas":      resultados.get("cuevas", []),
            "barras_potenciadoras": resultados.get("barras_potenciadoras", []),
            "game_over":   resultados.get("game_over", []),
            "totems":      resultados.get("totems", []),
            "tubos":       resultados.get("tubos", []),
            "descartados": todos_descartados,
            "mascaras": mascaras
        }