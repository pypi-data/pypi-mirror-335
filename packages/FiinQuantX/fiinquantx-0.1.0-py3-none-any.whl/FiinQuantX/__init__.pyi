from datetime import datetime
from typing import Union
import pandas as pd

from .FiinIndicator import _FiinIndicator
from .Fetch_Trading_Data import Fetch_Trading_Data
from .Trading_Data_Stream import Trading_Data_Stream
from .DateCorr import FindDateCorrelation
from .Rebalance import Rebalance
from .SimilarChart import SimilarChart
# from .Screening import Screening

class FiinSession:
    """
    This class is used to create a session to access FiinQuant.
    """
    def __init__(self, username: str, password: str):...

    def login(self) -> FiinSession: ...
        
    def FiinIndicator(self) -> _FiinIndicator: 
        """
        FiinIndicator class is used to calculate technical indicators for stock market data.
        """
    def Trading_Data_Stream(self, tickers: list, callback: callable) -> Trading_Data_Stream: 
        """
        Using this class to stream real-time stock market matching data. Using start() to start streaming and stop() to stop streaming.
        The variable _stop is used to check if the streaming is stopped or not."""
    def Fetch_Trading_Data(self, realtime: bool, tickers: list, fields: list, adjusted: bool, 
                           period: Union[int, None] = None, by: str='1m',
                           from_date: Union[str, datetime, None] = None,
                           to_date: Union[str, datetime, None] = None,
                           callback: callable = None,
                           wait_for_full_timeFrame: bool = False,
                           lasted: Union[bool, None] = None) -> Fetch_Trading_Data: 

        """summary:
        
        This function is used to fetch trading data from the server. The data can be fetched in real-time or historical data.
        lasted only required when realtime = False. When lasted=True, the last candle is an unfinished candle. When lasted=False, the last candle is a completed historical candle.
        callback and wait_for_full_timeFrame only required when realtime = True. Method stop() is used to stop receiving data (only needed when realtime = True).
        
        Args:
            realtime (bool): Real-time data or not.
            tickers (list): List of tickers.
            fields (list): List of fields. Including: 'open', 'high', 'low', 'close', 'volume', 'bu', 'sd', 'fb', 'fs', 'fn'. Can use 'full' for get all fields.
            adjusted (bool, optional): Adjusted price or unadjusted price. Default to True (Adjusted).
            period (Union[int, None], optional): Number of most recent candles. Default to None.
            by (str, optional): Unit of time: '1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d'. Default to '1m'.
            from_date (Union[str, datetime, None], optional): The furthest time of data. Default to None.
            to_date (Union[str, datetime, None], optional): Latest time of data. Default to None.
            callback (callable, optional): User-defined callback function for manipulating data. Default to None.
            wait_for_full_timeFrame (bool, optional): Wait until the candle is over to get data or not. Default to False.
            lasted (Union[bool, None], optional): Last candle is unfinished or not. Default to None.
        Methods:
            get_data(): Get data from the server.
            stop(): Stop receiving data (only need when realtime = True).
        """
    def FindDateCorrelation(self) -> FindDateCorrelation: 
        """
        Using this class to find the correlation between today data and the past data.
        """
    def Rebalance(self) -> Rebalance: 
        """Use this class for Rebalance."""
    def SimilarChart(self) -> SimilarChart: 
        """Use this class for Find Similar Pattern."""
    # def Screening(self, conditions: dict, from_date: Union[str, None] = None, period: Union[int, None] = None) -> Screening: 
    #     """Use this class for Screening."""
        
class FindDateCorrelation(object):
    """
    Using this class to find the correlation between today data and the past data.
    """
    def __init__(self) -> None: ...
    
    def intraday_Correlation(self, Ticker: Union[str, list[str]], Timeframe: str, 
                            t1: str = None, t2: str = None, method: str = "pearson correlation",
                            year: int = 1) -> None:
        """
        Plot the normalized price of a stock over time, comparing the current day to the past days.
        method (str, optional): Distance measurement. Default to "pearson correlation".
        For simple, use '1' for euclidean distance, '2' for dynamic time warping, 
        '3' for pearson correlation, '4' for cosine similarity.
        """

        
class Rebalance(object):
    """Use this class for Rebalance."""
    def __init__(self) -> None:...
    def get(self, Budget: int, Ticker: str) -> pd.DataFrame:...
class SimilarChart(object):
    """Use this class for find Similar Pattern."""
    def __init__(self)->None:...
    def plot(self, Ticker: Union[str, list[str]], t1:Union[str,None] = None, t2:Union[str,None] = None)->None:
        """Plot the similar chart of a Ticker."""
    
# class Screening:
#     """
#     This class is used to screen stocks based on the conditions provided. The conditions are in the form of a dictionary.
#     """
#     def __init__(self, conditions: dict, from_date: Union[str, None] = None, period: Union[int, None] = None):
#         """
#         Args:
#             conditions (dict): Conditions for screening.
          
#             start_date (Union[str, None], optional): Start date. Default to None.
#             period (Union[int, None], optional): Period. Default to None.
#         """
#     def screen_data(self) -> int: ...
class RealTimeData:
    """
    RealTimeData is a class that represents a real-time data of a stock. This class is 
    a structure that contains all the information of a stock at a specific time. You can use 
    to_dataFrame() method to convert this class to a pandas DataFrame.
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

class BarDataUpdate:
    """
    This class is used to store both the real-time data and the historical data of a stock.
    You can use to_dataFrame() method to convert this data to a pandas.
    
    """
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

