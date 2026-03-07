"""
Enhanced code templates with complete, interactive implementations
Supports beginner, intermediate, and advanced levels
"""

def get_linear_search_template(level='beginner'):
    """Linear search with different complexity levels"""
    
    if level == 'beginner':
        return """def linear_search(arr, target):
    \"\"\"
    Search for target in array using linear search
    Returns: index if found, -1 if not found
    \"\"\"
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Interactive example
if __name__ == "__main__":
    # Get input from user
    print("=== Linear Search ===")
    arr_input = input("Enter numbers separated by spaces: ")
    arr = [int(x) for x in arr_input.split()]
    
    target = int(input("Enter number to search: "))
    
    # Perform search
    result = linear_search(arr, target)
    
    # Display result
    if result != -1:
        print(f"\\n✓ Found {target} at index {result}")
    else:
        print(f"\\n✗ {target} not found in array")
    
    print(f"Array: {arr}")"""
    
    elif level == 'intermediate':
        return """def linear_search(arr, target):
    \"\"\"
    Linear search with step-by-step visualization
    Returns: (index, comparisons_made)
    \"\"\"
    comparisons = 0
    for i in range(len(arr)):
        comparisons += 1
        if arr[i] == target:
            return i, comparisons
    return -1, comparisons

# Interactive example with statistics
if __name__ == "__main__":
    print("=== Linear Search with Statistics ===\\n")
    
    # Get input
    try:
        arr_input = input("Enter numbers (space-separated): ")
        arr = [int(x) for x in arr_input.split()]
        target = int(input("Enter target number: "))
        
        # Perform search
        index, comparisons = linear_search(arr, target)
        
        # Display results
        print(f"\\nArray: {arr}")
        print(f"Target: {target}")
        print(f"Comparisons made: {comparisons}")
        
        if index != -1:
            print(f"\\n✓ SUCCESS: Found at index {index}")
        else:
            print(f"\\n✗ NOT FOUND")
            
    except ValueError:
        print("Error: Please enter valid integers")"""
    
    else:  # advanced
        return """class LinearSearch:
    \"\"\"Advanced linear search with multiple search modes\"\"\"
    
    def __init__(self, arr):
        self.arr = arr
        self.search_history = []
    
    def search(self, target, mode='first'):
        \"\"\"
        Search for target with different modes
        mode: 'first', 'last', 'all', 'count'
        \"\"\"
        result = {'target': target, 'mode': mode, 'comparisons': 0}
        
        if mode == 'first':
            for i in range(len(self.arr)):
                result['comparisons'] += 1
                if self.arr[i] == target:
                    result['index'] = i
                    break
            else:
                result['index'] = -1
                
        elif mode == 'last':
            result['index'] = -1
            for i in range(len(self.arr)):
                result['comparisons'] += 1
                if self.arr[i] == target:
                    result['index'] = i
                    
        elif mode == 'all':
            result['indices'] = []
            for i in range(len(self.arr)):
                result['comparisons'] += 1
                if self.arr[i] == target:
                    result['indices'].append(i)
                    
        elif mode == 'count':
            result['count'] = 0
            for i in range(len(self.arr)):
                result['comparisons'] += 1
                if self.arr[i] == target:
                    result['count'] += 1
        
        self.search_history.append(result)
        return result
    
    def get_statistics(self):
        \"\"\"Get search statistics\"\"\"
        if not self.search_history:
            return "No searches performed"
        
        total_comparisons = sum(s['comparisons'] for s in self.search_history)
        return {
            'total_searches': len(self.search_history),
            'total_comparisons': total_comparisons,
            'avg_comparisons': total_comparisons / len(self.search_history)
        }

# Interactive advanced example
if __name__ == "__main__":
    print("=== Advanced Linear Search ===\\n")
    
    # Get input
    arr_input = input("Enter numbers (space-separated): ")
    arr = [int(x) for x in arr_input.split()]
    
    searcher = LinearSearch(arr)
    
    while True:
        print(f"\\nArray: {arr}")
        print("\\nModes: first, last, all, count, stats, quit")
        
        target = input("Enter target (or command): ")
        
        if target == 'quit':
            break
        elif target == 'stats':
            stats = searcher.get_statistics()
            print(f"\\nStatistics: {stats}")
            continue
        
        try:
            target = int(target)
            mode = input("Mode (first/last/all/count): ") or 'first'
            
            result = searcher.search(target, mode)
            print(f"\\nResult: {result}")
            
        except ValueError:
            print("Invalid input")"""


