"""
Define estructuras de datos:
    Tripleta : sujeto, predicado, objeto
    Regla: tripleta_consecuente <- tripleta_antecedente
    Sustitucion: diccionario
"""

from dataclasses import dataclass, field


def es_variable(term: str) -> bool:
    """Comprueba si un termino es variable, las variables empiezan por letra mayuscula"""
    return isinstance(term, str) and len(term) > 0 and term[0].isupper()


def es_literal(term: str) -> bool:
    """Comprueba si un termino es literal"""
    return not es_variable(term)


@dataclass(eq=False)
class Tripleta:
    """Una Tripleta es un objeto con 3 terminos: Sujeto, Predicado, Objeto"""

    sujeto: str
    predicado: str
    objeto: str
    confianza: float = 1.0  # Nivel de confianza (lógica difusa), por defecto 100%

    def __eq__(self, other):
        """Compara solo S, P, O (ignora confianza para evitar duplicados)"""
        if not isinstance(other, Tripleta):
            return False
        return (self.sujeto == other.sujeto and 
                self.predicado == other.predicado and 
                self.objeto == other.objeto)
    
    def __hash__(self):
        """Hash basado solo en S, P, O para usar en conjuntos y diccionarios"""
        return hash((self.sujeto, self.predicado, self.objeto))

    def __iter__(self):
        """Permite desempaquetar Tripletas: s, p, v = una tripelta o iterar sobre una tripleta"""
        return iter([self.sujeto, self.predicado, self.objeto])

    def terminos(self) -> list[str]:
        """Devuelve una lista con todos los términos"""
        return [self.sujeto, self.predicado, self.objeto]

    def aplicar_sustitucion(self, ss: "Sustitucion") -> "Tripleta":
        """Dado una Sustitucion ss crea una nueva Tripleta aplicando dicha sustitucion"""
        return Tripleta(
            ss.aplicar(self.sujeto),
            ss.aplicar(self.predicado),
            ss.aplicar(self.objeto),
            self.confianza,  # Mantener la confianza
        )

    def get_confianza(self):
        """Devuelve eñ valor de la confianza"""
        return self.confianza


@dataclass
class Regla:
    """Una regla esta formado por consecuente <- lista[antecedente], ambas son tripletas"""

    consecuente: Tripleta
    antecedentes: list[Tripleta]
    confianza: float = 1.0  # Nivel de confianza de la regla, por defecto 100%

    def get_consecuente(self) -> Tripleta:
        return self.consecuente

    def get_antecedentes(self) -> list[Tripleta]:
        return self.antecedentes


@dataclass
class Sustitucion:
    """Una sustitución es un mapeo de variables -> valor"""

    # field(default_factory=dict) -> cada vez que se crea una instancia se crea un nuevo diccionario vacío.
    mappings: dict[str, str] = field(default_factory=dict)

    def get_mappings(self) -> dict[str, str]:
        """
        Devuelve en mapeo de las sustituciones
        """
        return self.mappings

    def get(self, var: str) -> str | None:
        """Devuelve el valor de una variable var"""
        return self.mappings.get(var)

    def add(self, var: str, value: str) -> None:
        self.mappings[var] = value

    def aplicar(self, termino: str, visitados: set[str] | None = None) -> str:
        """Aplica una sustitución a un término de manera recursiva
        
        Parámetros: 
        - termino: variable o término que se quiera sustituir.
        - visitados: conjunto para detectar ciclos infinitos.

        """
        # Crea un conjunto vacío para rastrear variables ya visitadas.
        if visitados is None:
            visitados = set()

        # Caso recursivo:

        # Procesamiento de variables
        if es_variable(termino):
            # 1. Detección ciclos: Si ya visitamos esta variable, paramos para evitar recursión infinita del tipo {x: x} o {x: y, y: x}
            if termino in visitados:
                return termino
            # 2. Búsqueda de sustitución: 
            valor = self.get(termino) # Busca en el diccionario de sustituciones
            if valor is not None: # Existe sustitución
                # Marcamos el término como visitado
                visitados.add(termino)
                # Aplica recursivamente la sustitución al valor encontrado
                return self.aplicar(valor, visitados)
            # 3. Si la variable no tiene sustitución definida, la devuelve tal cual.
            return termino
        
        # Caso base: Si el término no es una variable (es un valor constante), lo devuelve tal cual.
        return termino

    def __contains__(self, var: str) -> bool:
        """Permite hacer directamente 'var in ss', ss una sustitucion"""
        return var in self.mappings
