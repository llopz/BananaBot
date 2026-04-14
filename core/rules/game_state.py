class GameState:

    def __init__(
        self,
        banana=False,
        banana_carril=None,
        carriles = [{'suelo': True, 'banana_cercana': None, 'obstaculo_cercano': None}, {'suelo': False, 'banana_cercana': None, 'obstaculo_cercano': None}, {'suelo': False, 'banana_cercana': None, 'obstaculo_cercano': None}, {'suelo': False, 'banana_cercana': None, 'obstaculo_cercano': None}, {'suelo': False, 'banana_cercana': None, 'obstaculo_cercano': None}],
        carril_actual = 0
    ):
        self.banana = banana
        self.banana_carril = banana_carril
        self.carriles = carriles
        self.carril_actual = carril_actual
    
    def actualizar(self, kong, bananas, troncos, arbustos, aviones, paredes, plataformas, rocas, aguas, cuevas, totems, tubos):
        
        # Reset carriles
        self.carriles = [
            {"suelo": False, "banana_cercana": None, "obstaculo_cercano": None}
            for _ in range(5)
        ]

        self.banana = None
        self.banana_carril = None
        banana_objetivo = None
        banana_obj_carril = None

        if not kong:
            return

        kong_x = kong[0].centro_x
        kong_y = kong[0].centro_y

        # 🔹 Inicialmente el suelo base existe
        self.carriles[0]["suelo"] = True

        # 🔹 AGUA (quita suelo base)
        for a in aguas:
            if 0 < a.centro_x - kong_x < 200:
                self.carriles[0]["suelo"] = False

        # 🔹 PLATAFORMAS (activan suelo en carriles altos)
        for p in plataformas:
            if 0 < p.centro_x - kong_x < 200:
                carril = self.obtener_carril(p.centro_y)
                self.carriles[carril]["suelo"] = True

        # 🔹 BANANAS POR CARRIL
        for banana in bananas:
            dx = banana.centro_x - kong_x
            dy = banana.centro_y - kong_y
            if 0 < dx < 200:
                carril = self.obtener_carril(banana.centro_y)

                actual = self.carriles[carril]["banana_cercana"]

                if actual is None or banana.centro_x < actual[0].centro_x:
                    self.carriles[carril]["banana_cercana"] = (banana, dx, dy)

        for carril in range(1, 5):
            bc = self.carriles[carril]["banana_cercana"]
            if bc is not None:
                if banana_objetivo is None or bc[0].centro_x < banana_objetivo[0].centro_x:
                    banana_objetivo = bc
                    banana_obj_carril = carril

        # 🔹 OBSTÁCULOS POR CARRIL
        objetos = troncos + arbustos + aviones + paredes + rocas + cuevas + totems + tubos

        for obj in objetos:
            dx = obj.centro_x - kong_x
            dy = obj.centro_y - kong_y
            if 0 < dx < 300:
                carril = self.obtener_carril(obj.centro_y)

                actual = self.carriles[carril]["obstaculo_cercano"]

                if actual is None or obj.centro_x < actual[0].centro_x:
                    self.carriles[carril]["obstaculo_cercano"] = (obj, dx, dy)

        # 🔹 Carril actual del kong
        self.carril_actual = self.obtener_carril(kong_y)
        self.banana = banana_objetivo is not None
        self.banana_carril = banana_obj_carril

    def obtener_carril(self, y):
        if 149 < y < 240:
            return 1
        elif 247 < y < 340:
            return 2
        elif 345 < y <= 440:
            return 3
        elif 448 < y:
            return 4
        else:
            return 0  # suelo base
