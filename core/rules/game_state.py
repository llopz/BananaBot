from itertools import chain

class GameState:

    def __init__(
        self,
        banana_carril=None,
        carriles = None,
        carril_actual = 0,
        Kong = None,
    ):
        self.banana_carril = banana_carril
        if carriles is None:
            carriles = [
                {"suelo": False, "banana_cercana": None, "obstaculo_cercano": None}
                for _ in range(5)
            ]
            carriles[0]["suelo"] = True
        self.carriles = carriles
        self.carril_actual = carril_actual
        self.Kong = Kong
    
    def actualizar(self, kong, bananas, troncos, arbustos, aviones, paredes, plataformas, rocas, aguas, cuevas, totems, tubos):
        
        if not kong:
            return
        
        # Reset
        for carril in self.carriles:
            carril["suelo"] = False
            carril["banana_cercana"] = None
            carril["obstaculo_cercano"] = None

        self.carriles[0]["suelo"] = True

        self.banana_carril = None

        self.Kong = kong[0] if kong else None


        kong_x = kong[0].centro_x
        kong_y = kong[0].centro_y
        
        self.carril_actual = self.obtener_carril(kong_y)

        # Agua
        #for a in aguas:
        #   print(a)
        #if aguas:
         #   if 0 < aguas[0].centro_x - kong_x < 100:
          #          print(aguas[0].centro_x - aguas[0].w / 2 - kong_x)
           #         print(aguas[0].centro_x - kong_x)
            #        self.carriles[0]["suelo"] = False
        
        for a in aguas:
            if 0 < a.centro_x - kong_x < 100:
                print(aguas[a].centro_x - aguas[a].w / 2 - kong_x)
                print(aguas[a].centro_x - kong_x)
                self.carriles[0]["suelo"] = False
                break

        # Plataformas
        for p in plataformas:
            if 0 < p.centro_x - kong_x < 300:
                carril = self.obtener_carril(p.centro_y)
                self.carriles[carril]["suelo"] = True

        # Bananas
        banana_objetivo = None

        for banana in bananas:
            dx = banana.centro_x - kong_x
            dy = banana.centro_y - kong_y
            if 10 < dx < 300:
                carril = self.obtener_carril(banana.centro_y)

                actual = self.carriles[carril]["banana_cercana"]

                if actual is None or banana.centro_x < actual[0].centro_x:
                    self.carriles[carril]["banana_cercana"] = (banana, dx, dy)

                    if banana_objetivo is None or banana.centro_x < banana_objetivo.centro_x:
                        banana_objetivo = (banana, dx, dy)
        
        if banana_objetivo:
            self.banana_carril = self.obtener_carril(banana_objetivo)       

        # Obstaculos
        for obj in chain(troncos, arbustos, aviones, paredes, rocas, cuevas, totems, tubos):
            dx = obj.centro_x - kong_x
            dy = obj.centro_y - kong_y
            if 0 < dx < 300:
                carril = self.obtener_carril(obj.centro_y)

                actual = self.carriles[carril]["obstaculo_cercano"]

                if not actual or dx < actual[1]:
                    self.carriles[carril]["obstaculo_cercano"] = (obj, dx, dy)
        
        
    def obtener_carril(self, y):
        if y > 450: return 0
        if y > 350: return 1
        if y > 250: return 2
        if y > 149: return 3
        return 4
