from typing import Dict, Callable
from .base_detector import BaseDetector, Elemento
from .detectors import (
    BananaDetector, TroncoDetector, ArbustoDetector, AvionDetector,
    KongDetector, ParedDetector, AguaDetector, PlataformaDetector,
    PlataformaMaderaDetector, RocaDetector
)


class Detector:

    def __init__(self, config):
        self.config = config
        self._registry: Dict[str, Callable] = {}
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
        self._registrar("plataformas", PlataformaDetector(self.config).detectar)
        self._registrar("plataformas_madera", PlataformaMaderaDetector(self.config).detectar)
        self._registrar("rocas",       RocaDetector(self.config).detectar)

    def _registrar(self, nombre: str, metodo: Callable):
        self._registry[nombre] = metodo

    # ====================== DETECTAR TODOS  ======================
    def detectar_todos(self, frame) -> dict:

        resultados = {}
        todos_descartados = []
        mascaras = {}

        for nombre, detector_func in self._registry.items():
            elementos, descartados, mascara = detector_func(frame)
            
            resultados[nombre] = elementos
            todos_descartados.extend(descartados)
            mascaras[nombre] = mascara

        return {
            "bananas":     resultados.get("bananas", []),
            "troncos":     resultados.get("troncos", []),
            "arbustos":    resultados.get("arbustos", []),
            "aviones":     resultados.get("aviones", []),
            "kong":        resultados.get("kong", []),
            "paredes":     resultados.get("paredes", []),
            "aguas":       resultados.get("aguas", []),
            "plataformas": resultados.get("plataformas", []),
            "rocas":       resultados.get("rocas", []),
            "descartados": todos_descartados,
            "mascaras": mascaras
        }