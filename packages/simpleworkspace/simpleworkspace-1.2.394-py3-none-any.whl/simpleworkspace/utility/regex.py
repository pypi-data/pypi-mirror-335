import re as _re


def Replace(pattern: str, replacement: str, message:str, limit:int=None):  
    """:see: `Regex.Replace`"""
    return Regex(pattern).Replace(replacement, message, limit)

def Match(pattern: str, string: str, limit:int=None):  
    """:see: `Regex.Match`"""
    return Regex(pattern).Match(string, limit=limit)

def MatchFirst(pattern: str, string: str):  
    """:see: `Regex.MatchOne`"""
    return Regex(pattern).MatchFirst(string)

def Test(pattern:str, string:str):
    """:see: `Regex.Test`"""
    return Regex(pattern).Test(string)

class Regex:
    def __init__(self, pattern:str):
        ''' 
        :param pattern: The regex pattern, with flags following in the format "/pattern/flags". Default flag is multiline
        '''
        self.pattern, self.flags = self._ParsePattern(pattern)
        self._preppedRegex = _re.compile(self.pattern, self.flags)

    def Test(self, string:str) -> bool:
        """
        Checks if there is at least one match of the regex pattern in the string.

        :param string: The string to search for matches in.
        :return: True if at least one match is found, False otherwise.
        """
        return self._preppedRegex.search(string) is not None

    def Match(self, string: str, limit:int=None) -> (tuple[tuple[str]] | None):  
        """
        Finds all matches of the regex pattern in the string

        :param string: The string to search pattern in.
        :param limit: stop search after specified amount of matches
        :return:
            A 2D array of matches and their corresponding capture groups, or None if no matches found.
            Example: ((match1, capture1, capture2), (match2, capture1, capture2))

        Example Usage:
        >>> Match(r"/hej (.*?) /is", "hej v1.0 hej v2.2 hejsan v3.3")
        (('hej v1.0 ', 'v1.0'), ('hej v2.2 ', 'v2.2'))
        """

        iterator = self._preppedRegex.finditer(string)
        if(limit is not None):
            from itertools import islice
            iterator = islice(iterator, limit)

        results = tuple((i.group(0), *i.groups()) for i in iterator)
        if len(results) == 0:
            return None
        return results
    
    def MatchFirst(self, string: str) -> tuple[str]|None:  
        """
        Finds only first match of the regex pattern in the string.

        :param string: The string to search pattern in.
        :return:
            An array containing the match itself and its capture groups, or None if no match is found.
            Example: (match, capture1, capture2)

        Example Usage:
        >>> Match(r"/hej (.*?) /is", "hej v1.0 hej v2.2")
        ('hej v1.0 ', 'v1.0')
        """

        #we could use self.Match with limit set to 1, but using search uses less overhead therefore is a little faster
        matchRes = self._preppedRegex.search(string)
        if matchRes is None:
            return None
        return (matchRes.group(0), *matchRes.groups())

    def Replace(self, replacement: str, message:str, limit:int=None) -> str:  
        """
        Replaces all occurrences of the regex pattern in the message with the given replacement.

        :param replacement: The replacement string for matches. Back reference to capture groups with \\1...\\100 or \\g<1>...\\g<100>
        :param message: The string to search for matches in.
        :param limit: limits max amount of replacements to perform

        :Return: The message with all matches replaced by the replacement string or same text if not matches

        Example Usage:
        >>> RegexReplace(r"/hej (.*?) /i", r"bye \\1 or \\g<1> ", "hej v1.0 hej v2.2 hejsan v3.3") 
        "bye v1.0 or v1.0 bye v2.2 or v2.2 hejsan v3.3"
        """

        if(limit is None):
            limit = 0 #default value for no limit
        return  self._preppedRegex.sub(replacement, message, count=limit)

    def _ParsePattern(self, pattern:str):
        """
        Parses the given regex pattern into its regex pattern and flags.
        
        :param pattern: The regex pattern, with flags following in the format "/pattern/flags".
        :raises Exception: If pattern does not have the format "/pattern/flags".

        :return: A tuple containing the regex pattern and flags.
        """
        flagSplitterPos = pattern.rfind("/", 1)
        if pattern[0] != "/" or flagSplitterPos == -1:
            raise ValueError("Pattern need to have format of '/pattern/flags'")
        regexPattern = pattern[1:flagSplitterPos]  # remove first slash
        flags = pattern[flagSplitterPos + 1 :]

        flagParamValue = 0
        if 'i' in flags:
            flagParamValue |= _re.IGNORECASE
        if 's' in flags:
            flagParamValue |= _re.DOTALL
        if 'm' in flags:
            flagParamValue |= _re.MULTILINE

        if not (flagParamValue & _re.DOTALL) and not (flagParamValue & _re.MULTILINE):
            flagParamValue |= _re.MULTILINE #default to use multiline

        return (regexPattern, flagParamValue)


def Glob(pattern:str, string:str, ignoreCase=True):
    '''
    Uses glob pattern to test for match in string. A fully matching string is considered a match.
    
    Usage:
    - '*' matches zero or more characters.
    - '?' matches exactly one character.
    - To escape characters wrap the character in brackets. For example, '[?]' would be a literal question mark.\n
      [seq]  matches any character in seq and supports ranges such as [a-z]\n
      [!seq] matches any char not in seq
      
    '''
    import fnmatch
    import re

    regexFlags = re.IGNORECASE if ignoreCase else 0
    res = re.compile(fnmatch.translate(pattern), regexFlags).match(string)
    if(res is None):
        return False
    return True
