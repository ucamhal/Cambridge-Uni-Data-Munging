from operator import add
import re

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
        return reduce(add, _non_bracket_sections(string, "(", ")"), "")
    
    PUNCTUATION = set(list("!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"))
    
    @staticmethod
    def strippunctuation(string):
        "Replaces punctuation characters with spaces."
        return "".join(map(lambda x: " " if x in Transforms.PUNCTUATION else x, string))
    
    WS_PATTERN = re.compile("\s+")
    
    @staticmethod
    def condensewhitespace(string):
        "Collapses sequences of whitespace into single spaces."
        return Transforms.WS_PATTERN.sub(" ", string)
    
    @staticmethod
    def strip(string):
        "Strips whitespace from the beginning and end of the string."
        return string.strip()
    
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

def _non_bracket_sections(string, start, end):
    state = 0
    depth = 0
    for i, c in enumerate(string):
        if state == 0:
            if c == start:
                depth = 1
                state = 1
            elif c == end:
                yield string[i:]
                return
            else:
                yield c
        elif state == 1:
            if c == start:
                depth += 1
            elif c == end:
                depth -= 1
            if depth == 0:
                state = 0
