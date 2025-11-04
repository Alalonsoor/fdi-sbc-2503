"""
Define estructuras de datos:
    Tripleta : sujeto, predicado, objeto
    Regla: tripleta_consecuente <- tripleta_antecedente
    Sustitucion: diccionario
"""
from dataclasses import dataclass, field

def es_variable(term: str) -> bool:
    """Comprueba si un termino es variable, las variables empiezan por ?"""
    return isinstance(term, str) and len(term) > 0 and term[0].isupper()

def es_literal(term: str) -> bool:
    """Comprueba si un termino es literal"""
    return not es_variable(term)

@dataclass
class Tripleta:
    """Una Tripleta es un objeto con 3 terminos: Sujeto, Predicado, Objeto"""
    sujeto: str
    predicado: str
    objeto: str

    def __iter__(self):
        """Permite desempaquetar Tripletas: s, p, v = una tripelta o iterar sobre una tripleta"""
        return iter([self.sujeto, self.predicado, self.objeto])
    
    def terminos(self) -> list[str]:
        """Devuelve una lista con todos los términos"""
        return [self.sujeto, self.predicado, self.objeto]
    
    def aplicar_sustitucion(self, ss: 'Sustitucion') -> 'Tripleta':
        """Dado una Sustitucion ss crea una nueva Tripleta aplicando dicha sustitucion"""
        return Tripleta(
            ss.aplicar(self.sujeto),
            ss.aplicar(self.predicado),
            ss.aplicar(self.objeto)
        )
    
@dataclass
class Regla:
    """Una regla esta formado por consecuente <- antecedente, ambas son tripletas"""
    consecuente: Tripleta
    antecedente: list[Tripleta]

@dataclass
class Sustitucion:
    """Una sustitución es un mapeo de variables -> valor"""
    # field(default_factory=dict) -> cada vez que se crea una instancia se crea un nuevo diccionario vacío.
    mappings : dict[str,str] = field(default_factory=dict)

    def get(self, var: str) -> str | None:
        """Devuelve el valor de una variable var"""
        return self.mappings.get(var)
    
    def add(self, var: str, value: str) -> None:
        self.mappings[var] = value
    
    def aplicar(self, termino:str) -> str:
        """Aplica una sustitución a un término de manera recursiva"""
        if es_variable(termino):
            valor = self.get(termino)
            if valor is not None:
                return self.aplicar(valor)
            return termino
        return termino

    def __contains__(self, var: str) -> bool:
        """Permite hacer directamente 'var in ss', ss una sustitucion"""
        return var in self.mappings

