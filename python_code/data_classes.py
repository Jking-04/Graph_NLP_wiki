from dataclasses import dataclass

@dataclass
class Entity:
    text:str
    compounds:list
    prep_phrases:list[tuple]

@dataclass
class VerbFrame:
    verb: str
    negation:bool
    subjects: list[Entity]
    objects: list[Entity]
    i_objects: list[Entity]
    object_compliments: list[Entity]
    attributes: list[Entity]
    prep_phrases:list[tuple]

    



