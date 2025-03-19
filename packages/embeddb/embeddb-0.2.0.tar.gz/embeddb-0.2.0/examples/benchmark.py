"""
Benchmarking script for EmbedDB.

This script measures performance of EmbedDB for different database sizes:
- Add performance (ms per vector)
- Search performance (ms per search)
- Memory usage (MB)

Results can be used to update the README benchmarks.
"""

import gc
import os
import random
import sys
import time
from typing import List, Dict, Any
import numpy as np
import psutil
import matplotlib.pyplot as plt

# Add parent directory to path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from embeddb import EmbedDB


def generate_random_vector(dim: int) -> List[float]:
    """Generate a random vector with the specified dimension."""
    return [random.random() for _ in range(dim)]


def generate_test_data(count: int, dim: int) -> Dict[str, Any]:
    """Generate test data with random vectors."""
    vectors = {}
    for i in range(count):
        id = f"vec{i}"
        vector = generate_random_vector(dim)
        metadata = {"description": f"Test vector {i}"}
        vectors[id] = (vector, metadata)
    return vectors


def measure_memory() -> float:
    """Measure the current memory usage in MB."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert to MB


def benchmark_add(db: EmbedDB, test_data: Dict[str, Any]) -> float:
    """Benchmark the add operation."""
    start_time = time.time()
    for id, (vector, metadata) in test_data.items():
        db.add(id, vector, metadata)
    end_time = time.time()
    total_time = end_time - start_time
    return (total_time * 1000) / len(test_data)  # ms per vector


def benchmark_search(db: EmbedDB, dim: int, num_searches: int = 10) -> float:
    """Benchmark the search operation."""
    total_time = 0
    for _ in range(num_searches):
        query = generate_random_vector(dim)
        start_time = time.time()
        db.search(query, top_k=10)
        end_time = time.time()
        total_time += (end_time - start_time)
    return (total_time * 1000) / num_searches  # ms per search


def run_benchmarks(sizes: List[int], dim: int = 384) -> Dict[str, Dict[str, float]]:
    """Run benchmarks for different database sizes."""
    results = {}
    
    for size in sizes:
        print(f"Benchmarking with {size} vectors...")
        
        # Clear memory and create a fresh database
        gc.collect()
        db = EmbedDB(dimension=dim)
        
        # Generate test data
        test_data = generate_test_data(size, dim)
        
        # Measure baseline memory
        baseline_memory = measure_memory()
        
        # Benchmark add operation
        add_time = benchmark_add(db, test_data)
        
        # Measure memory after adding vectors
        after_add_memory = measure_memory()
        memory_usage = after_add_memory - baseline_memory
        
        # Benchmark search operation
        search_time = benchmark_search(db, dim)
        
        # Store results
        results[size] = {
            "add_time_ms": add_time,
            "search_time_ms": search_time,
            "memory_mb": memory_usage
        }
        
        print(f"  Add time: {add_time:.2f} ms/vector")
        print(f"  Search time: {search_time:.2f} ms")
        print(f"  Memory usage: {memory_usage:.2f} MB")
    
    return results


def plot_results(results: Dict[str, Dict[str, float]]):
    """Plot the benchmark results."""
    sizes = list(results.keys())
    sizes.sort()
    
    # Extract metrics
    add_times = [results[size]["add_time_ms"] for size in sizes]
    search_times = [results[size]["search_time_ms"] for size in sizes]
    memory_usages = [results[size]["memory_mb"] for size in sizes]
    
    # Create a figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot add time
    ax1.plot(sizes, add_times, marker='o')
    ax1.set_xscale('log')
    ax1.set_title('Add Time (ms/vector)')
    ax1.set_xlabel('Database Size (vectors)')
    ax1.set_ylabel('Time (ms)')
    ax1.grid(True)
    
    # Plot search time
    ax2.plot(sizes, search_times, marker='o')
    ax2.set_xscale('log')
    ax2.set_title('Search Time (ms)')
    ax2.set_xlabel('Database Size (vectors)')
    ax2.set_ylabel('Time (ms)')
    ax2.grid(True)
    
    # Plot memory usage
    ax3.plot(sizes, memory_usages, marker='o')
    ax3.set_xscale('log')
    ax3.set_title('Memory Usage (MB)')
    ax3.set_xlabel('Database Size (vectors)')
    ax3.set_ylabel('Memory (MB)')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png')
    plt.show()


def print_table(results: Dict[str, Dict[str, float]]):
    """Print the benchmark results as a markdown table."""
    sizes = list(results.keys())
    sizes.sort()
    
    print("\n### Benchmarking Results\n")
    print("| Database Size | Add (ms/vector) | Search (ms) | Memory (MB) |")
    print("|---------------|----------------|------------|-------------|")
    
    for size in sizes:
        add_time = results[size]["add_time_ms"]
        search_time = results[size]["search_time_ms"]
        memory_usage = results[size]["memory_mb"]
        
        print(f"| {size:,} vectors | {add_time:.2f} | {search_time:.2f} | {memory_usage:.1f} |")


if __name__ == "__main__":
    try:
        import psutil
        import matplotlib.pyplot as plt
    except ImportError:
        print("Please install required packages:")
        print("pip install psutil matplotlib")
        sys.exit(1)
    
    # Define the database sizes to benchmark
    sizes = [100, 1000, 10000]
    
    # Optionally add larger sizes if enough memory is available
    system_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # GB
    if system_memory > 8:
        sizes.append(100000)
    if system_memory > 16:
        sizes.append(1000000)
        
    # Run benchmarks
    print(f"Running benchmarks on sizes: {sizes}")
    results = run_benchmarks(sizes)
    
    # Print table for README
    print_table(results)
    
    # Plot results if matplotlib is available
    try:
        plot_results(results)
        print("\nBenchmark plot saved as 'benchmark_results.png'")
    except:
        print("\nCould not create plot. Make sure matplotlib is installed.")
    
    print("\nBenchmark complete!") 