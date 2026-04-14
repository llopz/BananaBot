from ..base_detector import BaseDetector, Elemento, ESPACIOS_COLOR
from .banana_detector import BananaDetector
from .tronco_detector import TroncoDetector
from .arbusto_detector import ArbustoDetector
from .avion_detector import AvionDetector
from .kong_detector import KongDetector
from .pared_detector import ParedDetector
from .agua_detector import AguaDetector
from .plataforma_detector import PlataformaDetector
from .plataforma_madera_detector import PlataformaMaderaDetector
from .roca_detector import RocaDetector
from .cueva_detector import CuevaDetector
from .totem_detector import TotemDetector

__all__ = [
    "BaseDetector", "Elemento", "ESPACIOS_COLOR",
    "BananaDetector", "TroncoDetector", "ArbustoDetector", "AvionDetector",
    "KongDetector", "ParedDetector", "AguaDetector", "PlataformaDetector",
    "PlataformaMaderaDetector", "RocaDetector", "CuevaDetector", "TotemDetector"
]