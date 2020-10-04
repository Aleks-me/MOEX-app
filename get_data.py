import requests
import json
import time
from blist import blist
from datetime import datetime as dt

#######################################################################
#
# https://iss.moex.com - base url
# /iss/history – trade history
# /engines/stock/markets/shares - shares
#                       /bonds - bonds
#
# /boards/board_name - trading mode
#        /TQOB - federal bonds (Russian Federation)
#        /TQCB - corporate bonds
#        /TQBR - Т+2 mode
#        /TQOD - T+ eurobonds
# If no board selected in URL, then data will contain info
# across all boards.
#
# /securities.json?date=2019-12-01 - instrument for selected date
# /securities/GAZP.json - select company
#
# URL examples:
# Yandex trade from 2020-08-21 to 2020-08-31:
# https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/YNDX.json?from=2020-08-21&till=2020-08-31
#
# All bonds trade by 2020-08-31:
# https://iss.moex.com/iss/history/engines/stock/markets/bonds/securities.json?date=2020-08-31
#
# All info about SU52002RMFS1 federal bond for two months:
# https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQOB/securities/SU52002RMFS1.json?from=2020-07-01&till=2020-09-01
#
#######################################################################


class GetMOEXData:
    """Class to get data from MOEX.

    Params:
        market (str): select "bonds" or "shares".
        board (str): trading mode.

    Methods:
        stock_data_from_request (static): fetch stock data from decoded
                                          json and return a list.
        bonds_data_from_request (static): fetch bonds data from decoded
                                          json and return a list.
        get_all_date_dates: request market data by one day or between
                            dates for all instruments.
        get_target_date_dates: request market data by one day or between
                               dates for ONE selected instrument.
        get_target_all: all trade history for selected instrument.
    """

    def __init__(self, market: str = None, board: str = None):
        self.market = market
        self.board = board
        self.base = "https://iss.moex.com/iss/history/engines/stock/"
        self.data = blist()

    def __repr__(self):
        return (f'{self.__class__.__name__}:',
                f'{self.market!r}', f'{self.board!r}')

    def __str__(self):
        return (f"Selected market: {self.market}, board: {self.board}.",
                "See __doc__ for class and methods description.")

    @staticmethod
    def shares_data_from_req(json_decoded: dict) -> blist:
        """Helper function to take stock data from request line and
        return a list.

        Input:
            json_decoded: argument after json.loads()

        Return: list
        """

        data_line = blist()
        where_to_look = json_decoded["history"]["data"]
        if len(where_to_look) == 0:
            return data_line
        else:
            for line in where_to_look:
                board_name = line[0]
                trade_date = dt.strptime(line[1], "%Y-%m-%d").date()
                short_name = line[2]
                ticker = line[3]
                if line[4] is None:
                    num_trades = 0
                else:
                    num_trades = int(line[4])
                if line[5] is None:
                    value = 0
                else:
                    value = float(line[5])
                if line[6] is None:
                    p_open = 0
                else:
                    p_open = float(line[6])
                if line[7] is None:
                    low = 0
                else:
                    low = float(line[7])
                if line[8] is None:
                    high = 0
                else:
                    high = float(line[8])
                if line[11] is None:
                    p_close = 0
                else:
                    p_close = float(line[11])
                data_line.append([board_name, trade_date, short_name,
                                  ticker, num_trades, value,
                                  p_open, low, high, p_close])
        return data_line

    @staticmethod
    def bonds_data_from_req(json_decoded: dict) -> blist:
        """Helper function to take bonds data from request line and
        return a list.

        Input:
            json_decoded: argument after json.loads()

        Return: list
        """

        data_line = blist()
        where_to_look = json_decoded["history"]["data"]
        if len(where_to_look) == 0:
            return data_line
        else:
            for line in where_to_look:
                board_name = line[0]
                trade_date = dt.strptime(line[1], "%Y-%m-%d").date()
                short_name = line[2]
                secid = line[3]
                if line[4] is None:
                    num_trades = 0
                else:
                    num_trades = int(line[4])
                if line[5] is None:
                    value = 0
                else:
                    value = float(line[5])
                if line[13] is None:
                    p_open = 0
                else:
                    p_open = float(line[13])
                if line[6] is None:
                    low = 0
                else:
                    low = float(line[6])
                if line[7] is None:
                    high = 0
                else:
                    high = float(line[7])
                if line[8] is None:
                    p_close = 0
                else:
                    p_close = float(line[8])
                if line[30] is None:
                    nom_value = 0
                else:
                    nom_value = float(line[30])
                expire_date = dt.strptime(line[21], "%Y-%m-%d").date()
                unit = line[36]
                data_line.append([board_name, trade_date, short_name,
                                  secid, num_trades, value, p_open,
                                  low, high, p_close, expire_date,
                                  nom_value, unit])
        return data_line

    def get_all_date(self, day: str = None) -> blist:
        """ This will collect all info about all stock instruments that
        were traded during one day or between dates.

        MOEX returns only one day trades across all instruments that
        traded during that day.
        History for current day (today) is available only for the paid
        accounts, so free latest available == previous day.

        Use case: explore instruments for several days and select all
                  that fits the conditions.

        Input:
            day (str): day in format YYYY-MM-DD (default - None)

        Return: list
        """

        self.data = blist()
        where = f"markets/{self.market}/boards/{self.board}/"
        what = f"securities.json?date={day}"
        try:
            getter = requests.get(self.base + where + what)
            from_json = json.loads(getter.content)
            # Add fields to self.data with different helper
            # functions (depends on selected market):
            if self.market == "shares":
                get_data = self.shares_data_from_req(from_json)
            else:
                get_data = self.bonds_data_from_req(from_json)
            self.data += get_data
            if len(self.data) == 0:
                print("No information for that day:", day)
        except requests.exceptions.ConnectionError as ce1:
            print("GET failed on single request:", ce1)
        else:
            # If "total" > 100 we need several requests to get all data.
            # At first 100 results index is 0, then next 100 results
            # with index=100 and so on while -
            # "index" + "pagesize" < "total":
            ind_tot_pages = from_json["history.cursor"]["data"][0]
            index = 0
            total = ind_tot_pages[1]
            pagesize = ind_tot_pages[2]
            while (index + pagesize) < total:
                index += pagesize
                # Same request with different index:
                ic = f"&start={index}"
                try:
                    time.sleep(0.01)
                    wgetter = requests.get(self.base + where +
                                           what + ic)
                    w_json = json.loads(wgetter.content)
                    # Add fields to self.data with different helper
                    # functions (depends on selected market):
                    if self.market == "shares":
                        w_data = self.shares_data_from_req(w_json)
                    else:
                        w_data = self.bonds_data_from_req(w_json)
                    self.data += w_data
                except requests.exceptions.ConnectionError as ce2:
                    print("GET failed on while request.", ce2)
                    index -= 100
                    continue
        return self.data

    def get_target_date_dates(self,
                              target: str = None,
                              dfrom: str = None,
                              duntil: str = None) -> blist:
        """ This will collect all info about selected stock instrument
        that was traded during one day or between dates.

        When requesting target data results - approach with
        history.cursor won't work, 'cause there is no such fields in
        response. In that case we check if we have 100 results and
        if so - is there empty response after the next request.
        If list is empty, then first request was full, then return data.
        If list is not empty - make another request and check for
        empty-next response and so on until we get all data.

        Input:
            target (str): stock company ticker (TSLA, AAPL, etc.)
            dfrom (str): day in format YYYY-MM-DD to start collect
                         data from (default - None)
            duntil (str): day in format YYYY-MM-DD, last to collect
                          data (default - None)

        Return: list
        """

        self.data = blist()
        where = f"markets/{self.market}/boards/{self.board}/securities/"
        what = f"{target}.json?from={dfrom}&till={duntil}"
        try:
            getter = requests.get(self.base + where + what)
            from_json = json.loads(getter.content)
            # Add fields to self.data with different helper
            # functions (depends on selected market):
            if self.market == "shares":
                get_data = self.shares_data_from_req(from_json)
            else:
                get_data = self.bonds_data_from_req(from_json)
            self.data += get_data
            if len(self.data) == 0:
                print("No information for that period.")
        except requests.exceptions.ConnectionError as ce1:
            print("GET failed on single request:", ce1)
        else:
            if len(self.data) > 99:
                start = 100
                while start >= 0:
                    what_1 = f"{target}.json?from={dfrom}"
                    what_2 = f"&till={duntil}&start={start}"
                    what_start = what_1 + what_2
                    time.sleep(0.01)
                    getter_start = requests.get(self.base + where +
                                                what_start)
                    json_st = json.loads(getter_start.content)
                    # Add fields to self.data with different helper
                    # functions (depends on selected market):
                    if self.market == "shares":
                        data_start = self.shares_data_from_req(json_st)
                    else:
                        data_start = self.bonds_data_from_req(json_st)
                    if len(data_start) != 0:
                        self.data += data_start
                        start += 100
                    else:
                        start = -1
        return self.data

    def get_target_all(self, target: str = None) -> blist:
        """ This will collect all info about selected instrument
        for all period of it's existence.

        Input:
            target (str): stock company ticker or security ID
                          (YNDX, SU24021RMFS6, etc.)

        Return: list
        """

        self.data = blist()
        where = f"markets/{self.market}/boards/{self.board}/"
        what = f"securities/{target}.json"
        # This loop will get all data for all time for selected target:
        start_all = 0
        conn_failures = 0
        while start_all >= 0:
            try:
                time.sleep(0.01)
                getter_all = requests.get(self.base + where + what +
                                          f"?start={start_all}")
                json_all = json.loads(getter_all.content)
                # Add fields to self.data with different helper
                # functions (depends on selected market):
                if self.market == "shares":
                    get_data_all = self.shares_data_from_req(json_all)
                else:
                    get_data_all = self.bonds_data_from_req(json_all)
                if len(get_data_all) != 0:
                    self.data += get_data_all
                    start_all += 100
                else:
                    start_all = -1
            except requests.exceptions.ConnectionError as ce:
                print("Connection issue during loop. Retrying..:", ce)
                start_all -= 100
                continue
            if conn_failures > 3:
                print("Multiple connection issues -> data is not full.")
                break
        return self.data
