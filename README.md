# lahmans-baseball-mysql
Script for creating MySQL database containing Lahmans Baseball Data.

> This data is used in a small portion of our [Actionable Python book](https://www.amazon.com/Python-3-8-Nat-Dunn/dp/1951959027).

If you just want to create the MySQL database, download *lahman-mysql-dump.sql* and import it into MySQL using MySQL Workbench:
1. **Server > Data Import**
1. Select **Import from Self-Contained File**
1. Pick any **Default Target Schema**. It will be ignored, as the file creates a new one.
1. Click **Start Import** button.

## General Notes
1. Added leagues and divisions tables to stored data related to the CSV data's pseudo-foreign keys: `lgID` and `divID`.
1. Added autoincrementing `ID` fields to all tables that had obvious single-field primary key.
1. Added foreign keys to tables references the added `ID` primary keys. All of these foreign keys contain an underscore: `div_id`, `team_id`, `team_IDwinner`, `team_IDloser`, `lg_IDwinner`, `lg_IDloser`, `park_ID`.
    1. **We did not remove** the existing ids, so queries relying on those should continue to work.
1. Added date fields for `people.birth_date`, `people.debut_date`, `people.lastgame_date`, `people.death_date`, `homegames.spanfirst_date`, and `homegames.spanlast_date`.
    1. These make it easier to run date comparison queries. [An example](#youngest-debuts-this-century)
1. Changed the field name `rank` to `teamRank`, as 'rank' is a reserved word in MySQL 8+.
1. Removed all periods from field names. This affects fields in *Parks.csv* and *HomeGames.csv*.
1. Assumed 'NA' should be treated as `NULL` for all fields except `lgID`, where it relates to 'National Association'
1. Converted the `inf` integer value to `NULL` for lack of a better idea.

## Data Lost
1. In `allstarfull`, the row with this data: `['bailean01', None, None, None, 'OAK', 1512, 'AL', 0, None]` has no `yearID`. Because of this, we made `yearID` optional in the `allstarfull` table.
1. In `awardsplayers`, the row with this data: `['cruzne02', 'Outstanding DH Award', 2017, None, None, None]` has no `lgID`. Because of this, we made `lgID` optional in the `awardsplayers` table.
1. The following `schoolID`s appear in *CollegePlaying.csv*, but not in *Schools.csv*: 'ctpostu', 'txutper', 'txrange', 'caallia'. Records in *CollegePlaying.csv* with those schoolIDs do not get included in the `collegeplaying` table of the MySQL database.
1. PlayerID 'thompan01' appears in *fieldingOF.csv*, but not in *People.csv*. His record does not get included in the `fieldingof` table of the MySQL database.

## Data Changed/Fixed
1. MLN - In *AllstarFull.csv*, `teamID` "MLN" exists. That should be "ML1". In *Teams.csv*, "MLN" is value for `teamIDBR`, `teamIDlahman45`, and `teamIDretro`, but not for `teamID`. We changed this value to "ML1" in the `allstarfull` table of the MySQL database.
1. WSN - In *AllstarFull.csv*, `teamID` "WSN" exists. That should be "WAS". In *Teams.csv*, "WSN" is value for `teamIDlahman45` and `teamIDretro`, but not for `teamID`. We changed this value to "WAS" in the `allstarfull` table of the MySQL database.
1. MIL 1970 - 1997. In *AllstarFull.csv*, these records use "MIL" as the `teamID`. They should be "ML4" as that is the Brewers' `teamID` for those years. We changed this.
1. LAA 1997 - 2004. In *AllstarFull.csv*, these records use "LAA" as the `teamID`. They should be "ANA" as that is the Angels' `teamID` for those years. We changed this.
                    
## Python Script
1. This is only relevant if you're going to try to recreate the MySQL script. If you do that and have suggestions, please create an issue.
1. You will need the following files:
    1. *lahman_bbdb_mysql_from_csvs_2019.py*
    1. *create-lahman-mysql.sql*
    1. *requirements.txt*
    1. A *csvs* directory containing all the CSV files from https://github.com/chadwickbureau/baseballdatabank/tree/master/core.
1. You will need to change the user and password variables (lines 56-57 of *lahman_bbdb_mysql_from_csvs_2019.py*) to your MySQL login.
1. We recommend you create a virtual environment:
    1. Create a directory called ".venv"
    1. cd into that directory
    1. Run: `python -m venv virtual-lahman`
    1. Run one of the following:
        - **Windows:** `virtual-lahman/Scripts/activate`
        - **Mac/Linux:** `virtual-lahman/bin/activate`
    1. Run `pip install -r requirements.txt`
1. The migration took just under 10 minutes on my computer.
1. The larger CSVs will cause `DtypeWarning`s, but these don't seem to have any negative effect.
1. We could definitely do a better job with our error handling. We got lazy at the end.

## Creating the DUMP File
1. Open MySQL Workbench
1. Select **Server > Data Export**
1. Check lahmansbaseballdb
1. **Select Export to Self-Contained File**
1. Check **Create Dump in a Single Transaction** and **Include Create Schema**
1. Click **Start Export**. This will create a .sql file.
1. Copy all the `DROP TABLE` statements below and paste them at the top of the dump file after the `USE lahmansbaseballdb;` line.
<pre>
DROP TABLE IF EXISTS seriespost;
DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS pitchingpost;
DROP TABLE IF EXISTS pitching;
DROP TABLE IF EXISTS managershalf;
DROP TABLE IF EXISTS managers;
DROP TABLE IF EXISTS homegames;
DROP TABLE IF EXISTS parks;
DROP TABLE IF EXISTS halloffame;
DROP TABLE IF EXISTS fieldingpost;
DROP TABLE IF EXISTS fieldingofsplit;
DROP TABLE IF EXISTS fieldingof;
DROP TABLE IF EXISTS fielding;
DROP TABLE IF EXISTS collegeplaying;
DROP TABLE IF EXISTS schools;
DROP TABLE IF EXISTS battingpost;
DROP TABLE IF EXISTS batting;
DROP TABLE IF EXISTS awardsshareplayers;
DROP TABLE IF EXISTS awardssharemanagers;
DROP TABLE IF EXISTS awardsplayers;
DROP TABLE IF EXISTS awardsmanagers;
DROP TABLE IF EXISTS appearances;
DROP TABLE IF EXISTS allstarfull;
DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS teamshalf;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS teamsfranchises;
DROP TABLE IF EXISTS divisions;
DROP TABLE IF EXISTS leagues;
</pre>

The file should be ready to use as an import file.

## sqlite3 version
Also included is *lahmansbaseballdb.sqlite* - a sqlite3 version of the database, which we created using [MySQL to SQLite3](https://pypi.org/project/mysql-to-sqlite3/).

    mysql2sqlite -f lahmansbaseballdb.sqlite -d lahmansbaseballdb -u username -p password

## Some Queries to Try
### Most homeruns in 1977
    SELECT p.nameFirst, p.nameLast, b.HR, t.name AS team, b.yearID
    FROM batting b
        JOIN people p ON p.playerID = b.playerID
        JOIN teams t ON t.ID = b.team_ID
    WHERE b.YearID = 1977
    ORDER BY b.HR DESC
    LIMIT 5;

Without the new primary key - foreign key relationship, that query would be:*

    SELECT p.nameFirst, p.nameLast, b.HR, t.name AS team, b.yearID
    FROM batting b
        JOIN people p ON p.playerID = b.playerID
        JOIN teams t ON t.teamID = b.teamID AND t.yearID = b.yearID
    WHERE b.YearID = 1977
    ORDER BY b.HR DESC
    LIMIT 5;

* This query will still work.

### Ten Heaviest Rookies
    SELECT nameFirst, nameLast, weight, year(debut)
    FROM people
    ORDER BY weight DESC
    LIMIT 10;

### Worst ERA for Cy Young Winners
    SELECT people.playerID, people.nameFirst, people.nameLast, ap.yearID, pitching.ERA
    FROM awardsplayers ap 
        JOIN pitching pitching ON pitching.playerID = ap.playerID AND pitching.yearID = ap.yearID
        JOIN people ON people.playerID = pitching.playerID
    WHERE ap.awardID = 'Cy Young Award'
    ORDER BY pitching.ERA DESC
    LIMIT 5;

#### The Results
    sutclri01   Rick    Sutcliffe   1984    5.15
    hoytla01    LaMarr  Hoyt        1983    3.66
    clemero02   Roger   Clemens     2001    3.51
    colonba01   Bartolo Colon       2005    3.48
    mcdowja01   Jack    McDowell    1993    3.37

This query reveals a challenge. It shows that Rick Sutcliffe had an ERA of 5.15 in 1984,
a year in which he won the Cy Young Award. Sutcliffe played on two teams that year, which
we can see by running this query:

    SELECT p2.ERA, p2.ER, p2.IPouts,
        t.teamID, t.name AS team
    FROM people p1
        JOIN pitching p2 ON p1.playerID = p2.playerID
        JOIN teams t ON t.ID = p2.team_ID
    WHERE p1.playerID = 'sutclri01' AND p2.yearID=1984;

#### The Results
    5.15    54  283 CLE Cleveland Indians
    2.69    45  451 CHN Chicago Cubs

Because of this, we have to calculate the ERA ourselves, like this:

    SELECT people.playerID, people.nameFirst, people.nameLast, ap.yearID, 
        9*SUM(pitching.ER)/(SUM(pitching.Ipouts)/3) AS ERA
    FROM awardsplayers ap 
        JOIN pitching pitching ON pitching.playerID = ap.playerID AND pitching.yearID = ap.yearID
        JOIN people ON people.playerID = pitching.playerID
    WHERE ap.awardID = 'Cy Young Award'
    GROUP BY people.playerID, people.nameFirst, people.nameLast, ap.yearID
    ORDER BY ERA DESC
    LIMIT 5;

#### The Results
    hoytla01    LaMarr  Hoyt        1983    3.6598
    sutclri01   Rick    Sutcliffe   1984    3.6417
    clemero02   Roger   Clemens     2001    3.5129
    colonba01   Bartolo Colon       2005    3.4760
    mcdowja01   Jack    McDowell    1993    3.3662

### Youngest Debuts This Century
    SELECT nameFirst, nameLast, birth_date, debut_date, 
    timestampdiff(day, birth_date, debut_date)/365.25 AS debut_age
    FROM people
    WHERE debut_date IS NOT NULL AND birth_date IS NOT NULL
        AND debut_date > '2000-01-01'
    ORDER BY debut_age
    LIMIT 5;

#### The Results
    Elvis       Luciano     2000-02-15    2019-03-31    19.1211
    Felix       Hernandez   1986-04-08    2005-08-04    19.3238
    Jurickson   Profar      1993-02-20    2012-09-02    19.5318
    Bryce       Harper      1992-10-16    2012-04-28    19.5318
    Juan        Soto        1998-10-25    2018-05-20    19.5674

## The Model
<img src="https://github.com/WebucatorTraining/lahman-baseball-mysql/blob/master/lahman-model-thumbnail.png?raw=true" alt="Lahman Model">
<a href="https://github.com/WebucatorTraining/lahman-baseball-mysql/blob/master/lahman-model.png">Full Size Model</a>