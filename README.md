# Python Capstone Project 

This is my final work after completing "Python software developer" course with CodingNomads.
I've decided to use Moscow Exchange free API since I have interest in investing.

Main ideas:
- collect data for selected instrument or instruments;
- save data to MYSQL database;
- explore data to find an instrument which is not much volatile,
  has good liquidity, not that expensive to by and has a potential
  to earn some money.

Also this code will be useful for anyone who interested in testing of MOEX free API.


## Getting Started

In order to run the project:
1. You'll need a local MYSQL server ready and use "mysqldump" to import my test database.
2. In the "main.py" provided rows from "config.ini" file to use with "configparser" module. 
Create file "config.ini" in the MOEX-app directory with this setup:
```
[Database]
secret = your_password
address = localhost
db_name = MOEX
user = root
```
P.S. You can use another user instead of root if yoy've created one earlier.
3. Check methods description.
4. Run "main.py".

Tips on #1 (working with MYSQL):
- **MySQL**: [Download](https://www.mysql.com/downloads/) & Install MySQL to your system
- **Server**: Make sure the MySQL server is running, and that you can access the program through your `PATH`
- **Database**: Create a new database called `MOEX` with `mysqladmin -u root -p create MOEX`
- **Create Tables**: Set up your local project database by importing the included dump file: `mysql -u root -p MOEX < moex_dump.sql`

After completing these steps, your database part should be set up and be ready to go.

```
Structure of MYSQL DB: MOEX db -> "Shares" table
			       -> "FederalBonds" table
			       -> "CorporateEurobonds" table
			       -> "CorporateBonds" table
```

Some project use examples are provided in the "main.py" (instruments choosing, requests printing, quering database).


THIS IS IMPORTANT!
If you'll decide to save collected data to MOEX database, then save it to corresponding table,
e.g. If "TQCB" board was chosen, then save data to "CorporateBonds" table. 


### Prerequisites

In general these packages are essential: SQLAlchemy, requests, numpy, pandas, blist, configparser. 

See requirements.txt


## Authors

* **Alex Kuznetsov** - *Initial work* - [ Aleks-me ](https://github.com/Aleks-me)

See also the [CodingNomads](https://codingnomads.co/)
