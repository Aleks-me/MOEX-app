"""
There are many sites in .ru internet segment that are gathering data
from the Moscow Exchange. Some of them are showing information for free,
for some of them you'll need ot pay for monthly subscription.

Since MOEX give free access to trading history (but not for the present
day) we can use this info to help us make an investment decisions.

-----
Main ideas of all this code are:
- collect data for selected instrument or instruments (you choose share
  or bond for some date or between some dates, make request and get your
  data back from Moscow Exchange);
- save data to MYSQL database;
- explore data to find an instrument which is not much volatile,
  has good liquidity, not that expensive to by and has a potential
  to earn some money. This comes through your trading experience and
  there is no exact values on which to filter instruments :(

This analysis will be valid as an idea for further investigation.

Little advice for stocks:
Minimum possible action is to calculate company coefficients (EV/EBITDA,
PV/EBITDA, P/BV and etc.) and compare them to coefficients of other
companies in specific economy field (you've selected company from).

Little advice for bonds:
Decision to buy bonds must come through several things:
- understanding of the current key interest rate of the
  Russian Federation central bank;
- looking on the bond expiration date and current bond value.

"""
import os
from get_data import GetMOEXData
from save_load_data import SLDataMYSQL
from explore_data import EDA
from datetime import date

"""
[Access to the Database]
secret = "your_password"
address = "127.0.0.1" (or address = "localhost")
db_name = "MOEX"
user = "your_user_name"
"""
secret = os.environ["PASSWORD_MOEX"]
address = "localhost"
db_name = "MOEX"
user = "aleks"

if __name__ == "__main__":
    # What I'm seeking for:
    sh_data = GetMOEXData("shares", "TQBR")
    fb_data = GetMOEXData("bonds", "TQOB")

    # Get all data for one day:
    shares_day = sh_data.get_all_date("2020-09-08")
    bonds_day = fb_data.get_all_date("2020-09-08")
    explore = EDA()

    df_sh = explore.choose_share(shares_day)
    print(df_sh.loc[df_sh["trading_liq"] == "high"].
          sort_values(by=["vol_pct"]).to_string(), "\n")

    df_fb = explore.choose_bond(bonds_day)
    print(df_fb.loc[df_fb["expire_date"] < date(2022, 1, 1)].
          sort_values(by=["expire_date"]).to_string(), "\n")

    # Get selected instrument data for 6 months:
    inst_data = sh_data.get_target_date_dates("MTSS", "2020-03-01",
                                              "2020-09-09")
    # Save data for offline use:
    sl_data = SLDataMYSQL(address, db_name, user, secret)
    sl_data.write_to_mysql(inst_data, "Shares")
    saved_data = sl_data.query_db("Shares")
