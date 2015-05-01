'''
Created on Oct 21, 2012

@author: xiaoxiao
'''
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QStandardItemModel, QTableView, QVBoxLayout, QLabel
from PyQt4.QtGui import QSizePolicy

import random

import networkx as nx
import matplotlib
import matplotlib.pyplot

from db.programmableweb.mongo_source import DataSource

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
'''
Created on Sep 19, 2012

@author: xiaoxiao
'''

def get_api_name(api):
    return str(api['id'])[(len("http://www.programmableweb.com/api/")):]

def get_mashup_name(mashup):
    return str(mashup['id'])[(len("http://www.programmableweb.com/mashup/")):]



data_source = DataSource()
mashups = data_source.mashups()

class MplCanvas(FigureCanvas):
    api_map = data_source.api_with_mashups()
    mashup_map = data_source.mashup_with_apis()
    
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # self.ax.hold(False)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def draw_related_mashup(self, mashups, current_mashup=None, highlight_mashup=None):
        """
        Draw the realated mashup graph
        """
        self.ax.clear()
        layout = {}
        g = nx.Graph()
        node_size = {}
        node_color = {}
        node_map = {}
        node_id = 0

        for mashup in mashups:
            if node_map.get(mashup["id"]) == None:
                node_map[mashup["id"]] = node_id
                g.add_node(node_id)
                node_size[node_id] = 20
                if current_mashup and mashup["id"] == current_mashup["id"]:
                    node_color[node_id] = 0.7
                    node_size[node_id] = 180
                    layout[node_id] = (random.random() , random.random())
                else:
                    node_color[node_id] = 0.5
                    layout[node_id] = (random.random() , random.random())
                node_id = node_id + 1
        for i in range(0, len(mashups)):
            node_id_start = node_map.get(mashups[i]["id"])
            node_id_end = node_map.get(current_mashup["id"])
            g.add_edge(node_id_start, node_id_end)
        try:
            print 'graph1'
            nx.draw(g, pos=layout, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False, edge_color='y')
        except Exception, e:
            print e
        self.draw()
        matplotlib.pyplot.show()


    def draw_related_api(self, apis, current_api=None, highlight_api=None):
        """
        Draw the realated api graph
        """
        self.ax.clear()
        layout = {}
        g = nx.Graph()
        node_size = {}
        node_color = {}
        node_map = {}
        node_labels = {}
        node_id = 0
        for api in apis:
            if node_map.get(api["id"]) == None:
                node_map[api["id"]] = node_id
                g.add_node(node_id)
                node_size[node_id] = 20
                node_labels[node_id] = get_api_name(api)
                layout[node_id] = (random.random() , random.random()) 
                if current_api and api["id"] == current_api["id"]:
                    node_color[node_id] = 0.7
                    node_size[node_id] = 180
                elif highlight_api and api["id"] == highlight_api["id"]:
                    node_color[node_id] = 0.3
                    node_size[node_id] = 180
                else:
                    node_color[node_id] = 0.5
                node_id = node_id + 1
        for i in range(0, len(apis)):
            node_id_start = node_map.get(apis[i]["id"])
            node_id_end = node_map.get(current_api["id"])
            g.add_edge(node_id_start, node_id_end)
        try:
            with_labels = False
            if len(apis) < 20:
                print 'testtesttest'
                with_labels = True
            print 'graph2'
            nx.draw(g, pos=layout, labels=node_labels, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=with_labels)
        except Exception, e:
            print e
        self.draw()
        matplotlib.pyplot.show()



    def draw_api(self, emphasize=False):

        self.ax.clear()
        layout = {}
        g = nx.Graph()

        node_size = {}
        node_color = {}
        node_map = {}
        node_id = 0
        for key in self.mashup_map:
                for api in self.mashup_map[key]:
                    if node_map.get(api) == None:
                        node_map[api] = node_id
                        g.add_node(node_id)
                        node_size[node_id] = 20
                        if (emphasize):
                            node_color[node_id] = 0.7
                            node_size[node_id] = 180
                            emphasize = False;
                        else:
                            node_color[node_id] = 0.5
                        layout[node_id] = (random.random() , random.random())
                        node_id = node_id + 1
                for i in range(0, len(self.mashup_map[key])):
                    for j in range(0, len(self.mashup_map[key])):
                        node_id_start = node_map.get(self.mashup_map[key][i])
                        node_id_end = node_map.get(self.mashup_map[key][j])
                        g.add_edge(node_id_start, node_id_end)
