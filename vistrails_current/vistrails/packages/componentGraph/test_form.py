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

from db.programmableweb.mongo_source import DataSource

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
'''
Created on Sep 19, 2012

@author: xiaoxiao
'''

data_source = DataSource()
mashups = data_source.mashups()

class TestForm(QtGui.QMainWindow):

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
#        self.createEventMap()

    def draw_api_to_api(self):
        self.widget = MatplotlibWidget(1)

    def draw_mashup_to_mashup(self):
        self.widget = MatplotlibWidget(2)

    def draw_member_mashup(self):
        self.widget = MatplotlibWidget(3)

    def draw_graph(self):
        self.widget = MatplotlibWidget(1)
        self.setCentralWidget(self.widget)

        layout = {}
        g = nx.Graph()

        pairs = data_source.pairs()
        api_map = {}
        mashup_map = {}
        node_size = {}
        node_color = {}
        
        all_apis = data_source.apis()
        all_api_map = {}
        for api in all_apis:
            all_api_map[api["id"]] = api
            
        all_mashups = data_source.mashups()
        all_mashup_map = {}
        for mashup in all_mashups:
            all_mashup_map[mashup["id"]] = mashup
    
        for pair in pairs:
            api = all_api_map.get(pair["api"])
            mashup = all_mashup_map.get(pair["mashup"])
            api_id = None
            mashup_id = None
            if api:
                api_id = api_map.get(pair["api"])
                _id = api["id"]
                if not api_id:
                    api_map[_id] = True
                    g.add_node(_id, api)
                    layout[_id] = (random.random() , random.random())
                    node_size[_id] = 50
                    node_color[_id] = 0.5
    
            if mashup:
                mashup_id = mashup_map.get(pair["mashup"])
                _id = mashup["id"]
                if not mashup_id:
                    mashup_map[_id] = True
                    g.add_node(_id, mashup)
                    layout[_id] = (random.random() , random.random())
                    node_size[_id] = 80
                    node_color[_id] = 0.8
                else:
                    node_size[_id] = node_size[_id] + 40
    
            if api and mashup:
                g.add_edge(api["id"], mashup["id"])
    
    
        for v in g.nodes():
            print v
    
        ax = self.widget.axes
        ax.get_xaxis().set_visible(False) 
        ax.get_yaxis().set_visible(False)
        try:
            print 'test4'
            nx.draw(g, pos=layout, ax=ax, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False)
        except Exception, e:
            print e
        finally:
            self.widget.draw()


class MashUpInfoWidget(QtGui.QWidget):
    
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
        if num == 0:
            pass
        elif num == 1:
            sc = ApiToApiCanvas(self, width=5, height=4, dpi=100)
        elif num == 2:
            sc = MashupToMashupCanvas(self, width=5, height=4, dpi=100)
        elif num == 3:
            sc = MemberToMashup(self, width=5, height=4, dpi=100)
        l.addWidget(sc)

        self.infoLabel = QtGui.QLabel('', self)
        self.infoLabel.move(20, 20)
        self.infoLabel.setFixedWidth(1000)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(sc)

        self.setLayout(l)
        
    def getFigure(self):
        return self.fig

    def draw(self):
        pass

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
            print 'test1'
            nx.draw(g, pos=layout, ax=self.axes, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False)
        except Exception, e:
            print e

class ApiToApiCanvas(TestFigureCanvas):
    
    def draw(self):
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
            print 'test2'
            nx.draw(g, pos=layout, ax=self.axes, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False)
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
            print 'test3'
            nx.draw(g, pos=layout, ax=self.axes, node_size=[node_size[v] for v in g.nodes()], node_color=[node_color[v] for v in g.nodes()], with_labels=False, width=3)
        except Exception, e:
            print e
