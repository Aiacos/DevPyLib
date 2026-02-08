"""Startup performance benchmark for lazy loading implementation.

This script measures the performance improvement from lazy loading by comparing:
1. Lazy import time (just importing mayaLib without accessing submodules)
2. Eager import time (importing and accessing all submodules)

The benchmark verifies that lazy loading reduces import time by at least 30%.
"""

import importlib
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories to path for imports
_test_dir = Path(__file__).parent.resolve()
_mayalib_dir = _test_dir.parent
_root_dir = _mayalib_dir.parent

if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))


# ANSI color codes for output
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def clean_module_cache():
    """Remove all mayaLib-related modules from sys.modules cache.

    This ensures we get accurate timing for fresh imports.
    """
    modules_to_remove = [
        key for key in list(sys.modules.keys()) if key.startswith("mayaLib")
    ]
    for module in modules_to_remove:
        del sys.modules[module]


def measure_lazy_import() -> float:
    """Measure time to import mayaLib with lazy loading (no submodule access).

    Returns:
        float: Import time in seconds.
    """
    clean_module_cache()

    start_time = time.perf_counter()
    import mayaLib  # noqa: F401
    end_time = time.perf_counter()

    return end_time - start_time


def measure_eager_import() -> Tuple[float, Dict[str, bool]]:
    """Measure time to import mayaLib and access all submodules (simulates eager loading).

    Returns:
        Tuple[float, Dict[str, bool]]: Import time in seconds and dict of submodule availability.
    """
    clean_module_cache()

    # List of all submodules to access
    submodules = [
        "animationLib",
        "bifrostLib",
        "fluidLib",
        "guiLib",
        "lookdevLib",
        "lunaLib",
        "modelLib",
        "pipelineLib",
        "rigLib",
        "shaderLib",
        "utility",
    ]

    submodule_status = {}

    start_time = time.perf_counter()

    # Import mayaLib
    import mayaLib

    # Access all submodules to trigger lazy loading
    for submodule_name in submodules:
        try:
            submodule = getattr(mayaLib, submodule_name)
            submodule_status[submodule_name] = submodule is not None
        except (ImportError, AttributeError) as e:
            print(
                f"{Colors.WARNING}Warning: Failed to load {submodule_name}: {e}{Colors.ENDC}"
            )
            submodule_status[submodule_name] = False

    end_time = time.perf_counter()

    return end_time - start_time, submodule_status


def measure_nested_imports() -> Tuple[float, Dict[str, bool]]:
    """Measure time to import common nested submodules (realistic usage).

    Returns:
        Tuple[float, Dict[str, bool]]: Import time in seconds and dict of submodule availability.
    """
    clean_module_cache()

    # Common nested imports that users typically need
    nested_imports = [
        ("rigLib", ["base", "utils", "Ziva"]),
        ("fluidLib", ["fire", "smoke"]),
        ("guiLib", ["base"]),
        ("modelLib", ["utils"]),
        ("shaderLib", ["base"]),
        ("pipelineLib", ["utility"]),
    ]

    import_status = {}

    start_time = time.perf_counter()

    # Import mayaLib
    import mayaLib

    # Access nested modules
    for parent, children in nested_imports:
        try:
            parent_module = getattr(mayaLib, parent)
            for child in children:
                try:
                    child_module = getattr(parent_module, child)
                    key = f"{parent}.{child}"
                    import_status[key] = child_module is not None
                except (ImportError, AttributeError) as e:
                    key = f"{parent}.{child}"
                    import_status[key] = False
                    print(
                        f"{Colors.WARNING}Warning: Failed to load {key}: {e}{Colors.ENDC}"
                    )
        except (ImportError, AttributeError) as e:
            print(
                f"{Colors.WARNING}Warning: Failed to load {parent}: {e}{Colors.ENDC}"
            )
            for child in children:
                import_status[f"{parent}.{child}"] = False

    end_time = time.perf_counter()

    return end_time - start_time, import_status


