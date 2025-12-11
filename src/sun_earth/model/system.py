
import numpy as np
from ..config import G

class SolarSystem:
    def __init__(self, bodies=None):
        self.bodies = bodies if bodies else []

    def add_body(self, body):
        self.bodies.append(body)

    def compute_forces(self):
        """
        Compute gravitational forces on all bodies.
        Currently optimized for Sun-Earth (Sun fixed at origin, Earth moves).
        For a general N-body, we would iterate all pairs.
        """
        # Reset accelerations
        for body in self.bodies:
            body.acceleration = np.zeros(2, dtype=float)

        # Basic N-body (O(N^2)) - fine for small N
        for i, body1 in enumerate(self.bodies):
            for j, body2 in enumerate(self.bodies):
                if i == j:
                    continue
                
                # Vector from body1 to body2
                r_vec = body2.position - body1.position
                r_mag = np.linalg.norm(r_vec)
                
                if r_mag == 0:
                    continue
                
                # F = G * m1 * m2 / r^2
                # a1 = F / m1 = G * m2 / r^2 * (r_vec / r)
                # a1 = G * m2 * r_vec / r^3
                
                acc = G * body2.mass * r_vec / (r_mag**3)
                body1.acceleration += acc
    
    def get_total_energy(self):
        """Calculate total energy (Kinetic + Potential) of the system."""
        kinetic = 0.0
        potential = 0.0
        
        for i, body1 in enumerate(self.bodies):
            # Kinetic Energy: 0.5 * m * v^2
            v_sq = np.sum(body1.velocity**2)
            kinetic += 0.5 * body1.mass * v_sq
            
            # Potential Energy: - G * m1 * m2 / r
            for j in range(i + 1, len(self.bodies)):
                body2 = self.bodies[j]
                r = np.linalg.norm(body1.position - body2.position)
                if r > 0:
                    potential -= G * body1.mass * body2.mass / r
                    
        return kinetic + potential
