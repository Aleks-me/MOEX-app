import sqlalchemy as sql
import sqlalchemy.exc
import blist


class SLDataMYSQL:
    """Operate with MYSQL database.

    Methods:
        write_to_mysql: insert selected data to MYSQL db.
        query_db: select from MYSQL db.
    """

    def __init__(self, address: str, db_name: str,
                 username: str, passw: str):
        self.address = address
        self.db_name = db_name
        self.username = username
        self.password = passw
        self.engine_mysql = sql.create_engine(
            f'mysql+pymysql://{self.username}:{self.password}@' +
            f'{self.address}/{self.db_name}')
        self.connection = self.engine_mysql.connect()
        self.metadata = sql.MetaData()

    def __repr__(self):
        return (f"{self.__class__.__name__}:",
                f"Connect to: {self.address}, DB name: {self.db_name}",
                f"User: {self.username}",
                self.__class__.__doc__)

    def __str__(self):
        return (f"Connect to: {self.address}, DB name: {self.db_name}",
                f"User: {self.username}")

    def write_to_mysql(self, input_data: [blist, list],
                       table_name: str):
        """ Insert to DB.

        Input:
            input_data (list): list with bond or share parameters.
            table_name (str): table in MYSQL db to insert to.
        """

        table = sql.Table(f'{table_name}', self.metadata,
                          autoload=True,
                          autoload_with=self.engine_mysql)
        if len(input_data) == 0:
            print("There is no data from request to write.")
        if table_name == "Shares":
            for line in input_data:
                try:
                    ins = table.insert().values(board=line[0],
                                                trade_date=line[1],
                                                short_name=line[2],
                                                secid=line[3],
                                                num_trades=line[4],
                                                trade_value=line[5],
                                                open_price=line[6],
                                                low_price=line[7],
                                                high_price=line[8],
                                                close_price=line[9])
                    self.connection.execute(ins)
                except sqlalchemy.exc.SQLAlchemyError as dbe1:
                    print("Error while writing to db:", dbe1)

        else:
            for line in input_data:
                try:
                    ins = table.insert().values(board=line[0],
                                                trade_date=line[1],
                                                short_name=line[2],
                                                secid=line[3],
                                                num_trades=line[4],
                                                trade_value=line[5],
                                                open_price=line[6],
                                                low_price=line[7],
                                                high_price=line[8],
                                                close_price=line[9],
                                                expire_date=line[10],
                                                nom_value=line[11],
                                                unit=line[12])
                    self.connection.execute(ins)
                except sqlalchemy.exc.SQLAlchemyError as dbe1:
                    print("Error while writing to db:", dbe1)

    def query_db(self, table_name: str, instrument: str = None) -> list:
        """ Select from DB.

        Input:
            table_name (str): table from MYSQL database to select.
            instrument (str): WHERE case - selecting bond or stock,
                              if not specified then return all table.

        Return: list
        """

        table = sql.Table(f'{table_name}', self.metadata,
                          autoload=True,
                          autoload_with=self.engine_mysql)
        try:
            if instrument:
                query = sql.select([table]).\
                    where(table.c.secid == instrument)
            else:
                query = sql.select([table])
            result_get = self.connection.execute(query)
            result_set = result_get.fetchall()
            return result_set
        except sqlalchemy.exc.SQLAlchemyError as dbe2:
            print("Error while reading from db:", dbe2)
