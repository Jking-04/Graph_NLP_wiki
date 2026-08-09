from dataclasses import dataclass

@dataclass
class Entity:
    text:str
    id:int

    compounds:list
    adjectives:list
    numbers:list
    determiners:list

    prep_phrases:list[tuple]

    def node_name(self):
        parts = []

        parts.extend(self.adjectives)
        parts.extend(self.compounds)
        parts.extend(self.numbers)
        parts.append(self.text)

        return " ".join(parts)

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

    



