class ClassyDict(dict):
    """A dictionary that supports dot notation access, including nested dicts."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = ClassyDict(value)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'ClassyDict' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = ClassyDict(value)
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'ClassyDict' object has no attribute '{key}'") 