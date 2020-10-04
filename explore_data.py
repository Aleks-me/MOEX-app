import pandas as pd
import numpy as np
import blist


class EDA:
    """Group data, create dataframe, use filters to explore instruments.

    Methods:
        liquidity (static): trade volume by liquidity - low/medium/high.
        choose_share: take data from request and return Pandas
                      dataframe with some counts and filters.
        choose_bond: take data from request and return Pandas
                      dataframe with some counts and filters.
    """

    def __init__(self):
        self.df = pd.DataFrame()

    def __repr__(self):
        return (f"{self.__class__.__name__}:",
                print("First 10 rows:", self.df.head(10).to_string()),
                self.__class__.__doc__)

    def __str__(self):
        return print(self.df.to_string())

    @staticmethod
    def liquidity(num: float) -> str:
        """Categorizing trade volume by liquidity - low/medium/high.
        """
        if num < 1000000:
            return "low"
        elif 1000000 <= num < 10000000:
            return "medium"
        elif num >= 10000000:
            return "high"

    # I know that in reality some things are calculated in another way
    # but i need some raw numbers here (this is not a fundamental
    # analysis):
    def choose_share(self, input_data: [blist, list]) -> pd.DataFrame:
        """ Return Pandas dataframe with some calculated stuff ready
            for filtering and instrument selection.

        Input:
            input_data (list): list with share parameters.

        Returns:
            pd.DataFrame: table with parameters.
        """

        cols = ["name", "id", "num_trades", "trade_value",
                "trading_liq", "close_price", "volatility", "vol_pct"]
        self.df = pd.DataFrame(columns=cols)
        for line in input_data:
            close_price = round(line[-1], 2)
            max_min_gap = round(np.abs(line[-3] - line[-2]), 2)
            if close_price == 0:
                max_min_gap_pct = 0.0
            else:
                max_min_gap_pct = round(
                    (np.abs(line[-3] - line[-2]) / close_price)*100, 2)
            trading_liq = self.liquidity(line[5])
            row = ([line[2], line[3], line[4], line[5],
                   trading_liq, close_price, max_min_gap,
                    max_min_gap_pct])
            to_df = pd.Series(row, cols)
            self.df = self.df.append(to_df, ignore_index=True)
        return self.df

    def choose_bond(self, input_data: [blist, list]) -> pd.DataFrame:
        """ Return Pandas dataframe with some calculated stuff ready
            for filtering and instrument selection.

        Input:
            input_data (list): list with bonds parameters.

        Returns:
            pd.DataFrame: table with parameters.
        """

        cols = ["name", "id", "num_trades", "trade_value",
                "close_price", "nom_value", "expire_date", "unit"]
        self.df = pd.DataFrame(columns=cols)
        for line in input_data:
            close_price = round(line[-4], 2)
            row = ([line[2], line[3], line[4], line[5],
                   close_price, line[-2], line[-3], line[-1]])
            to_df = pd.Series(row, cols)
            self.df = self.df.append(to_df, ignore_index=True)
        return self.df
