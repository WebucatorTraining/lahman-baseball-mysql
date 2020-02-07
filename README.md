# lahmans-baseball-mysql
Script for creating MySQL database containing Lahmans Baseball Data
This data is used in our soon-to-be-released Python book.

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
* MLN - In AllstarFull.csv, teamID "MLN" exists. That should be "ML1". In Teams.csv, MLN is value for teamIDBR, teamIDlahman45, and teamIDretro, but not for teamID. We changed this value to "ML1" in the allstarfull table of the MySQL database.
* WSN - In AllstarFull.csv, teamID "WSN" exists. That should be "WAS". In Teams.csv, WSN is value for teamIDlahman45 and teamIDretro, but not for teamID. We changed this value to "WAS" in the allstarfull table of the MySQL database.
                    
# Python Script
1. The migration took about 20 minutes on my computer.
1. The larger CSVs will cause DtypeWarnings, but these don't seem to have any negative effect.
1. We could definitely do a better job with our error handling. We got lazy at the end.