def get_bubble_sort_template(level='beginner'):
    """Bubble sort with different complexity levels"""
    
    if level == 'beginner':
        return """def bubble_sort(arr):
    \"\"\"
    Sort array using bubble sort algorithm
    Returns: sorted array
    \"\"\"
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Interactive example
if __name__ == "__main__":
    print("=== Bubble Sort ===\\n")
    
    # Get input
    arr_input = input("Enter numbers to sort (space-separated): ")
    arr = [int(x) for x in arr_input.split()]
    
    print(f"\\nOriginal: {arr}")
    
    # Sort
    sorted_arr = bubble_sort(arr.copy())
    
    print(f"Sorted:   {sorted_arr}")"""
    
    elif level == 'intermediate':
        return """def bubble_sort(arr, show_steps=False):
    \"\"\"
    Bubble sort with optional step visualization
    Returns: (sorted_array, swaps_made, passes)
    \"\"\"
    n = len(arr)
    swaps = 0
    passes = 0
    
    for i in range(n):
        passes += 1
        swapped = False
        
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                
                if show_steps:
                    print(f"Pass {passes}: {arr}")
        
        if not swapped:
            break
    
    return arr, swaps, passes

# Interactive example with statistics
if __name__ == "__main__":
    print("=== Bubble Sort with Statistics ===\\n")
    
    # Get input
    arr_input = input("Enter numbers (space-separated): ")
    arr = [int(x) for x in arr_input.split()]
    
    show = input("Show steps? (y/n): ").lower() == 'y'
    
    print(f"\\nOriginal: {arr}")
    
    # Sort
    sorted_arr, swaps, passes = bubble_sort(arr.copy(), show)
    
    print(f"\\nSorted: {sorted_arr}")
    print(f"Swaps made: {swaps}")
    print(f"Passes: {passes}")"""
    
    else:  # advanced
        return """class BubbleSort:
    \"\"\"Advanced bubble sort with analysis and optimization\"\"\"
    
    def __init__(self):
        self.history = []
    
    def sort(self, arr, optimized=True):
        \"\"\"
        Sort with optional optimization
        Returns: detailed statistics
        \"\"\"
        n = len(arr)
        stats = {
            'original': arr.copy(),
            'comparisons': 0,
            'swaps': 0,
            'passes': 0,
            'optimized': optimized
        }
        
        for i in range(n):
            stats['passes'] += 1
            swapped = False
            
            for j in range(0, n - i - 1):
                stats['comparisons'] += 1
                
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    stats['swaps'] += 1
                    swapped = True
            
            # Optimization: stop if no swaps
            if optimized and not swapped:
                break
        
        stats['sorted'] = arr
        stats['efficiency'] = stats['comparisons'] / (n * n) if n > 0 else 0
        
        self.history.append(stats)
        return stats
    
    def compare_optimization(self, arr):
        \"\"\"Compare optimized vs non-optimized\"\"\"
        result_opt = self.sort(arr.copy(), optimized=True)
        result_std = self.sort(arr.copy(), optimized=False)
        
        return {
            'optimized': result_opt,
            'standard': result_std,
            'improvement': {
                'passes_saved': result_std['passes'] - result_opt['passes'],
                'comparisons_saved': result_std['comparisons'] - result_opt['comparisons']
            }
        }

# Interactive advanced example
if __name__ == "__main__":
    print("=== Advanced Bubble Sort Analysis ===\\n")
    
    sorter = BubbleSort()
    
    while True:
        print("\\nOptions: sort, compare, history, quit")
        choice = input("Choose: ").lower()
        
        if choice == 'quit':
            break
        
        elif choice == 'sort':
            arr_input = input("Enter numbers: ")
            arr = [int(x) for x in arr_input.split()]
            
            opt = input("Use optimization? (y/n): ").lower() == 'y'
            stats = sorter.sort(arr, opt)
            
            print(f"\\nOriginal: {stats['original']}")
            print(f"Sorted: {stats['sorted']}")
            print(f"Comparisons: {stats['comparisons']}")
            print(f"Swaps: {stats['swaps']}")
            print(f"Passes: {stats['passes']}")
            print(f"Efficiency: {stats['efficiency']:.2%}")
        
        elif choice == 'compare':
            arr_input = input("Enter numbers: ")
            arr = [int(x) for x in arr_input.split()]
            
            comparison = sorter.compare_optimization(arr)
            print(f"\\nImprovement: {comparison['improvement']}")
        
        elif choice == 'history':
            print(f"\\nTotal sorts: {len(sorter.history)}")"""


