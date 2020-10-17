import requests
import json
import time
from blist import blist
from helpers import shares_helper, bonds_helper

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

        where_to_look = json_decoded["history"]["data"]
        data_line = shares_helper(where_to_look)
        return data_line

    @staticmethod
    def bonds_data_from_req(json_decoded: dict) -> blist:
        """Helper function to take bonds data from request line and
        return a list.

        Input:
            json_decoded: argument after json.loads()

        Return: list
        """

        where_to_look = json_decoded["history"]["data"]
        data_line = bonds_helper(where_to_look)
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
