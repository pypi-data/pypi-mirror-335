from typing import Union
class FindDateCorrelation(object):
    def __init__(self) -> None: ...
    
    def intraday_Correlation(self, Ticker: Union[str, list[str]], Timeframe: str, 
                            t1: Union[str, None] = None, t2: Union[str, None] = None, method: str = "pearson correlation",
                            year: Union[int,None] = 1) -> None:...
        