"""Progress callback feature demonstration script.

Example script demonstrating the progress callback functionality in FunctionUI.
Shows how functions can provide progress feedback during long-running operations
using the automatic progress bar and status label display.

Run this script in Maya to see various progress callback examples.
"""

__author__ = "Lorenzo Argentieri"

import time

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

from mayaLib.guiLib.base.base_ui import FunctionUI


def simple_operation(iterations=10, progress_callback=None):
    """Demonstrate basic progress callback usage.

    Simulates a simple long-running operation with progress updates.
    Each iteration updates the progress bar and status message.

    Args:
        iterations (int): Number of iterations to perform (default: 10).
        progress_callback (callable, optional): Callback function for progress updates.
            Receives (percent: int, message: str).
    """
    for i in range(iterations):
        # Simulate work
        time.sleep(0.2)

        # Update progress
        if progress_callback:
            percent = int(((i + 1) / iterations) * 100)
            message = f"Processing iteration {i + 1} of {iterations}"
            progress_callback(percent, message)


def multi_stage_operation(stages=3, steps_per_stage=5, progress_callback=None):
    """Demonstrate multi-stage operation with progress updates.

    Simulates a complex operation with multiple stages, each containing
    multiple steps. Shows how to calculate progress across stages.

    Args:
        stages (int): Number of stages in the operation (default: 3).
        steps_per_stage (int): Number of steps per stage (default: 5).
        progress_callback (callable, optional): Callback function for progress updates.
            Receives (percent: int, message: str).
    """
    total_steps = stages * steps_per_stage
    current_step = 0

    for stage in range(stages):
        for step in range(steps_per_stage):
            # Simulate work
            time.sleep(0.15)

            # Update progress
            if progress_callback:
                current_step += 1
                percent = int((current_step / total_steps) * 100)
                message = f"Stage {stage + 1}/{stages} - Step {step + 1}/{steps_per_stage}"
                progress_callback(percent, message)


def batch_processing(item_count=8, progress_callback=None):
    """Demonstrate batch processing with progress updates.

    Simulates processing multiple items (e.g., textures, meshes, nodes)
    with detailed status messages for each item.

    Args:
        item_count (int): Number of items to process (default: 8).
        progress_callback (callable, optional): Callback function for progress updates.
            Receives (percent: int, message: str).
    """
    items = [f"item_{i + 1}" for i in range(item_count)]

    for idx, item in enumerate(items):
        # Simulate processing item
        time.sleep(0.25)

        # Update progress with item name
        if progress_callback:
            percent = int(((idx + 1) / len(items)) * 100)
            message = f"Processing {item} ({idx + 1}/{len(items)})"
            progress_callback(percent, message)


def variable_speed_operation(total_time=5, progress_callback=None):
    """Demonstrate operation with variable speed updates.

    Simulates an operation where progress updates occur at different
    intervals, showing that the callback can be called at any time.

    Args:
        total_time (int): Total duration in seconds (default: 5).
        progress_callback (callable, optional): Callback function for progress updates.
            Receives (percent: int, message: str).
    """
    start_time = time.time()
    last_percent = 0

    while True:
        elapsed = time.time() - start_time
        percent = min(int((elapsed / total_time) * 100), 100)

        # Update progress if percentage changed
        if progress_callback and percent > last_percent:
            if percent < 30:
                message = "Initializing..."
            elif percent < 70:
                message = "Processing..."
            elif percent < 100:
                message = "Finalizing..."
            else:
                message = "Complete!"

            progress_callback(percent, message)
            last_percent = percent

        # Break when complete
        if percent >= 100:
            break

        # Variable sleep duration
        time.sleep(0.1)


def show_simple_example():
    """Create and show UI for simple operation example."""
    ui = FunctionUI(simple_operation)
    ui.setWindowTitle("Simple Progress Example")
    ui.show()
    return ui


def show_multistage_example():
    """Create and show UI for multi-stage operation example."""
    ui = FunctionUI(multi_stage_operation)
    ui.setWindowTitle("Multi-Stage Progress Example")
    ui.show()
    return ui


def show_batch_example():
    """Create and show UI for batch processing example."""
    ui = FunctionUI(batch_processing)
    ui.setWindowTitle("Batch Processing Progress Example")
    ui.show()
    return ui


def show_variable_speed_example():
    """Create and show UI for variable speed operation example."""
    ui = FunctionUI(variable_speed_operation)
    ui.setWindowTitle("Variable Speed Progress Example")
    ui.show()
    return ui


def show_all_examples():
    """Create and show all progress callback examples.

    Opens multiple UI windows demonstrating different progress
    callback patterns and use cases.
    """
    examples = []

    # Simple operation
    ui1 = show_simple_example()
    examples.append(ui1)

    # Multi-stage operation
    ui2 = show_multistage_example()
    examples.append(ui2)

    # Batch processing
    ui3 = show_batch_example()
    examples.append(ui3)

    # Variable speed operation
    ui4 = show_variable_speed_example()
    examples.append(ui4)

    # Position windows in a grid to avoid overlap
    for idx, ui in enumerate(examples):
        x_offset = (idx % 2) * 400
        y_offset = (idx // 2) * 300
        ui.move(100 + x_offset, 100 + y_offset)

    return examples


# Main execution
if __name__ == "__main__":
    # Example usage: uncomment the line you want to test

    # Show individual example:
    # ui = show_simple_example()
    # ui = show_multistage_example()
    # ui = show_batch_example()
    # ui = show_variable_speed_example()

    # Show all examples at once:
    uis = show_all_examples()

    print("Progress callback examples created.")
    print("Click 'Execute' on any window to see progress updates.")
    print("")
    print("Expected behavior:")
    print("1. Progress bar appears when operation starts")
    print("2. Progress bar updates from 0-100%")
    print("3. Status text changes with meaningful messages")
    print("4. UI hides progress bar after completion")