def get_factorial_template(level='beginner'):
    """Factorial with different complexity levels"""
    
    if level == 'beginner':
        return """def factorial(n):
    \"\"\"Calculate factorial of n\"\"\"
    if n < 0:
        return None
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

# Interactive example
if __name__ == "__main__":
    print("=== Factorial Calculator ===\\n")
    
    try:
        n = int(input("Enter a number: "))
        result = factorial(n)
        
        if result is None:
            print("Error: Factorial not defined for negative numbers")
        else:
            print(f"\\n{n}! = {result}")
    except ValueError:
        print("Error: Please enter a valid integer")"""
    
    elif level == 'intermediate':
        return """def factorial_iterative(n):
    \"\"\"Calculate factorial iteratively\"\"\"
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def factorial_recursive(n):
    \"\"\"Calculate factorial recursively\"\"\"
    if n < 0:
        return None
    if n == 0 or n == 1:
        return 1
    return n * factorial_recursive(n - 1)

# Interactive comparison
if __name__ == "__main__":
    print("=== Factorial Calculator (Iterative vs Recursive) ===\\n")
    
    try:
        n = int(input("Enter a number: "))
        
        if n < 0:
            print("Error: Factorial not defined for negative numbers")
        else:
            result_iter = factorial_iterative(n)
            result_rec = factorial_recursive(n)
            
            print(f"\\nIterative: {n}! = {result_iter}")
            print(f"Recursive: {n}! = {result_rec}")
            
            # Show calculation steps
            print(f"\\nCalculation: ", end="")
            print(" × ".join(str(i) for i in range(1, n+1) if n > 0) or "1")
            
    except ValueError:
        print("Error: Please enter a valid integer")
    except RecursionError:
        print("Error: Number too large for recursive calculation")"""
    
    else:  # advanced
        return """import time
from functools import lru_cache

class FactorialCalculator:
    \"\"\"Advanced factorial with multiple methods and caching\"\"\"
    
    def __init__(self):
        self.cache = {0: 1, 1: 1}
        self.stats = {'iterative': 0, 'recursive': 0, 'cached': 0}
    
    def iterative(self, n):
        \"\"\"Iterative factorial\"\"\"
        if n < 0:
            return None
        self.stats['iterative'] += 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @lru_cache(maxsize=None)
    def recursive(self, n):
        \"\"\"Recursive factorial with memoization\"\"\"
        if n < 0:
            return None
        self.stats['recursive'] += 1
        if n == 0 or n == 1:
            return 1
        return n * self.recursive(n - 1)
    
    def cached(self, n):
        \"\"\"Manual cache implementation\"\"\"
        if n < 0:
            return None
        if n in self.cache:
            self.stats['cached'] += 1
            return self.cache[n]
        
        result = n * self.cached(n - 1)
        self.cache[n] = result
        return result
    
    def benchmark(self, n, method='all'):
        \"\"\"Benchmark different methods\"\"\"
        results = {}
        
        if method in ['all', 'iterative']:
            start = time.time()
            result = self.iterative(n)
            results['iterative'] = {'result': result, 'time': time.time() - start}
        
        if method in ['all', 'recursive']:
            start = time.time()
            result = self.recursive(n)
            results['recursive'] = {'result': result, 'time': time.time() - start}
        
        if method in ['all', 'cached']:
            start = time.time()
            result = self.cached(n)
            results['cached'] = {'result': result, 'time': time.time() - start}
        
        return results

# Interactive advanced example
if __name__ == "__main__":
    print("=== Advanced Factorial Calculator ===\\n")
    
    calc = FactorialCalculator()
    
    while True:
        print("\\nOptions: calc, benchmark, stats, quit")
        choice = input("Choose: ").lower()
        
        if choice == 'quit':
            break
        
        elif choice == 'calc':
            try:
                n = int(input("Enter number: "))
                method = input("Method (iterative/recursive/cached): ") or 'cached'
                
                if method == 'iterative':
                    result = calc.iterative(n)
                elif method == 'recursive':
                    result = calc.recursive(n)
                else:
                    result = calc.cached(n)
                
                print(f"\\n{n}! = {result}")
                
            except ValueError:
                print("Invalid input")
            except RecursionError:
                print("Number too large")
        
        elif choice == 'benchmark':
            try:
                n = int(input("Enter number (< 100): "))
                results = calc.benchmark(n)
                
                print("\\nBenchmark Results:")
                for method, data in results.items():
                    print(f"{method}: {data['time']:.6f}s")
                    
            except ValueError:
                print("Invalid input")
        
        elif choice == 'stats':
            print(f"\\nMethod usage: {calc.stats}")
            print(f"Cache size: {len(calc.cache)}")"""
