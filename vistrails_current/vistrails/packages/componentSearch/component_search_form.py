'''
Created on Sep 19, 2012

@author: xiaoxiao
'''
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QStandardItemModel, QTableView, QPushButton, QWidget
from PyQt4.QtGui import QTextEdit, QLabel

import core.modules.module_registry
import core.packagemanager
import core.modules.vistrails_module as vistrails_module
from core.modules.vistrails_module import Module
from packages.SUDSWebServices.init import Service
#from packages.SUDSWebServices.init import add_new_service

from db.programmableweb.mongo_source import DataSource
from networkx_graph import matplotlibWidget

import random
import requests

def get_api_name(api):
    return str(api['id'])[(len("http://www.programmableweb.com/api/")):]

def get_api_full_name(api):
    return "http://www.programmableweb.com/api/%s" % api

def get_mashup_name(mashup):
    return str(mashup['id'])[(len("http://www.programmableweb.com/mashup/")):]

def get_mashup_full_name(mashup):
    return "http://www.programmableweb.com/mashup/%s" % mashup

class ComponentSearchForm():

    data_source = None
    
    related_mashups = None
    
    widget = None
    
    table = None
    
    add_btn = None
    
    graph_form = None
    
    highlighted_api = None
    
    highlighted_mashup = None
    
    def show_main_window(self):
        self.graph_form = matplotlibWidget()
        if self.widget:
            self.widget.destroy()
            self.widget = None;
        self.widget = QWidget()
        self.widget.setMinimumSize(800, 600)
        btn_api = QtGui.QPushButton("Recommend Modules", self.widget)
        btn_api.move(30, 20)

        btn_mashup = QtGui.QPushButton("Recommend Workflows", self.widget)
        btn_mashup.move(200, 20)

        self.textboxLabel = QLabel(self.widget)
        self.textboxLabel.setText("Describe your goals:")
        self.textboxLabel.move(35, 60)
        self.textboxLabel.show
        
        self.textbox = QTextEdit(self.widget)
        self.textbox.move(30, 80)
        self.textbox.setFixedWidth(300)
        self.textbox.setFixedHeight(28)

        btn_api.clicked.connect(self.api_button_clicked)
        btn_mashup.clicked.connect(self.mashups_button_clicked)

        self.table = QTableView(self.widget)
        self.table.clicked.connect(self.table_clicked)
        self.table.setMinimumSize(740, 500)
        self.table.resizeColumnsToContents()
        self.table.move(30, 120)

        self.widget.show()
        
        self.add_btn = QPushButton(self.widget)
        self.add_btn.clicked.connect(self.add_new_api)
        self.add_btn.setText("Add to Palette")
        self.add_btn.hide()
        self.add_btn.move(650, 20)
        
        self.recommendLabel = QLabel(self.widget)
        self.recommendLabel.setText("Also Used")
        self.recommendLabel.move(30, 95)
        self.recommendLabel.hide()
        
        self.switch_btn_apis = QPushButton(self.widget)
        self.switch_btn_apis.clicked.connect(self._show_related_apis)
        self.switch_btn_apis.setText("Related Workflows")
        self.switch_btn_apis.move(500, 20)
        self.switch_btn_apis.hide()
        
        self.switch_btn_mashups = QPushButton(self.widget)
        self.switch_btn_mashups.clicked.connect(self._show_related_mashups)
        self.switch_btn_mashups.setText("Related Modules")
        self.switch_btn_mashups.move(500, 20)
        self.switch_btn_mashups.hide()

    def __init__(self, parent=None):
        self.data_source = DataSource()
        
    def table_clicked(self):
        """
        Click the table, the graph form may change according to the selection.
        """
        model = self.table.selectionModel()
        indexes = model.selectedIndexes()
        for index in indexes:
            row = index.row()
            #            data = index.model().headerData(0,Qt.Horizontal).toString()
            data = index.model().headerData(0,Qt.Horizontal)
            newIndex = index.model().index(row, 0)
            if data == "API":
                api_id = get_api_full_name(newIndex.model().data(newIndex))
                api = self.data_source.api_by_id(api_id)
                print api
                mashups = self.data_source.mashups_by_api(api)
                apis = []
                for mashup in mashups:
                    apis.extend(self.data_source.apis_by_mashup(mashup))
                self.graph_form.draw_apis(apis, api, self.highlighted_api)
            else:
                mashup_id = get_mashup_full_name(newIndex.model().data(newIndex))
                mashup = self.data_source.mashup_by_id(mashup_id)
                if not mashup:
                    return
                apis = self.data_source.apis_by_mashup(mashup)
                mashups = []
                if len(apis) > 0:
                    mashups.extend(self.data_source.mashups_by_api(apis[0]))
                self.graph_form.draw_mashups(mashups, mashup, self.highlighted_mashup)
            return


    def _show_apis(self, apis, recommend=False):
        self.switch_btn_apis.hide()
        self.switch_btn_mashups.hide()
        self.recommendLabel.hide()

        row = 0
        model = QStandardItemModel(len(apis), 4)
        model.setColumnCount(4)
        #QVariant(...) -> ...
        for api in apis:
            model.setData(model.index(row, 0), get_api_name(api))
            model.setData(model.index(row, 1), api['protocols'])
            model.setData(model.index(row, 2), api['provider'])
            model.setData(model.index(row, 3), api['version'])
            row += 1

        model.setHeaderData(0, Qt.Horizontal, "Module")
        model.setHeaderData(1, Qt.Horizontal, "Protocol")
        model.setHeaderData(2, Qt.Horizontal, "Provider")
        model.setHeaderData(3, Qt.Horizontal, "Version")

