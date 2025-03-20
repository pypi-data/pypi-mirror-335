import pandas as pd
from typing import Union
from datetime import datetime

class BarData:
    def __init__(self, data) -> None:
        self.__private_attribute: pd.DataFrame = data
        self.timestamp: Union[str, datetime]
        self.open: float
        self.high: float
        self.low: float
        self.close: float
        self.volume: int
        self.ticker: str
        self.bu: int
        self.sd: int
        self.fb: float
        self.fs: float
        self.fn: float
        
    def to_dataFrame(self) -> pd.DataFrame: ...

class BarDataUpdate:
    def __init__(self, data) -> None:
        self.__private_attribute: pd.DataFrame
        self.timestamp: Union[str, datetime]
        self.open: float
        self.high: float
        self.low: float
        self.close: float
        self.volume: int
        self.ticker: str
        self.bu: int
        self.sd: int
        self.fb: float
        self.fs: float
        self.fn: float
        
    def to_dataFrame(self) -> pd.DataFrame: ...

class GetBarData:
    def __init__(self, 
                 tickers: Union[str, list],
                 by: str, 
                 from_date: Union[str, datetime, None], 
                 to_date: Union[str, datetime, None],
                 adjusted: bool, 
                 fields: list, 
                 period: int) -> None: ...
    
    def get(self) -> BarData: ...

class RealTimeData:
    
    """
    RealTimeData is a class that represents a real-time data of a stock. 
    This class is a structure that contains all the information of a stock at a specific time. 
    You can use to_dataFrame() method to convert this class to a pandas DataFrame.
    """
    
    def __init__(self, data: pd.DataFrame) -> None:
        self.__private_attribute = data
        self.Ticker: str
        self.TotalMatchVolume: int
        self.MarketStatus: str
        self.TradingDate: str
        self.ComGroupCode: str
        self.ReferencePrice: float
        self.Open: float
        self.Close: float
        self.High: float
        self.Low: float
        self.Change: float
        self.ChangePercent: float
        self.MatchVolume: int
        self.MatchValue: float
        self.TotalMatchValue: float
        self.TotalBuyTradeVolume: int
        self.TotalSellTradeVolume: int
        self.TotalDealVolume: int
        self.TotalDealValue: float
        self.ForeignBuyVolumeTotal: int
        self.ForeignBuyValueTotal: float
        self.ForeignSellVolumeTotal: int
        self.ForeignSellValueTotal: float
        self.Bu: int
        self.Sd: int
        
    def to_dataFrame(self) -> pd.DataFrame: ...