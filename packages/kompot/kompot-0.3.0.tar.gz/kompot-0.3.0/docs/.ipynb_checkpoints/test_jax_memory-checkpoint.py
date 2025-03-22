"""Test script to identify JAX memory error types by creating increasingly larger arrays."""

import jax
import jax.numpy as jnp
import numpy as np
import traceback
import gc
import time

def test_with_size(size_mb):
    """Test with a specific array size in MB."""
    # Calculate dimensions for the desired size in MB
    # float32 = 4 bytes per element
    elements = size_mb * (1024 * 1024) // 4
    
    # Square array where possible
    side = int(np.sqrt(elements))
    
    try:
        print(f"\nAttempting to create and evaluate a {size_mb} MB JAX array...")
        # Create array
        shape = (side, side)
        print(f"Array shape: {shape} (float32)")
        start = time.time()
        array = jnp.ones(shape, dtype=jnp.float32)
        print(f"Array created in {time.time() - start:.2f}s, forcing evaluation...")
        
        # Force evaluation
        result = array.block_until_ready()
        print(f"Success! Array evaluated in {time.time() - start:.2f}s")
        return True
    except Exception as e:
        print(f"\nFAILED with {size_mb} MB array")
        print(f"Error type: {type(e).__name__}")
        print(f"Error module: {type(e).__module__}")
        print(f"Error message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("JAX version:", jax.__version__)
    
    # Test with increasingly larger arrays
    sizes = [100000, 200000, 300000, 400000, 500000]
    
    for size in sizes:
        gc.collect()  # Force garbage collection between tests
        success = test_with_size(size)
        if not success:
            print(f"\nError occurred at {size} MB. Testing a few more larger sizes to confirm pattern.")
            
            # Try a few more sizes to confirm error pattern
            for bigger_size in [size * 2, size * 5]:
                gc.collect()
                try:
                    print(f"\nRetrying with {bigger_size} MB to observe error pattern...")
                    array = jnp.ones((int(np.sqrt(bigger_size * (1024 * 1024) // 4)),
                                     int(np.sqrt(bigger_size * (1024 * 1024) // 4))))
                    result = array.block_until_ready()
                    print("Unexpected success!")
                except Exception as e:
                    print(f"Confirmed error type: {type(e).__name__}")
                    print(f"From module: {type(e).__module__}")
            
            break