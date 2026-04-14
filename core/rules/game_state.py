class GameState:

    def __init__(
        self,
        obstacle_ahead=False,
        obstacle_distance=None,
        banana=False,
        banana_distance=None,
        superficie=[True, False, False, False],
    ):
        self.obstacle_ahead = obstacle_ahead
        self.obstacle_distance = obstacle_distance
        self.banana = banana
        self.banana_distance = banana_distance
        self.superficie = [True, False, False, False]
    
    def actualizar(self, kong, bananas, troncos, arbustos, aviones, paredes, plataformas, rocas, aguas):
        bananas_relevantes = []
        banana_objetivo = None
        banana_objetivo_distance = None
        objects_relevantes = []
        nearest_object = None
        nearest_object_distance = None
        plataformas_relevantes = []
        self.superficie = [True, False, False, False]

        if kong:
            kong_x = kong[0].centro_x
            kong_y = kong[0].centro_y

            # BANANAS
            if bananas:
                for banana in bananas:
                    dx = banana.centro_x - kong_x
                    if 0 < dx < 200:
                        bananas_relevantes.append(banana)

            if bananas_relevantes:
                banana_objetivo = min(bananas_relevantes, key=lambda b: b.centro_x)
                banana_objetivo_distance = [
                    banana_objetivo.centro_x - kong_x,
                    banana_objetivo.centro_y - kong_y,
                ]

            # OBJETOS
            objects = troncos + arbustos + aviones + paredes + rocas
            if objects:
                objects_relevantes = [
                    obj for obj in objects
                    if 0 < obj.centro_x - kong_x < 200
                ]

            if objects_relevantes:
                nearest_object = min(objects_relevantes, key=lambda o: o.centro_x)
                nearest_object_distance = [
                    nearest_object.centro_x - kong_x,
                    nearest_object.centro_y - kong_y,
                ]
            
            # AGUA
            agua = [
                a for a in aguas
                if kong and 0 < a.centro_x - kong_x < 200
            ]

            if agua:
                self.superficie[0] = False

            # PLATAFORMAS            
            plataformas_relevantes = [
                p for p in plataformas
                if kong and 0 < p.centro_x - kong_x < 200
            ]

            for p in plataformas_relevantes:
                
                if p.centro_y > 250:
                    nivel = 1  # plataforma baja
                elif 0 < p.centro_y <= 50:
                    nivel = 2  # media
                elif -50 < p.centro_y <= 0:
                    nivel = 3  # alta
                else:
                    nivel = None

                if nivel is not None:
                    self.superficie[nivel] = True
            
            if plataformas_relevantes:
                print(
                    f"nearest_object_distance: {plataformas[0]}"
                )

        # 🔹 Aquí sí usas self
        self.obstacle = nearest_object
        self.obstacle_distance = nearest_object_distance
        self.banana = banana_objetivo is not None
        self.banana_distance = banana_objetivo_distance
