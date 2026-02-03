from typing import List, Optional

class PetType:
    def __init__(self, id: str, type: str, family: str, genus: str, 
                 attributes: List[str], lifespan: Optional[int]):
        self.id = id
        self.type = type
        self.family = family
        self.genus = genus
        self.attributes = attributes
        self.lifespan = lifespan
        self.pets = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "family": self.family,
            "genus": self.genus,
            "attributes": self.attributes,
            "lifespan": self.lifespan,
            "pets": self.pets
        }

class Pet:
    def __init__(self, name: str, birthdate: str = "NA", picture: str = "NA"):
        self.name = name
        self.birthdate = birthdate
        self.picture = picture
    
    def to_dict(self):
        return {
            "name": self.name,
            "birthdate": self.birthdate,
            "picture": self.picture
        }
