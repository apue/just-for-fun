from enum import Enum, auto
from dataclasses import dataclass

class Gender(Enum):
    MALE = auto()
    FEMALE = auto()

class PersonType(Enum):
    ORDINARY = auto()
    BIO = auto()

@dataclass
class Person:
    gender: Gender
    person_type: PersonType
    age: int = 0
    is_alive: bool = True

    def age_up(self):
        if not self.is_alive:
            return
        self.age += 1
        if self.age >= 80:
            self.die()

    def die(self):
        self.is_alive = False
