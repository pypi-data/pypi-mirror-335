from .vrint import Vrint
import functools
# Create a single instance of Vrint
vrint = Vrint()

# Decorator for function-scoped verbose control
def with_vrint_state(func):
    """
    Decorator that allows a function to accept a vrint_state parameter
    to control verbosity within that function.
    
    Usage:
    @with_vrint_state
    def my_func():
        vrint("This message may or may not be printed")
        
    my_func(vrint_state=vrint.verbose)  # Will print the message
    my_func(vrint_state=vrint.quiet)    # Will not print the message
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if first arg is a VerboseStateObject (from vrint.verbose or vrint.quiet)
        vrint_state = None
        if args and hasattr(args[0], 'vrint_obj') and hasattr(args[0], 'value'):
            vrint_state = args[0]
            args = args[1:]  # Remove the vrint_state from args
        else:
            # Check for explicit vrint_state in kwargs
            vrint_state = kwargs.pop('vrint_state', None)
        
        # Store original state
        original_state = vrint._verbose
        
        try:
            # Set temporary state if provided
            if vrint_state is not None:
                if hasattr(vrint_state, 'value'):
                    vrint._verbose = vrint_state.value
                else:
                    vrint._verbose = bool(vrint_state)
            
            # Call function with new state
            return func(*args, **kwargs)
        finally:
            # Restore original state
            vrint._verbose = original_state
            
    return wrapper

# Export the vrint instance and the decorator
__all__ = ['vrint', 'with_vrint_state']