#                        node_size[node_id_start] = node_size[node_id_start] + 5
#                        node_size[node_id_end] = node_size[node_id_end] + 5

        try:
            print 'graph3'
            nx.draw(g, pos=layout, ax=self.ax, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False, edge_color='y')
        except Exception, e:
            print e
        self.draw()

    def draw_mashup(self, emphasize=False):
        self.ax.clear()

        layout = {}
        g = nx.Graph()

        node_size = {}
        node_color = {}
        node_map = {}
        node_id = 0
        
        for key in self.api_map:
            if len(self.api_map[key]) == 8:
                for api in self.api_map[key]:
                    if node_map.get(api) == None:
                        node_map[api] = node_id
                        g.add_node(node_id)
                        node_size[node_id] = 20
                        if (emphasize):
                            node_color[node_id] = 0.7
                            node_size[node_id] = 180
                            emphasize = False;
                        else:
                            node_color[node_id] = 0.5
                        layout[node_id] = (random.random() , random.random())
                        node_id = node_id + 1
                for i in range(0, len(self.api_map[key])):
                    for j in range(0, len(self.api_map[key])):
                        node_id_start = node_map.get(self.api_map[key][i])
                        node_id_end = node_map.get(self.api_map[key][j])
                        g.add_edge(node_id_start, node_id_end)
#                        node_size[node_id_start] = node_size[node_id_start] + 5
#                        node_size[node_id_end] = node_size[node_id_end] + 5
    
        try:
            print 'graph4'
            nx.draw(g, pos=layout, ax=self.ax, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False, edge_color='y')
        except Exception as e:
            print e
        self.draw()

    def draw_graph(self):
        self.ax.clear()

        G=nx.Graph()

        G.add_edge('a','b',weight=1)
        G.add_edge('a','c',weight=1)
        G.add_edge('a','d',weight=1)
        G.add_edge('a','e',weight=1)
        G.add_edge('a','f',weight=1)
        G.add_edge('a','g',weight=1)

        pos=nx.spring_layout(G)

        print 'graph5'
        nx.draw(G,pos,self.ax,node_size=1200,node_shape='o',node_color='0.75')

        self.draw()
 

class matplotlibWidget(QtGui.QWidget):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        
    def draw_graph(self):
        self.canvas.draw_graph()
    
    def draw_api(self, emphasize=False):
        self.canvas.draw_api(emphasize)
    
    def draw_mashup(self, emphasize=False):
        self.canvas.draw_mashup(emphasize)
    
    def draw_apis(self, apis, current_api=None, highlight_api=None):
        self.canvas.draw_related_api(apis, current_api, highlight_api)

    def draw_mashups(self, mashups, current_mashup=None, highlight_mashup=None):
        self.canvas.draw_related_mashup(mashups, current_mashup, highlight_mashup)

class TestForm(QtGui.QMainWindow):
    """
    The form to draw the graph.
    """

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

    def draw_api_to_api(self):
        self.widget = MatplotlibWidget(1)

    def draw_mashup_to_mashup(self):
        self.widget = MatplotlibWidget(2)

    def draw_member_mashup(self):
        self.widget = MatplotlibWidget(3)

class MashUpInfoWidget(QtGui.QWidget):
    """
    This widget is used to display the information of certain mashup.
    Jia asked me to display this when the mouse hover certain node.
    It is kind of hard for me to figure this out with a version with less bugs.
    """
    
    def __init__(self, mashup):
        QtGui.QWidget.__init__(self)
        self.mashup = mashup
        self.sample_url_label = QtGui.QLabel('', self)
        self.sample_url_label.setFixedWidth(500)
        self.sample_url_label.setText("sample url: %s" % (mashup["sampleUrl"]))
        self.sample_url_label.move(0, 20)
        self.link_label = QtGui.QLabel('', self)
        self.link_label.setFixedWidth(500)
        self.link_label.move(0, 50)
        self.link_label.setText("link: %s" % (mashup["link"]))
        self.summary_label = QtGui.QLabel('', self)
        self.summary_label.setFixedWidth(500)
        self.summary_label.move(0, 80)
        self.summary_label.setText("summary: %s" % (mashup["summary"]))



class MatplotlibWidget(QtGui.QWidget):
    """
    Implements a Matplotlib figure inside a QWidget.
    Use getFigure() and redraw() to interact with matplotlib.

    Example::

        mw = MatplotlibWidget()
        subplot = mw.getFigure().add_subplot(111)
        subplot.plot(x,y)
        mw.draw()
    """
    def mousePressEvent(self, event):
        print "clicked"

    def __init__(self, num, size=(5.0, 4.0), dpi=100):
        QtGui.QWidget.__init__(self)
        
        l = QtGui.QVBoxLayout()

        #Use number to decied which form to show.
        if num == 0:
            pass
        elif num == 1:
            self.sc = ApiToApiCanvas(self, width=5, height=4, dpi=100)
        elif num == 2:
            self.sc = MashupToMashupCanvas(self, width=5, height=4, dpi=100)
        elif num == 3:
            self.sc = MemberToMashup(self, width=5, height=4, dpi=100)
        l.addWidget(self.sc)

        self.infoLabel = QtGui.QLabel('', self)
        self.infoLabel.move(20, 20)
        self.infoLabel.setFixedWidth(1000)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.sc)

        self.setLayout(l)
        
    def getFigure(self):
        return self.fig

    def draw(self):
        self.sc.draw()

    def show_label(self, x, y):
        mashup = mashups[int(random.uniform(0, len(mashups)))]
        self.infoLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.infoLabel.setText("mashups: %s" % (mashup["id"]))
        self.infoLabel.setStyleSheet("background-color: rgb(199, 199, 199);")
        self.infoLabel.move(x, y)
    
    def show_detail(self, x, y):
        mashup = mashups[int(random.uniform(0, len(mashups)))]
        self.detail = MashUpInfoWidget(mashup)
        self.detail.resize(500, 100)
        self.detail.move(x, y)
        self.detail.show()

