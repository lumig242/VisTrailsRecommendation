#! /usr/bin/env bash
sudo service mongodb start
mongorestore --host localhost --db PW_2012_09_02_09_03_35 --directoryperdb /home/developer/PW_2012_09_02_09_03_35 --drop 
