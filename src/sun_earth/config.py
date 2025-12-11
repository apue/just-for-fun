
import numpy as np

# Physical Constants (Normalized)
# Unit of distance: 1 AU (Astronomical Unit)
# Unit of time: 1 Year
# Unit of mass: 1 Solar Mass (M_sun)

G = 4 * np.pi**2  # Gravitational constant in these units

# Constants for reference
AU = 1.0
YEAR = 1.0
M_SUN = 1.0
M_EARTH = 3.003e-6  # Earth's mass in solar masses

# Default Simulation Parameters
DEFAULT_DT = 0.001 # Time step in years (approx 8 hours)
# A smaller dt is better for energy conservation analysis
