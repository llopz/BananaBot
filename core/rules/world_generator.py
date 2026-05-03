from dataclasses import dataclass
from random import Random
from typing import Dict, List, Optional


LANE_CENTER_Y = {
    0: 500,
    1: 400,
    2: 300,
    3: 200,
    4: 120,
}

OBSTACLE_TYPES = ["tronco", "arbusto", "avion", "pared", "roca", "cueva", "totem", "tubo"]
RESULT_KEYS = [
    "bananas",
    "troncos",
    "arbustos",
    "aviones",
    "kong",
    "paredes",
    "plataformas_madera",
    "rocas",
    "cuevas",
    "totems",
    "tubos",
    "aguas",
    "descartados",
    "mascaras",
]

KEY_BY_OBSTACLE_TYPE = {
    "tronco": "troncos",
    "arbusto": "arbustos",
    "avion": "aviones",
    "pared": "paredes",
    "roca": "rocas",
    "cueva": "cuevas",
    "totem": "totems",
    "tubo": "tubos",
}


@dataclass
class ElementoSintetico:
    x: int
    y: int
    w: int
    h: int
    centro_x: int
    centro_y: int
    area: float
    proporcion: float
    tipo: str


class SyntheticWorldGenerator:
    """Genera escenas sintéticas con una distribución simple de objetos.

    El objetivo no es replicar fielmente el juego, sino producir estados plausibles
    para probar reglas de decisión basadas en posiciones relativas.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        width: int = 960,
        kong_x: int = 220,
    ):
        self.random = Random(seed)
        self.width = int(width)
        self.kong_x = int(kong_x)
        self.kong_lane = 0
        self.step = 0

    def _lane_to_y(self, lane: int) -> int:
        lane = max(0, min(4, int(lane)))
        return LANE_CENTER_Y[lane]

    def _crear_elemento(self, tipo: str, centro_x: int, centro_y: int, w: int, h: int) -> ElementoSintetico:
        x = int(centro_x - w // 2)
        y = int(centro_y - h // 2)
        w = int(max(1, w))
        h = int(max(1, h))
        return ElementoSintetico(
            x=x,
            y=y,
            w=w,
            h=h,
            centro_x=int(centro_x),
            centro_y=int(centro_y),
            area=float(w * h),
            proporcion=round(float(w) / float(h), 2) if h else 0.0,
            tipo=tipo,
        )

    def _base_resultados(self) -> Dict[str, list]:
        resultados = {k: [] for k in RESULT_KEYS}
        resultados["mascaras"] = {}
        return resultados

    def _avanzar_kong(self) -> None:
        salto_carril = self.random.choices([-1, 0, 1], weights=[0.12, 0.70, 0.18], k=1)[0]
        self.kong_lane = max(0, min(4, self.kong_lane + salto_carril))

    def _spawnear_agua(self, resultados: Dict[str, list]) -> None:
        if self.kong_lane != 0:
            return
        if self.random.random() > 0.16:
            return

        w = self.random.randint(130, 220)
        x = self.kong_x + self.random.randint(40, 120)
        y = self._lane_to_y(0) + 22
        resultados["aguas"].append(self._crear_elemento("agua", x, y, w, 38))

    def _spawnear_plataformas(self, resultados: Dict[str, list]) -> None:
        for lane in range(1, 5):
            if self.random.random() > 0.22:
                continue
            x = self.kong_x + self.random.randint(70, 250)
            y = self._lane_to_y(lane) + 24
            w = self.random.randint(120, 200)
            resultados["plataformas_madera"].append(
                self._crear_elemento("plataforma_madera", x, y, w, 28)
            )

        # Escenario útil para activar reglas de salto por plataforma.
        if self.kong_lane < 4 and self.random.random() < 0.35:
            lane_up = self.kong_lane + 1
            x = self.kong_x + self.random.randint(80, 140)
            y = self._lane_to_y(lane_up) + 20
            resultados["plataformas_madera"].append(
                self._crear_elemento("plataforma_madera", x, y, 165, 28)
            )

    def _spawnear_bananas(self, resultados: Dict[str, list]) -> None:
        if self.random.random() > 0.50:
            return

        if self.kong_lane < 4 and self.random.random() < 0.75:
            lane = self.kong_lane + 1
        else:
            lane = self.kong_lane

        base_x = self.kong_x + self.random.randint(70, 180)
        count = self.random.randint(1, 3)
        for i in range(count):
            x = base_x + i * self.random.randint(20, 36)
            y = self._lane_to_y(lane) + self.random.randint(-8, 8)
            resultados["bananas"].append(self._crear_elemento("banana", x, y, 24, 24))

    def _spawnear_obstaculos(self, resultados: Dict[str, list]) -> None:
        if self.random.random() > 0.65:
            return

        lane = self.kong_lane if self.random.random() < 0.75 else self.random.randint(0, 4)
        tipo = self.random.choice(OBSTACLE_TYPES)
        salida = KEY_BY_OBSTACLE_TYPE[tipo]

        if self.random.random() < 0.60:
            dx = self.random.randint(60, 220)
        else:
            dx = self.random.randint(221, 390)

        x = min(self.width - 20, self.kong_x + dx)
        y = self._lane_to_y(lane) + self.random.randint(-10, 10)

        w = self.random.randint(40, 78)
        h = self.random.randint(36, 88)
        resultados[salida].append(self._crear_elemento(tipo, x, y, w, h))

    def generate_frame(self) -> Dict[str, list]:
        self.step += 1
        self._avanzar_kong()

        resultados = self._base_resultados()
        kong_y = self._lane_to_y(self.kong_lane)
        resultados["kong"].append(self._crear_elemento("kong", self.kong_x, kong_y, 72, 92))

        self._spawnear_agua(resultados)
        self._spawnear_plataformas(resultados)
        self._spawnear_bananas(resultados)
        self._spawnear_obstaculos(resultados)

        return resultados