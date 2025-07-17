# closet.py

class Prenda:
    def __init__(self, nombre, tipo, color, temporada, estado, ocasion):
        self.nombre = nombre
        self.tipo = tipo
        self.color = color
        self.temporada = temporada
        self.estado = estado
        self.ocasion = ocasion

    def esta_disponible(self):
        return self.estado.lower() == "limpio"

    def es_apropiada_para(self, clima, ocasion):
        return self.temporada.lower() == clima and self.ocasion.lower() == ocasion.lower()

    def __str__(self):
        return f"{self.nombre} ({self.tipo}, {self.color}, {self.temporada}, {self.ocasion}, {self.estado})"

    def __repr__(self):
        return self.__str__()


class Closet:
    def __init__(self, prendas):
        self.prendas = prendas

    def filtrar_disponibles(self, clima, ocasion):
        return [p for p in self.prendas if p.esta_disponible() and p.es_apropiada_para(clima, ocasion)]

    def sugerir_outfit(self, clima, ocasion):
        import random
        disponibles = self.filtrar_disponibles(clima, ocasion)

        superiores = [p for p in disponibles if p.tipo == 'polera']
        inferiores = [p for p in disponibles if p.tipo in ['short', 'pantalonlargo', 'falda']]
        capas = [p for p in disponibles if p.tipo == 'abrigo']
        one_piece = [p for p in disponibles if p.tipo == 'vestido']

        if superiores and inferiores:
            outfit = {"superior": random.choice(superiores),
                      "inferior": random.choice(inferiores)}
            if one_piece:
                outfit2 = {"superior": random.choice(one_piece)}
                if random.randint(0, 1) == 1:
                    outfit = outfit2

            if capas:
                outfit["capa"] = random.choice(capas)

            return outfit
        else:
            return None