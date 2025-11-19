import random
from typing import List, Tuple, Optional
from .models import Person, Gender, PersonType

class Simulation:
    def __init__(self, initial_ordinary: int = 100, initial_bio: int = 100):
        self.population: List[Person] = []
        self.year = 0
        self.history = []  # List of dicts with stats
        
        # Initialize population
        # Assuming initial population is newborn? Or mixed ages?
        # Prompt says "Initial quantity is 100". Let's assume they are newborns for simplicity, 
        # or maybe spread out? 
        # If they are newborns, no one reproduces for 20 years.
        # Let's assume they are newborns to start clean.
        
        for _ in range(initial_ordinary):
            self.population.append(Person(
                gender=random.choice(list(Gender)),
                person_type=PersonType.ORDINARY,
                age=0
            ))
            
        for _ in range(initial_bio):
            self.population.append(Person(
                gender=random.choice(list(Gender)),
                person_type=PersonType.BIO,
                age=0
            ))

    def run(self, years: int):
        for _ in range(years):
            self.step()

    def step(self):
        self.year += 1
        
        # 1. Aging and Death
        self._handle_aging()
        
        # 2. Reproduction
        newborns = self._handle_reproduction()
        self.population.extend(newborns)
        
        # 3. Stats
        self._collect_stats()

    def _handle_aging(self):
        # Age up everyone
        for p in self.population:
            p.age_up()
            
        # Remove dead people
        self.population = [p for p in self.population if p.is_alive]

    def _handle_reproduction(self) -> List[Person]:
        # Filter eligible parents: Age 20
        eligible_males = [p for p in self.population if p.age == 20 and p.gender == Gender.MALE]
        eligible_females = [p for p in self.population if p.age == 20 and p.gender == Gender.FEMALE]
        
        random.shuffle(eligible_males)
        random.shuffle(eligible_females)
        
        # Pair up
        pairs = []
        min_len = min(len(eligible_males), len(eligible_females))
        for i in range(min_len):
            pairs.append((eligible_males[i], eligible_females[i]))
            
        newborns = []
        for father, mother in pairs:
            children = self._breed(father, mother)
            newborns.extend(children)
            
        return newborns

    def _breed(self, father: Person, mother: Person) -> List[Person]:
        # Rule 2:
        # Ord M + Ord F -> Ord
        # Ord M + Bio F -> Bio
        # Bio M + Bio F -> Bio
        # Bio M + Ord F -> None
        
        child_type = None
        
        if father.person_type == PersonType.ORDINARY and mother.person_type == PersonType.ORDINARY:
            child_type = PersonType.ORDINARY
        elif father.person_type == PersonType.ORDINARY and mother.person_type == PersonType.BIO:
            child_type = PersonType.BIO
        elif father.person_type == PersonType.BIO and mother.person_type == PersonType.BIO:
            child_type = PersonType.BIO
        elif father.person_type == PersonType.BIO and mother.person_type == PersonType.ORDINARY:
            return [] # Infertility
            
        # Produce 2 children
        children = []
        for _ in range(2):
            children.append(Person(
                gender=random.choice(list(Gender)),
                person_type=child_type,
                age=0
            ))
            
        return children

    def _collect_stats(self):
        ord_count = sum(1 for p in self.population if p.person_type == PersonType.ORDINARY)
        bio_count = sum(1 for p in self.population if p.person_type == PersonType.BIO)
        total = len(self.population)
        
        self.history.append({
            "year": self.year,
            "ordinary": ord_count,
            "bio": bio_count,
            "total": total
        })
