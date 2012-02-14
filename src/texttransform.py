from operator import add

# Could allow arbitrary function from module
class Transforms(object):
    NOT_TRANSFORMS = {'list_transforms', 'get_transform_funcs', 'help_string', 
                      'NOT_TRANSFORMS'}
    
    @staticmethod
    def ignorecase(string):
        "Reduces the input to lower case."
        return string.lower()
    
    @staticmethod
    def stripbrackets(string):
        """
        Strips brackets and their contents out of a string. Stripping stops if incorectly
        nested brackets are encountered."""
        return reduce(add, _find_bracket_sections(string, "(", ")"), "")
    
    @staticmethod
    def list_transforms():
        return {key for key in vars(Transforms).keys() 
                if not (key.startswith("__") or key in Transforms.NOT_TRANSFORMS)}
    
    @staticmethod
    def help_string():
        return " | ".join(["{}: {}".format(name, getattr(Transforms, name).__doc__) 
                for name in Transforms.list_transforms()])
    
    @staticmethod
    def get_transform_funcs(names):
        return [getattr(Transforms, tx_name) for tx_name in names]

def _find_bracket_sections(string, start, end):
    assert start != end
    i = 0
    while i < len(string):
        c = string[i]
        if c == start or c == end:
            try:
                end = _match_bracket(string, i, start, end)
                i = end
            except ValueError:
                yield string[i:]
                return
        else:
            yield string[i]
        i = i + 1

def _match_bracket(string, startIndex, start, end):
    assert string[startIndex] in [start, end]
    i = startIndex
    depth = 0
    while i < len(string):
        c = string[i]
        if c == start:
            depth = depth + 1
        elif c == end:
            depth = depth - 1
        
        if depth < 0:
            break
        elif depth == 0:
            return i
        i = i + 1
    raise ValueError("Mis-matched bracket nesting.")
    