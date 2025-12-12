
import numpy as np

# --- 1. Real World Constants (SI Units) ---
# For reference and external data input
SI_G = 6.67430e-11       # m^3 kg^-1 s^-2
SI_M_SUN = 1.989e30      # kg
SI_M_EARTH = 5.972e24    # kg
SI_AU = 1.496e11         # m
SI_YEAR = 3.15576e7      # s (Gaussian year approx 365.2568983 days)

# --- 2. Simulation Units (Normalized) ---
# Base units for the simulation kernel
# We choose these such that GM_sun = 4*pi^2 (if time is 1 year) or other convenient forms.
UNIT_MASS = SI_M_SUN
UNIT_DIST = SI_AU
UNIT_TIME = SI_YEAR

# --- 3. Derived Simulation Constants ---
# Gravity in simulation units: G_sim = G_si * (Mass_unit * Time_unit^2 / Length_unit^3)
# Theoretical check: 6.67e-11 * (1.989e30 * (3.15e7)^2 / (1.496e11)^3) ≈ 39.47 ≈ 4*pi^2
G = 4 * np.pi**2 

# Normalized values for use in code
AU = 1.0                # Distance unit
YEAR = 1.0              # Time unit
M_SUN = 1.0             # Mass unit
M_EARTH = SI_M_EARTH / SI_M_SUN  # Relative mass (~3e-6)

# --- 4. Simulation Settings ---
DEFAULT_DT = 1 / 365.0  # One day in years