#        model.setHeaderData(0, Qt.Horizontal, QVariant("API"))
#        model.setHeaderData(1, Qt.Horizontal, QVariant("Protocols"))
#        model.setHeaderData(2, Qt.Horizontal, QVariant("Provider"))
#        model.setHeaderData(3, Qt.Horizontal, QVariant("Version"))

        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        
        if recommend:
            self.recommendLabel.show()
        
        self.add_btn.show()

    def _show_mashups(self, mashups):
        self.switch_btn_apis.hide()
        self.switch_btn_mashups.hide()
        self.recommendLabel.hide()
        row = 0
        model = QStandardItemModel(len(mashups), 4)
        model.setColumnCount(4)
        for mashup in mashups:
            model.setData(model.index(row, 0), get_mashup_name(mashup))
            model.setData(model.index(row, 1), mashup['title'])
            model.setData(model.index(row, 2), mashup['self'])
            model.setData(model.index(row, 3), mashup['description'])
            
            row += 1
        
        model.setHeaderData(0, Qt.Horizontal, "Workflow")
        model.setHeaderData(1, Qt.Horizontal, "Short Description")
        model.setHeaderData(2, Qt.Horizontal, "Provider")
        model.setHeaderData(3, Qt.Horizontal, "Detailed Info")

#        model.setHeaderData(0, Qt.Horizontal, QVariant("Info"))
#        model.setHeaderData(1, Qt.Horizontal, QVariant("Title"))
#        model.setHeaderData(2, Qt.Horizontal, QVariant("self"))
#        model.setHeaderData(3, Qt.Horizontal, QVariant("Description"))

        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.add_btn.show()

    def api_button_clicked(self):
        """
        Trigger to search APIs
        """        
        self.graph_form.draw_api()
        self.graph_form.show()

        apis = self.data_source.apis()
        key = str(self.textbox.toPlainText())
        #Has key or not has key, it is different.
        if key:
            self.api_search_button_clicked()
        else:
            self._show_apis(apis)

    def mashups_button_clicked(self):
        """
        Trigger to search mashups
        """
        self.graph_form.draw_mashup()
        self.graph_form.show()

        key = str(self.textbox.toPlainText())
        print key
        print "button clicked"
        if key:
            self.mashup_search_button_clicked()
        else:
            self._show_mashups(self.data_source.mashups())

    #Should probably refactor this into one method.
    def api_search_button_clicked(self):
        """
        Search when no keyword
        """
        self.highlighted_api = None
        self.highlighted_mashup = None
        key = str(self.textbox.toPlainText())
        if key != "":
            apis = self.data_source.search_api(key)
            self._show_apis(apis)

    def mashup_search_button_clicked(self):
        """
        Search when no keyword
        """
        self.highlighted_api = None
        self.highlighted_mashup = None
        key = str(self.textbox.toPlainText())
        if key != "":
            mashups = self.data_source.search_mashup(key)
            self._show_mashups(mashups)
    
    def add_new_api(self):
        """
        Add new api to the modules package.
        """
        apis = self.data_source.apis()
        model = self.table.selectionModel()
        indexes = model.selectedIndexes()
        for index in indexes:
            api = apis[index.row()]
            self._add_new_api(api)
            return
    
    def add_related_api(self):
        objs = []
        for mashup in self.related_mashups:
            objs.append(mashup)
            for api in mashup["related_mashups"]:
                objs.append(api)
        model = self.table.selectionModel()
        indexes = model.selectedIndexes()
        for index in indexes:
            api = objs[index.row()]
            if api.get("protocols"):
                self._add_new_api(api)
                return

    def _show_related_mashups(self):
        self.switch_btn_apis.hide()
        self.switch_btn_mashups.hide()
        self.recommendLabel.hide()
        
        apis = []
        objs = []
        for mashup in self.related_mashups:
            apis.extend(mashup["related_mashups"])

        for api in apis:
            objs.append(api)
            mashups = self.data_source.mashups_by_api(api)
            objs.extend(mashups)

        row = 0
        model = QStandardItemModel(len(objs), 4)
        model.setColumnCount(4)
        for obj in objs:
            if obj.get('protocols'):
                model.setData(model.index(row, 0), get_api_name(obj))
                model.setData(model.index(row, 1), obj['protocols'])
                model.setData(model.index(row, 2), obj['provider'])
            else:
                model.setData(model.index(row, 3), get_mashup_name(obj))
            row += 1

        model.setHeaderData(0, Qt.Horizontal, "API")
        model.setHeaderData(1, Qt.Horizontal, "Protocols")
        model.setHeaderData(2, Qt.Horizontal, "Provider")
        model.setHeaderData(3, Qt.Horizontal, "Mashup")
        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.switch_btn_apis.show()

    def _show_related_apis(self):
        self.switch_btn_apis.hide()
        self.switch_btn_mashups.hide()
        self.recommendLabel.hide()
        
        row = 0
        objs = []
        for mashup in self.related_mashups:
            objs.append(mashup)
            for api in mashup["related_mashups"]:
                objs.append(api)
        #Combining similarity and related.
        similar_apis = self.data_source.search_api_similarity(self.highlighted_api)
        #return str(mashup['id'])[(len("http://www.programmableweb.com/mashup/")):]
        objs.append({'id': "http://www.programmableweb.com/mashup/Using-Similarity-Metric"})
        objs.extend(similar_apis)
        #Combining similarity and related.

        #http://localhost:9000/getReputation/John%20Lions
        model = QStandardItemModel(len(objs), 6)
        for obj in objs:
            if obj.get('protocols'):
                model.setData(model.index(row, 1), get_api_name(obj))
                model.setData(model.index(row, 2), obj['protocols'])
                model.setData(model.index(row, 3), obj['provider'])
                model.setData(model.index(row, 4), obj['version'])
                #trust  = requests.get('http://localhost:9000/getReputation/Luis Ramos').content
                model.setData(model.index(row, 5), str(random.random()))
                #model.setData(model.index(row, 5), QVariant(trust))
            else:
                model.setData(model.index(row, 0), get_mashup_name(obj))
            row += 1

        model.setHeaderData(0, Qt.Horizontal, "Mashup")
        model.setHeaderData(1, Qt.Horizontal, "API")
        model.setHeaderData(2, Qt.Horizontal, "Protocols")
        model.setHeaderData(3, Qt.Horizontal, "Provider")
        model.setHeaderData(4, Qt.Horizontal, "Version")
        model.setHeaderData(5, Qt.Horizontal, "Trust")

        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.switch_btn_mashups.show()

    def _add_new_api(self, api):
        self.highlighted_api = api
        mashups = self.data_source.mashups_by_api(api)
        for mashup in mashups:
            mashup['related_mashups'] = (self.data_source.apis_by_mashup(mashup))
        if len(mashups) > 0:
            self.related_mashups = mashups
            self._show_related_apis()
        manager = core.packagemanager.get_package_manager()
        reg = core.modules.module_registry.get_module_registry()
        package = manager.get_package("edu.cmu.sv.components", "1.0.0")
        core.modules.module_registry.set_current_package(package)

        if (api["protocols"] == "SOAP" and api["wsdl"] != ""):
            s = Service(api["wsdl"])
#            add_new_service(s, api["wsdl"])
        else:
            new_module = vistrails_module.new_module(Module, get_api_name(api))
            reg.add_module(new_module)
    
            reg.add_input_port(new_module, "value1",
                         (core.modules.basic_modules.String, 'the first argument'))
            reg.add_input_port(new_module, "value2",
                         (core.modules.basic_modules.String, 'the second argument'))
            reg.add_output_port(new_module, "value",
                          (core.modules.basic_modules.String, 'the result'))

