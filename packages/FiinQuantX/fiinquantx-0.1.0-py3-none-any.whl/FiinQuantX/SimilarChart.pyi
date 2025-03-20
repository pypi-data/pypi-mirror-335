from typing import Union
class SimilarChart(object):
    def __init__(self)->None: ...

    def plot(self, 
             Ticker: Union[str, list[str]], 
             t1: Union[str,None] = None, 
             t2: Union[str,None] = None
             )->None: 
        ...
    
        """Plot the similar chart of a Ticker."""

