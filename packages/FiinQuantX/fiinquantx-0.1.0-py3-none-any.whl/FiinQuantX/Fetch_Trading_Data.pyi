import pandas as pd
from typing import Union
from datetime import datetime
class Fetch_Trading_Data:
    def __init__(self,
                 realtime: bool,
                 tickers: Union[list[str], str], 
                 fields:list, 
                 adjusted: bool, 
                 period: Union[int, None] = None,
                 by: str = '1m',
                 from_date: Union[str, datetime, None] = None,
                 to_date: Union[str, datetime, None] = None,
                 callback: callable = None,
                 wait_for_full_timeFrame: bool = False,
                 lasted: Union[bool, None] = None) -> None:
            self._stop: bool
       
    def get_data(self) -> pd.DataFrame: ...
    def stop(self) -> None: ...

        
  