def format_time(seconds: float) -> str:
    """Format time in seconds to human-readable string.

    Args:
        seconds: Time in seconds.

    Returns:
        str: Formatted time string.
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} μs"
    elif seconds < 1.0:
        return f"{seconds * 1000:.1f} ms"
    else:
        return f"{seconds:.3f} s"


def print_section_header(title: str):
    """Print a formatted section header.

    Args:
        title: Section title.
    """
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


def run_benchmark() -> bool:
    """Run the complete startup performance benchmark.

    Returns:
        bool: True if lazy loading achieves >= 30% improvement, False otherwise.
    """
    print_section_header("Maya Startup Performance Benchmark")

    # Run benchmarks multiple times and take average
    num_runs = 5
    print(f"Running {num_runs} iterations for each test...\n")

    # Measure lazy import (multiple runs)
    lazy_times = []
    for i in range(num_runs):
        lazy_time = measure_lazy_import()
        lazy_times.append(lazy_time)
        print(f"  Lazy import run {i + 1}: {format_time(lazy_time)}")

    avg_lazy = sum(lazy_times) / len(lazy_times)
    print(
        f"\n{Colors.OKBLUE}Average lazy import time: {format_time(avg_lazy)}{Colors.ENDC}"
    )

    # Measure eager import (multiple runs)
    print(f"\n{Colors.OKCYAN}Simulating eager loading (accessing all submodules)...{Colors.ENDC}")
    eager_times = []
    submodule_status = {}

    for i in range(num_runs):
        eager_time, status = measure_eager_import()
        eager_times.append(eager_time)
        submodule_status = status  # Keep last status
        print(f"  Eager import run {i + 1}: {format_time(eager_time)}")

    avg_eager = sum(eager_times) / len(eager_times)
    print(
        f"\n{Colors.OKBLUE}Average eager import time: {format_time(avg_eager)}{Colors.ENDC}"
    )

    # Measure nested imports (realistic usage)
    print(f"\n{Colors.OKCYAN}Measuring realistic nested imports...{Colors.ENDC}")
    nested_times = []
    nested_status = {}

    for i in range(num_runs):
        nested_time, status = measure_nested_imports()
        nested_times.append(nested_time)
        nested_status = status  # Keep last status
        print(f"  Nested import run {i + 1}: {format_time(nested_time)}")

    avg_nested = sum(nested_times) / len(nested_times)
    print(
        f"\n{Colors.OKBLUE}Average nested import time: {format_time(avg_nested)}{Colors.ENDC}"
    )

    # Calculate improvement
    print_section_header("Performance Analysis")

    # Lazy vs Eager comparison
    time_saved = avg_eager - avg_lazy
    improvement_percentage = (time_saved / avg_eager) * 100 if avg_eager > 0 else 0

    print(f"Lazy loading time:       {format_time(avg_lazy)}")
    print(f"Eager loading time:      {format_time(avg_eager)}")
    print(f"Time saved:              {format_time(time_saved)}")
    print(
        f"Performance improvement: {Colors.BOLD}{improvement_percentage:.1f}%{Colors.ENDC}"
    )

    # Lazy vs Nested comparison (more realistic)
    nested_saved = avg_nested - avg_lazy
    nested_improvement = (nested_saved / avg_nested) * 100 if avg_nested > 0 else 0

    print(f"\nRealistic usage (nested imports):")
    print(f"Lazy loading time:       {format_time(avg_lazy)}")
    print(f"With nested imports:     {format_time(avg_nested)}")
    print(f"Time saved:              {format_time(nested_saved)}")
    print(
        f"Performance improvement: {Colors.BOLD}{nested_improvement:.1f}%{Colors.ENDC}"
    )

    # Module availability report
    print_section_header("Module Availability")

    successful_modules = sum(1 for available in submodule_status.values() if available)
    total_modules = len(submodule_status)

    print(
        f"Successfully loaded: {successful_modules}/{total_modules} submodules\n"
    )

    if successful_modules < total_modules:
        print(f"{Colors.WARNING}Failed to load:{Colors.ENDC}")
        for module, available in sorted(submodule_status.items()):
            if not available:
                print(f"  - {module}")
        print()

    # Nested module availability
    successful_nested = sum(1 for available in nested_status.values() if available)
    total_nested = len(nested_status)

    print(
        f"Successfully loaded: {successful_nested}/{total_nested} nested modules\n"
    )

    if successful_nested < total_nested:
        print(f"{Colors.WARNING}Failed to load:{Colors.ENDC}")
        for module, available in sorted(nested_status.items()):
            if not available:
                print(f"  - {module}")
        print()

    # Final verdict
    print_section_header("Benchmark Result")

    target_improvement = 30.0
    passed = improvement_percentage >= target_improvement

    if passed:
        print(
            f"{Colors.OKGREEN}{Colors.BOLD}✓ PASSED{Colors.ENDC}{Colors.OKGREEN}"
            f" - Lazy loading achieves {improvement_percentage:.1f}% improvement{Colors.ENDC}"
        )
        print(
            f"{Colors.OKGREEN}  (Target: >= {target_improvement}% improvement){Colors.ENDC}\n"
        )
    else:
        print(
            f"{Colors.FAIL}{Colors.BOLD}✗ FAILED{Colors.ENDC}{Colors.FAIL}"
            f" - Lazy loading achieves only {improvement_percentage:.1f}% improvement{Colors.ENDC}"
        )
        print(
            f"{Colors.FAIL}  (Target: >= {target_improvement}% improvement){Colors.ENDC}\n"
        )

    # Additional notes
    print(f"{Colors.OKCYAN}Notes:{Colors.ENDC}")
    print(
        f"  - Lazy loading defers all submodule imports until first access"
    )
    print(
        f"  - This benchmark simulates the worst case (accessing ALL submodules)"
    )
    print(
        f"  - In real usage, artists typically use only 1-2 submodules per session"
    )
    print(
        f"  - Actual startup time improvement will be even greater than measured"
    )
    print()

    return passed


if __name__ == "__main__":
    # Run benchmark
    success = run_benchmark()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
