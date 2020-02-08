# lahmans-baseball-mysql
Script for creating MySQL database containing Lahmans Baseball Data
This data is used in our soon-to-be-released Python book.

If you just want to create the MySQL database, download lahman-mysql-dump.sql and import it into MySQL using MySQL Workbench:
1. **Server > Data Import**
1. Select **Import from Self-Contained File**
1. Pick any **Default Target Schema**. It will be ignored, as the file creates a new one.
1. Click **Start Import** button.


## General Notes
1. We added leagues and divisions tables to stored data related to the CSV data's pseudo-foreign keys: lgID and divID.
1. We added autoincrementing ID fields to all tables that had obvious single-field primary key.
1. We added foreign keys to tables references the added ID primary keys. All of these foreign keys contain an underscore: div_id, team_id, team_IDwinner, teamIDloser, lg_IDwinner, lg_IDloser, parkID.
1. We change the field name 'rank' to 'teamRank', as 'rank' is a reserved word in MySQL 8+.
1. We removed all periods from field names. This affects fields in Parks.csv and HomeGames.csv.
1. We assumed 'NA' should be treated as NULL for all fields except lgID, where it relates to 'National Association'
1. We converted the inf integer value to NULL for lack of a better idea.

## Data Lost
1. In allstarfull, ['bailean01', None, None, None, 'OAK', 1512, 'AL', 0, None] has no yearID. Because of this, we made yearID optional in the allstarfull table.
1. In awardsplayers, ['cruzne02', 'Outstanding DH Award', 2017, None, None, None] has no lgID. Because of this, we made lgID optional in the awardsplayers table.
1. The following schoolIDs appear in CollegePlaying.csv, but not in Schools.csv: 'ctpostu', 'txutper', 'txrange', 'caallia'. Records in CollegePlaying.csv with those schoolIDs do not get included in the collegeplaying table of the MySQL database.
1. PlayerID 'thompan01' appears in fieldingOF.csv, but not in People.csv. His record does not get included in the fieldingof table of the MySQL database.

## Data Changed
1. MLN - In AllstarFull.csv, teamID "MLN" exists. That should be "ML1". In Teams.csv, MLN is value for teamIDBR, teamIDlahman45, and teamIDretro, but not for teamID. We changed this value to "ML1" in the allstarfull table of the MySQL database.
1. WSN - In AllstarFull.csv, teamID "WSN" exists. That should be "WAS". In Teams.csv, WSN is value for teamIDlahman45 and teamIDretro, but not for teamID. We changed this value to "WAS" in the allstarfull table of the MySQL database.
                    
## Python Script
1. This is only relevant if you're going to try to recreate the MySQL script. If you do that and have suggestions, please create an issue.
1. You will need the following files:
    1. lahman_bbdb_mysql_from_csvs_2019.py
    1. create-lahman-mysql.sql
    1. requirements.txt
    1. A csvs directory containing all the CSV files from https://github.com/chadwickbureau/baseballdatabank/tree/master/core.
1. You will need to change the user and password variables (lines 56-57 of lahman_bbdb_mysql_from_csvs_2019.py) to your MySQL login.
1. We recommend you create a virtual environment:
    1. Create a directory called ".venv"
    1. cd into that directory
    1. Run: `python -m venv virtual-lahman`
    1. Run one of the following:
        - **Windows:** virtual-lahman/Scripts/activate
        - **Mac/Linux:** virtual-lahman/bin/activate
    1. Run `pip install -r requirements.txt`
1. The migration took about 20 minutes on my computer.
1. The larger CSVs will cause DtypeWarnings, but these don't seem to have any negative effect.
1. We could definitely do a better job with our error handling. We got lazy at the end.

## Creating the DUMP File
1. Open MySQL Workbench
1. Select **Server > Data Export**
1. Check lahmansbaseballdb
1. **Select Export to Self-Contained File**
1. Check **Create Dump in a Single Transaction** and **Include Create Schema**
1. Click **Start Export**. This will create a .sql file.
1. Copy all the `DROP TABLE` statements from lahman_bbdb_mysql_from_csvs_2019.py and paste them at the top of the dump file after the `USE lahmansbaseballdb;` line.
1. The file should be ready to as an import file.
