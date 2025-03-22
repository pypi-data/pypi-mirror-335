from pickle import dump, load

class Storable:
    """A parent class for classes that should be storable as a pickle file."""
    
    def save(self, filepath):
        """Save the object as a pickle file to filepath."""
        with open(filepath, 'wb') as f:
            dump(self, f)
        return self
    
    def load(filepath):
        """Load a a object from a pickle file at filepath."""
        with open(filepath, 'rb') as f:
            self = load(f)
            return self