class TestFigureCanvas(FigureCanvas):
    """
    For testing....
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        
        self.draw()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                  QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    def set_widget(self, widget):
        self.widget = widget

    def mousePressEvent(self, event):
        if event.button() == 1:
            self.widget.show_label(event.x(), event.y())
        else:
            self.widget.show_detail(event.x(), event.y())

class MashupToMashupCanvas(TestFigureCanvas):
    
    def draw(self):
        """
        Canvas for drawing the relationship between mashups
        """
        layout = {}
        g = nx.Graph()

        node_size = {}
        node_color = {}
        node_map = {}
        node_id = 0
        api_map = data_source.api_with_mashups()
        for key in api_map:
            if len(api_map[key]) == 8:
                for api in api_map[key]:
                    if node_map.get(api) == None:
                        node_map[api] = node_id
                        g.add_node(node_id)
                        node_size[node_id] = 50
                        node_color[node_id] = 0.5
                        layout[node_id] = (random.random() , random.random())
                        node_id = node_id + 1
                for i in range(0, len(api_map[key])):
                    for j in range(0, len(api_map[key])):
                        node_id_start = node_map.get(api_map[key][i])
                        node_id_end = node_map.get(api_map[key][j])
                        g.add_edge(node_id_start, node_id_end)
                        node_size[node_id_start] = node_size[node_id_start] + 5
                        node_size[node_id_end] = node_size[node_id_end] + 5
    
        try:
            print 'graph6'
            nx.draw(g, pos=layout, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False)
        except Exception, e:
            print e

class ApiToApiCanvas(TestFigureCanvas):
    
    def draw(self):
        """
        Canvas for draw the relationship between apis
        """
        mashup_map = data_source.mashup_with_apis()
        layout = {}
        g = nx.Graph()

        node_size = {}
        node_color = {}
        node_map = {}
        node_id = 0
        for key in mashup_map:
            if len(mashup_map[key]) == 20:
                for api in mashup_map[key]:
                    if node_map.get(api) == None:
                        node_map[api] = node_id
                        g.add_node(node_id)
                        node_size[node_id] = 50
                        node_color[node_id] = 0.5
                        layout[node_id] = (random.random() , random.random())
                        node_id = node_id + 1
                for i in range(0, len(mashup_map[key])):
                    for j in range(0, len(mashup_map[key])):
                        node_id_start = node_map.get(mashup_map[key][i])
                        node_id_end = node_map.get(mashup_map[key][j])
                        g.add_edge(node_id_start, node_id_end)
                        node_size[node_id_start] = node_size[node_id_start] + 5
                        node_size[node_id_end] = node_size[node_id_end] + 5

        try:
            print 'graph7'
            nx.draw(g, pos=layout, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False)
        except Exception, e:
            print e

class MemberToMashup(TestFigureCanvas):
    def draw(self):
        layout = {}
        g = nx.Graph()

        node_size = {}
        node_color = {}
        
        mashup_map = {}
        node_id = 0
        
        member_mashups = data_source.get_member_mashups_collections()
        for member_mashup in member_mashups:
            if (len(member_mashup["mashups"]) > 0):
                for mashup in member_mashup["mashups"]:
                    mashup_id = mashup_map.get(mashup["id"])
                    if not mashup_id:
                        mashup_id = mashup["id"]
                        g.add_node(node_id)
                        mashup_map[mashup_id] = node_id
                        node_size[node_id] = 50
                        node_color[node_id] = 'r'
                        layout[node_id] = (random.random() , random.random())
                        node_id = node_id + 1

                for i in range(0, len(member_mashup["mashups"])):
                    for j in range(0, len(member_mashup["mashups"])):
                        node_id_start = mashup_map.get(member_mashup["mashups"][i]["id"])
                        node_id_end = mashup_map.get(member_mashup["mashups"][j]["id"])
                        g.add_edge(node_id_start, node_id_end)
                        node_size[node_id_start] = node_size[node_id_start] + 5
                        node_size[node_id_end] = node_size[node_id_end] + 5
    
        try:
            print 'graph8'
            nx.draw(g, pos=layout, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False, width=3)
        except Exception, e:
            print e
