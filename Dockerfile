FROM ubuntu:14.04

RUN apt-get update && apt-get install -y python python-pip python-dev
RUN apt-get install -y xvfb python python-dev zip python-qt4 python-qt4-gl python-qt4-sql python-vtk
RUN sudo apt-get install -y git gfortran libopenblas-dev liblapack-dev 
RUN sudo pip install numpy && sudo pip install scipy gitpython
RUN sudo apt-get install -y libfreetype6 libfreetype6-dev
RUN sudo apt-get install -y python-vtk
RUN sudo pip install networkx
RUN sudo apt-get install pkg-config 
RUN sudo pip install matplotlib
RUN sudo pip install suds
RUN sudo apt-get install libxext-dev libxrender-dev libxtst-dev -y
RUN sudo apt-get install -y mongodb mongodb-dev -y
RUN sudo pip install pymongo

# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer

USER developer
ENV HOME /home/developer
#RUN git clone git@github.com:cmusv-sc/VisTrailsWorkflowRecommender.git
ADD ./vistrails_current /home/developer/vistrails_current
ADD ./PW_2012_09_02_09_03_35 /home/developer/PW_2012_09_02_09_03_35
ADD ./setup.sh /home/developer/
#RUN sudo service mongodb start
#RUN mongorestore --host localhost --db PW_2012_09_02_09_03_35 --directoryperdb /home/developer/vistrails_current/PW_2012_09_02_09_03_35 --drop
#CMD /home/developer/setup.sh
#CMD python /home/developer/vistrails_current/vistrails/run.py
CMD /bin/bash
#docker run -ti --rm -e DISPLAY=unix$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix vt
