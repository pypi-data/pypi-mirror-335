from typing import Union
class Trading_Data_Stream:
    """Using this class to stream real-time stock market matching data. """
    def __init__(self, tickers: Union[list[str],str], callback: callable) -> None:
        self.tickers: Union[list[str],str]
        self._stop: bool
        
    def start(self) -> None: ...
        
    def stop(self) -> None: ...

