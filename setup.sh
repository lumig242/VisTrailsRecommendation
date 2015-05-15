#! /usr/bin/env bash
sudo service mongodb start
#Mongo takes a long time to start up
echo 'Sleeping for 3 minutes because mongo takes a long time'
sleep 60
echo '1 minute has passed'
sleep 60
echo '2 minutes have passed'
sleep 60
mongorestore --host localhost --db PW_2012_09_02_09_03_35 --directoryperdb /home/developer/PW_2012_09_02_09_03_35 --drop 
