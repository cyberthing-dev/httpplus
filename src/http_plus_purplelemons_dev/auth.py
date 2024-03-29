
from json import dumps
from random import getrandbits as grb
from base64 import b64encode

class Attrs:
    """
    Create javascript-like objects where attributes can be accessed
    via indices or dot notation.
    """
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
    def __getitem__(self, key): return self.__dict__[key]
    def __setitem__(self, key, value): self.__dict__[key] = value
    def __delitem__(self, key): del self.__dict__[key]
    def __getattr__(self, key): return self.__dict__[key]
    def __setattr__(self, key, value): self.__dict__[key] = value
    def __delattr__(self, key): del self.__dict__[key]
    def __str__(self): return dumps(self.__dict__, indent=2)
    def __repr__(self): return self.__str__()

class Auth:
    """
    Handles authorization conveniently!

    Example:
    >>> auth = Auth()
    >>> token = auth.generate(username="admin", password="password")
    >>> auth.check(token)
    True
    >>> auth[token]
    Attrs(username="admin", password="password")
    >>> auth.revoke(token)
    Attrs(username="admin", password="password")
    """

    def __init__(self):
        self.authorizations:dict[str,Attrs] = {}

    def __getitem__(self, token:str) -> Attrs:
        return self.authorizations[token]
    
    def __setitem__(self, token:str, data:Attrs):
        self.authorizations[token] = data

    def __delitem__(self, token:str):
        del self.authorizations[token]

    def check(self, token:str) -> bool:
        """
        Check if the token is valid.

        Args:
            token (str): The token to check.

        Returns:
            bool: Whether the token is valid or not.
        """
        return token in self.authorizations

    def generate(self, /, token_size:int=128, **kwargs) -> str:
        """
        Generate a new authorization and saves given data to it for later retrieval.

        Args:
            token_size (int): The size of the token in bits. Defaults to 128.
            **kwargs: The data to save to the authorization.

        Returns:
            str: The authorization token.
        """
        token = b64encode(str(grb(token_size)).encode()).decode()
        self.authorizations[token] = Attrs(**kwargs)
        return token

    def revoke(self, token:str) -> Attrs:
        """
        Revoke an authorization token and returns an Attrs object of the data associated with it.

        Args:
            token (str): The token to revoke.

        Returns:
            Attrs: The data associated with the token.
        """
        data = self.authorizations[token]
        del self[token]
        return data
