
import sys
import os
import numpy as np

# Add src to path to allow running directly from this location
# current_dir = .../src/sun_earth
# src_dir = .../src
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from sun_earth.config import G, AU, YEAR, M_EARTH
from sun_earth.model.body import Body
from sun_earth.model.system import SolarSystem
from sun_earth.model.integrators import Integrator

def run_test():
    print("Running Verification for Solar-Earth Model...")
    
    # Setup
    sun = Body(name='Sun', mass=1.0, position=[0, 0], velocity=[0, 0])
    v_circular = 2 * np.pi
    earth = Body(name='Earth', mass=M_EARTH, position=[1.0, 0], velocity=[0, v_circular])
    system = SolarSystem([sun, earth])
    
    dt = 1/3650 # Fine step for verification
    steps = 3650 # 1 Year
    
    # 1. Run Leapfrog
    print(f"Simulating 1 year with Leapfrog (dt={dt} year)...")
    system.compute_forces()
    initial_energy = system.get_total_energy()
    
    for _ in range(steps):
        Integrator.step(system, dt, method='leapfrog')
        
    final_energy = system.get_total_energy()
    final_pos = earth.position
    
    # 2. Checks
    print("\nResults:")
    
    # Position Check
    # At t=1, Earth should be back at (1, 0)
    dist_err = np.linalg.norm(final_pos - np.array([1.0, 0.0]))
    print(f"Position Error after 1 year: {dist_err:.6f} AU")
    
    if dist_err < 0.01:
        print("✔ Orbital Period Check Passed (Earth returned to start)")
    else:
        print("❌ Orbital Period Check Failed")

    # Energy Check
    energy_drift = abs((final_energy - initial_energy) / initial_energy)
    print(f"Energy Drift: {energy_drift:.2e}")
    
    if energy_drift < 1e-5:
        print("✔ Energy Conservation Check Passed")
    else:
        print("❌ Energy Conservation Check Failed")

if __name__ == "__main__":
    run_test()
