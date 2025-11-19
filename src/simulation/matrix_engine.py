import numpy as np
from typing import List, Dict
from .models import Gender, PersonType

class MatrixSimulation:
    def __init__(self, initial_ordinary: int = 100, initial_bio: int = 100):
        self.year = 0
        self.history = []
        
        # Population Tensor: [Age, Gender, Type]
        # Age: 0-80 (81 buckets)
        # Gender: 0=Male, 1=Female
        # Type: 0=Ordinary, 1=Bio
        self.population = np.zeros((81, 2, 2), dtype=np.float64)
        
        # Initialize population (assuming newborns for consistency with Agent model)
        # Ordinary: Type 0
        # Bio: Type 1
        
        # Split initial population evenly between genders
        self.population[0, 0, 0] = initial_ordinary / 2  # Male Ordinary
        self.population[0, 1, 0] = initial_ordinary / 2  # Female Ordinary
        
        self.population[0, 0, 1] = initial_bio / 2       # Male Bio
        self.population[0, 1, 1] = initial_bio / 2       # Female Bio

    def run(self, years: int):
        for _ in range(years):
            self.step()

    def step(self):
        self.year += 1
        
        # 1. Reproduction (before aging, using current 20-year-olds)
        newborns = self._calculate_newborns()
        
        # 2. Aging
        # Shift population array along Age axis (axis 0)
        # People at index i move to i+1
        # People at index 80 move out (die)
        self.population = np.roll(self.population, 1, axis=0)
        
        # 3. Births
        # Place newborns at Age 0
        # newborns is [Gender, Type]
        self.population[0] = newborns
        
        # 4. Stats
        self._collect_stats()

    def _calculate_newborns(self) -> np.ndarray:
        # Get 20-year-olds
        # Shape: [Gender, Type]
        cohort_20 = self.population[20]
        
        m_ord = cohort_20[0, 0]
        m_bio = cohort_20[0, 1]
        f_ord = cohort_20[1, 0]
        f_bio = cohort_20[1, 1]
        
        total_females = f_ord + f_bio
        
        if total_females == 0:
            return np.zeros((2, 2))
            
        # Probabilities of a male pairing with a specific female type
        # Assuming random pairing: P(Partner is F_type) = Count(F_type) / Total_F
        p_f_ord = f_ord / total_females
        p_f_bio = f_bio / total_females
        
        # Calculate expected offspring
        # Each couple produces 2 children (1 Male, 1 Female)
        # So total children = Total Couples * 2
        # Total Couples = min(Total Males, Total Females)? 
        # In the Agent model, we paired up min(len(males), len(females)).
        # Here we need to replicate that logic.
        
        total_males = m_ord + m_bio
        total_couples = min(total_males, total_females)
        
        if total_couples == 0:
            return np.zeros((2, 2))
            
        # We need to know how many of these couples involve M_ord vs M_bio
        # Assuming random selection of males too:
        # Count(M_ord in couples) = Total_Couples * (M_ord / Total_M)
        
        m_ord_active = total_couples * (m_ord / total_males)
        m_bio_active = total_couples * (m_bio / total_males)
        
        # Now apply breeding rules to active males
        # 1. M_ord + F_ord -> Ordinary
        # 2. M_ord + F_bio -> Bio
        # 3. M_bio + F_bio -> Bio
        # 4. M_bio + F_ord -> None
        
        # Offspring counts (Total, not per gender yet)
        # Rule 1: M_ord * P(F_ord)
        offspring_ord_from_1 = m_ord_active * p_f_ord * 2
        
        # Rule 2: M_ord * P(F_bio)
        offspring_bio_from_2 = m_ord_active * p_f_bio * 2
        
        # Rule 3: M_bio * P(F_bio)
        offspring_bio_from_3 = m_bio_active * p_f_bio * 2
        
        # Rule 4: M_bio * P(F_ord) -> 0
        
        total_new_ord = offspring_ord_from_1
        total_new_bio = offspring_bio_from_2 + offspring_bio_from_3
        
        # Split by gender (50/50)
        newborns = np.zeros((2, 2))
        
        # Male Ordinary
        newborns[0, 0] = total_new_ord / 2
        # Female Ordinary
        newborns[1, 0] = total_new_ord / 2
        
        # Male Bio
        newborns[0, 1] = total_new_bio / 2
        # Female Bio
        newborns[1, 1] = total_new_bio / 2
        
        return newborns

    def _collect_stats(self):
        # Sum across Age and Gender axes to get total per Type
        # Axis 0 = Age, Axis 1 = Gender, Axis 2 = Type
        # Sum over 0 and 1 -> [Type]
        totals = np.sum(self.population, axis=(0, 1))
        
        ord_count = int(totals[0])
        bio_count = int(totals[1])
        total = ord_count + bio_count
        
        self.history.append({
            "year": self.year,
            "ordinary": ord_count,
            "bio": bio_count,
            "total": total
        })
