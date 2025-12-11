
import numpy as np

class Body:
    def __init__(self, name, mass, position, velocity, color='white', texture_path=None):
        """
        Initialize a celestial body.
        
        Args:
            name (str): Name of the body (e.g., 'Earth')
            mass (float): Mass in solar masses
            position (list or np.array): Initial position [x, y] in AU
            velocity (list or np.array): Initial velocity [vx, vy] in AU/Year
            color (str): Fallback color for visualization
            texture_path (str): Path to texture image (optional)
        """
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2, dtype=float)
        self.color = color
        self.texture_path = texture_path
        
        # History for trail
        self.history = []

    def update_pos(self, dt):
        self.position += self.velocity * dt
        self.history.append(self.position.copy())
        # Limit history size to prevent memory issues 
        # (Though for 1-10 years daily steps it's fine, ~3650 points)
        if len(self.history) > 5000:
             self.history.pop(0)

    def update_vel(self, dt):
        self.velocity += self.acceleration * dt
    
    def clear_history(self):
        self.history = []
