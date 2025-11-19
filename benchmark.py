import sys
import os
import time
import pandas as pd

# Add src to path
sys.path.append(os.path.abspath('src'))

from simulation.engine import Simulation
from simulation.matrix_engine import MatrixSimulation

def run_benchmark(population_size: int, years: int = 500):
    print(f"\n--- Benchmarking with Initial Population: {population_size} ---")
    
    # 1. Agent-Based Simulation
    start_time = time.time()
    agent_sim = Simulation(initial_ordinary=population_size, initial_bio=population_size)
    agent_sim.run(years)
    agent_time = time.time() - start_time
    
    agent_final = agent_sim.history[-1]
    print(f"Agent-Based: {agent_time:.4f}s")
    print(f"  Final Pop: {agent_final['total']} (Ord: {agent_final['ordinary']}, Bio: {agent_final['bio']})")
    
    # 2. Matrix-Based Simulation
    start_time = time.time()
    matrix_sim = MatrixSimulation(initial_ordinary=population_size, initial_bio=population_size)
    matrix_sim.run(years)
    matrix_time = time.time() - start_time
    
    matrix_final = matrix_sim.history[-1]
    print(f"Matrix-Based: {matrix_time:.4f}s")
    print(f"  Final Pop: {matrix_final['total']} (Ord: {matrix_final['ordinary']}, Bio: {matrix_final['bio']})")
    
    # Comparison
    speedup = agent_time / matrix_time if matrix_time > 0 else 0
    print(f"Speedup: {speedup:.2f}x")
    
    return {
        "population": population_size,
        "agent_time": agent_time,
        "matrix_time": matrix_time,
        "speedup": speedup
    }

def main():
    # Run benchmarks for different sizes
    # Note: Agent based gets very slow, so we keep sizes moderate for the demo
    sizes = [100, 1000, 10000] 
    results = []
    
    for size in sizes:
        results.append(run_benchmark(size))
        
    print("\n--- Summary ---")
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
