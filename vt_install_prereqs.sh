#! /usr/bin/env bash
# For Mint 15: deb http://ubuntu.media.mit.edu/ubuntu/ raring main universe
# For Ubuntu 12 LTS: deb http://ubuntu.media.mit.edu/ubuntu/ precise main universe
#If one part stalls, try commenting it out.
echo 'deb http://ubuntu.media.mit.edu/ubuntu/ precise main universe' >> /etc/apt/sources.list
sudo apt-get update &&

apt-get install -y git &&
sudo apt-get install -y python-pip &&
sudo apt-get install -y build-essential &&

sudo apt-get install -y -f libqt4-dev &&
#sudo apt-get build-dep libqt4-dev

sudo apt-get install -y gperf bison &&
sudo apt-get install -y libxcb1 libxcb1-dev libx11-xcb1 libx11-xcb-dev libxcb-keysyms1 libxcb-keysyms1-dev libxcb-image0 libxcb-image0-dev libxcb-shm0 libxcb-shm0-dev libxcb-icccm4 libxcb-icccm4-dev libxcb-sync0 libxcb-sync0-dev libxcb-xfixes0-dev libxrender-dev libxcb-shape0-dev &&

sudo apt-get install -y mongodb mongodb-dev &&
sudo apt-get install -y python-dev &&
sudo apt-get install -y -f python-numpy &&
sudo pip install -U numpy &&

sudo pip install -U networkx &&

apt-get install -y -f python-pymongo &&

sudo apt-get install -y libqt4-opengl &&
sudo apt-get install -y python-qt4-gl &&
sudo apt-get install -y python-pyside.qtopengl &&

sudo apt-get install -y libfreetype6 libfreetype6-dev -y &&
sudo apt-get install -y python-vtk &&

#sudo apt-get install -y python-pyqt python-pyqt-dev &&
sudo apt-get install -y python-qt4 python-qt4-dev &&
sudo apt-get install -y python-matplotlib &&
sudo apt-get install -y python-suds &&
sudo apt-get install -y python-support 

sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose -y

#This command will initialize the DB
#mongorestore --host localhost --db PW_2012_09_02_09_03_35 --directoryperdb {data-dir} --drop 
