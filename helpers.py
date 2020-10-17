"""
Some helper-functions to reduce the size of some methods (make
them less ugly).

"""
from blist import blist
from datetime import datetime as dt


def shares_helper(inp: list) -> [list, blist]:
    dl = blist()
    if len(inp) == 0:
        return dl
    else:
        for line in inp:
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
            dl.append([board_name, trade_date, short_name,
                       ticker, num_trades, value,
                       p_open, low, high, p_close])
    return dl


def bonds_helper(inp: list) -> [list, blist]:
    dl = blist()
    if len(inp) == 0:
        return dl
    else:
        for line in inp:
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
            if line[21] is None:
                expire_date = 0
            else:
                expire_date = dt.strptime(line[21],
                                          "%Y-%m-%d").date()
            unit = line[36]
            dl.append([board_name, trade_date, short_name,
                       secid, num_trades, value, p_open,
                       low, high, p_close, expire_date,
                       nom_value, unit])
    return dl
