from typing import Any, Dict, List, Optional

class ndict(dict):
    """
    Multi-level (nested) dictionary. Automatically adds new levels
    """

    def __missing__(self, key: Any) -> 'ndict':
        self[key] = ndict()
        return self[key]
    
    def extract(self, extracted: Optional[List] = None, _seen: Optional[set] = None) -> List:
        """
        Extracts the leaf (deepest) level of the multi-level dictionary.
        Will NOT recurse into standard dictionaries.
        
        Args:
            extracted: Optional list to store results. If None, a new list is created.
            _seen: Internal parameter to detect circular references
        
        Returns:
            List containing the items at the leaves
        """
        # Create new list for this call to avoid modifying shared state
        local_extracted = [] if extracted is None else extracted
        seen = set() if _seen is None else _seen
        
        # Protect against circular references
        if id(self) in seen:
            return local_extracted
        seen.add(id(self))
        
        for v in self.values():
            if isinstance(v, ndict):
                v.extract(local_extracted, seen)
            else:
                local_extracted.append(v)
        return local_extracted
    
    @staticmethod
    def extract_all(d: Dict, extracted: Optional[List] = None, _seen: Optional[set] = None) -> List:
        """
        Extracts the leaf (deepest) level of the multi-level dictionary.
        WILL recurse into standard dictionaries.
        
        Args:
            d: Dictionary to extract from
            extracted: Optional list to store results. If None, a new list is created.
            _seen: Internal parameter to detect circular references
            
        Returns:
            List containing the items at the leaves
        """
        local_extracted = [] if extracted is None else extracted
        seen = set() if _seen is None else _seen
        
        # Protect against circular references
        if id(d) in seen:
            return local_extracted
        seen.add(id(d))
        
        for v in d.values():
            if isinstance(v, dict):
                ndict.extract_all(v, local_extracted, seen)
            else:
                local_extracted.append(v)
        return local_extracted
    
    def flatten(self, flattened: Optional[Dict] = None, parent_key: str = '', 
               sep: str = "_", _seen: Optional[set] = None) -> Dict:
        """
        Flattens the nested dictionary into a single-level dictionary.
        
        Args:
            flattened: Optional dict to store results. If None, a new dict is created.
            parent_key: Parent key to prepend to the flattened key
            sep: Separator string to place between key levels
            _seen: Internal parameter to detect circular references
            
        Returns:
            A flattened, single-level dictionary
        """
        local_flattened = {} if flattened is None else flattened
        seen = set() if _seen is None else _seen
        
        # Protect against circular references
        if id(self) in seen:
            return local_flattened
        seen.add(id(self))
        
        for k, v in self.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, ndict):
                v.flatten(local_flattened, new_key, sep, seen)
            else:
                local_flattened[new_key] = v
        return local_flattened
    
    @staticmethod
    def flatten_all(d, flattened=None, parent_key='', sep='_'):
        """
        Flattens the nested dictionary into a single-level dictionary. The keys for flattened dictionary are the 
        concatenated keys for each level in ndict: d[1][2][3] -> d[1_2_3]. WILL recurse into standard dictionaries.
        To recurse into only ndicts, see flatten.
        : param flattened: A dictionary to store the results
        : param parent_key: Parent key to prepend to the flattened key
        : param sep: Separator string to place between key levels
        : returns a flattened, single-level dictionary
        """
        if flattened is None:
            flattened = {}
        for k, v in d.items():
            new_key = parent_key + sep + str(k) if parent_key else str(k)
            if isinstance(v, dict):
                ndict.flatten_all(v, flattened=flattened, parent_key=new_key, sep=sep)
            else:
                flattened[new_key] = v
        return flattened