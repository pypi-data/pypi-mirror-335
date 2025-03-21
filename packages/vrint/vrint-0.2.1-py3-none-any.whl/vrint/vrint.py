import functools

class VerboseStateObject:
    """Smart state object that works for function scope and per-call control"""
    def __init__(self, vrint_obj, value):
        self.vrint_obj = vrint_obj
        self.value = value
    
    def __bool__(self):
        return self.value
    
    def __call__(self, func_result):
        """Enable syntax: vrint.verbose(myfunc())"""
        # Function was already called, this just modifies state temporarily
        return func_result

class Vrint:
    def __init__(self):
        print("Initializing Vrint")
        self._verbose = False
    
    def __call__(self, message, state=None):
        should_print = self._verbose
        if state is not None:
            if hasattr(state, 'value'):
                should_print = state.value
            else:
                should_print = bool(state)
        
        if should_print:
            print(message)
    
    @property
    def verbose(self):
        """Smart property that changes state globally when accessed directly"""
        self._verbose = True
        return VerboseStateObject(self, True)
    
    @property
    def quiet(self):
        """Smart property that changes state globally when accessed directly"""
        self._verbose = False
        return VerboseStateObject(self, False)
    
    def __getattr__(self, name):
        if name == 'verbose':
            return self.verbose
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
