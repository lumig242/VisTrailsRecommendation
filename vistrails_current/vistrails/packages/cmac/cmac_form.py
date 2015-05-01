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
import re
import requests


def get_api_name(api):
    return str(api['id'])[(len("http://www.programmableweb.com/api/")):]

def get_api_full_name(api):
    return "http://www.programmableweb.com/api/%s" % api

def get_mashup_name(mashup):
    return str(mashup['id'])[(len("http://www.programmableweb.com/mashup/")):]

def get_mashup_full_name(mashup):
    return "http://www.programmableweb.com/mashup/%s" % mashup

class CMACForm():

    data_source = None
    
    related_mashups = None
    
    widget = None
    
    table = None
    
    add_btn = None
    
    graph_form = None
    
    highlighted_api = None
    
    highlighted_mashup = None

    #TODO: Make global config
    SERVICE_URL = "http://einstein.sv.cmu.edu:9002/svc/twoDimMap?model={0}&var={1}&start_time={2}&end_time={3}&lon1={4}&lon2={5}&lat1={6}&lat2={7}&months={8}&scale={9}"
    
    def show_main_window(self):
        self.graph_form = matplotlibWidget()
        if self.widget:
            self.widget.destroy()
            self.widget = None;
        self.widget = QWidget()
        self.widget.setMinimumSize(800, 600)

        ds_label = QLabel(self.widget)
        ds_label.setText("Data Source:")
        ds_label.move(30,20)
        self.ds = QtGui.QComboBox(self.widget)
        self.ds.addItem("NASA/MODIS")
        self.ds.addItem("NASA/AMSRE")
        self.ds.move(30, 40)

        var_label = QLabel(self.widget)
        var_label.setText("Variable Name:")
        var_label.move(150,20)
        self.var = QtGui.QComboBox(self.widget)
        self.var.addItem("Precipitation Flux")
        self.var.addItem("Total Cloud Fraction")
        self.var.move(150, 40)
        self.var.setCurrentIndex(1)
        
        self.sdate = QTextEdit("2004-01", self.widget)
        self.sdate.move(30, 100)
        self.sdate.setFixedWidth(100)
        self.sdate.setFixedHeight(30)
#        print self.sdate.toPlainText()

        sdate_label = QLabel(self.widget)
        sdate_label.setText("Start Date")
        sdate_label.move(30, 80)

        self.edate = QTextEdit("2004-12", self.widget)
        self.edate.move(150, 100)
        self.edate.setFixedWidth(100)
        self.edate.setFixedHeight(30)

        edate_label = QLabel(self.widget)
        edate_label.setText("End Date")
        edate_label.move(150, 80)

        self.slat = QTextEdit("-90", self.widget)
        self.slat.move(270, 100)
        self.slat.setFixedWidth(100)
        self.slat.setFixedHeight(30)

        slat_label = QLabel(self.widget)
        slat_label.setText("Start Lat (deg)")
        slat_label.move(270, 80)

        self.elat = QTextEdit("90", self.widget)
        self.elat.move(390, 100)
        self.elat.setFixedWidth(100)
        self.elat.setFixedHeight(30)

        elat_label = QLabel(self.widget)
        elat_label.setText("End Lat (deg)")
        elat_label.move(390, 80)

        self.slon = QTextEdit("0", self.widget)
        self.slon.move(510, 100)
        self.slon.setFixedWidth(100)
        self.slon.setFixedHeight(30)

        slon_label = QLabel(self.widget)
        slon_label.setText("Start Lon (deg)")
        slon_label.move(510, 80)

        self.elon = QTextEdit("360", self.widget)
        self.elon.move(630, 100)
        self.elon.setFixedWidth(100)
        self.elon.setFixedHeight(30)

        elon_label = QLabel(self.widget)
        elon_label.setText("End Lon (deg)")
        elon_label.move(630, 80)

        self.cb1 = QtGui.QCheckBox('January', self.widget)
        self.cb1.move(30,160)
        self.cb1.setChecked(True)
        self.cb2 = QtGui.QCheckBox('February', self.widget)
        self.cb2.move(130,160)
        self.cb2.setChecked(True)
        self.cb3 = QtGui.QCheckBox('March', self.widget)
        self.cb3.move(230,160)
        self.cb3.setChecked(True)
        self.cb4 = QtGui.QCheckBox('April', self.widget)
        self.cb4.move(330,160)
        self.cb4.setChecked(True)
        self.cb5 = QtGui.QCheckBox('May', self.widget)
        self.cb5.move(430,160)
        self.cb5.setChecked(True)
        self.cb6 = QtGui.QCheckBox('June', self.widget)
        self.cb6.move(530,160)
        self.cb6.setChecked(True)
        self.cb7 = QtGui.QCheckBox('July', self.widget)
        self.cb7.move(30,200)
        self.cb7.setChecked(True)
        self.cb8 = QtGui.QCheckBox('August', self.widget)
        self.cb8.move(130,200)
        self.cb8.setChecked(True)
        self.cb9 = QtGui.QCheckBox('September', self.widget)
        self.cb9.move(230,200)
        self.cb9.setChecked(True)
        self.cb10 = QtGui.QCheckBox('October', self.widget)
        self.cb10.move(330,200)
        self.cb10.setChecked(True)
        self.cb11 = QtGui.QCheckBox('November', self.widget)
        self.cb11.move(430,200)
        self.cb11.setChecked(True)
        self.cb12 = QtGui.QCheckBox('December', self.widget)
        self.cb12.move(530,200)
        self.cb12.setChecked(True)

        cscale_label = QLabel(self.widget)
        cscale_label.setText("Color Scale")
        cscale_label.move(30, 240)
        self.rbg = QtGui.QButtonGroup(self.widget)
        self.rb1 = QtGui.QRadioButton('Linear', self.widget)
        self.rb1.move(130,240)

        self.rb2 = QtGui.QRadioButton('Logarithmic', self.widget)
        self.rb2.move(230,240)
        self.rbg.addButton(self.rb1)
        self.rbg.addButton(self.rb2)
        self.rb1.setChecked(True)
#        print self.rb1.isChecked()
        self.btn_call_service = QtGui.QPushButton("Call Service", self.widget)
        self.btn_call_service.move(30,280)
        self.btn_call_service.clicked.connect(self.button_call_service)


        btn_api = QtGui.QPushButton("Recommend Modules", self.widget)
        btn_api.move(30, 20)
        btn_api.hide()

        btn_mashup = QtGui.QPushButton("Recommend Workflows", self.widget)
        btn_mashup.move(200, 20)
        btn_mashup.hide()
        self.widget.show()

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
            data = index.model().headerData(0,Qt.Horizontal).toString()
            newIndex = index.model().index(row, 0)
            if data == "API":
                api_id = get_api_full_name(newIndex.model().data(newIndex).toString())
                api = self.data_source.api_by_id(api_id)
                print api
                mashups = self.data_source.mashups_by_api(api)
                apis = []
                for mashup in mashups:
                    apis.extend(self.data_source.apis_by_mashup(mashup))
                self.graph_form.draw_apis(apis, api, self.highlighted_api)
            else:
                mashup_id = get_mashup_full_name(newIndex.model().data(newIndex).toString())
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
        for api in apis:
            model.setData(model.index(row, 0), QVariant(get_api_name(api)))
            model.setData(model.index(row, 1), QVariant(api['protocols']))
            model.setData(model.index(row, 2), QVariant(api['provider']))
            model.setData(model.index(row, 3), QVariant(api['version']))
            row += 1

        model.setHeaderData(0, Qt.Horizontal, QVariant("Module"))
        model.setHeaderData(1, Qt.Horizontal, QVariant("Protocol"))
        model.setHeaderData(2, Qt.Horizontal, QVariant("Provider"))
        model.setHeaderData(3, Qt.Horizontal, QVariant("Version"))

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
            model.setData(model.index(row, 0), QVariant(get_mashup_name(mashup)))
            model.setData(model.index(row, 1), QVariant(mashup['title']))
            model.setData(model.index(row, 2), QVariant(mashup['self']))
            model.setData(model.index(row, 3), QVariant(mashup['description']))
            
            row += 1
        
        model.setHeaderData(0, Qt.Horizontal, QVariant("Workflow"))
        model.setHeaderData(1, Qt.Horizontal, QVariant("Short Description"))
        model.setHeaderData(2, Qt.Horizontal, QVariant("Provider"))
        model.setHeaderData(3, Qt.Horizontal, QVariant("Detailed Info"))

#        model.setHeaderData(0, Qt.Horizontal, QVariant("Info"))
#        model.setHeaderData(1, Qt.Horizontal, QVariant("Title"))
#        model.setHeaderData(2, Qt.Horizontal, QVariant("self"))
#        model.setHeaderData(3, Qt.Horizontal, QVariant("Description"))

        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.add_btn.show()


    def button_call_service(self):
        """
        Trigger to call JPL's service
        """
        var_dict = {"Total Cloud Fraction" : "clt",
                        "Surface Temperature" : "ts",
                        "Sea Surface Temperature" : "tos",
                        "Precipitation Flux" : "pr",
                        "Eastward Near-Surface Wind" : "uas",
                        "Northward Near-Surface Wind" : "vas",
                        "Near-Surface Wind Speed" : "sfcWind",
                        "Sea Surface Height" : "zos",
                        "Leaf Area Index" : "lai",
                        "Equivalent Water Height Over Land" : "zl",
                        "Equivalent Water Height Over Ocean" : "zo",
                        "Ocean Heat Content Anomaly within 700 m Depth" : "ohc700",
                        "Ocean Heat Content Anomaly within 2000 m Depth" : "ohc2000",
                        "Surface Downwelling Longwave Radiation" : "rlds",
                        "Surface Downwelling Shortwave Radiation" : "rlus",
                        "Surface Upwelling Longwave Radiation" : "rsds",
                        "Surface Upwelling Shortwave Radiation" : "rsus",
                        "Surface Downwelling Clear-Sky Longwave Radiation" : "rldscs",
                        "Surface Downwelling Clear-Sky Shortwave Radiation" : "rsdscs",
                        "Surface Upwelling Clear-Sky Shortwave Radiation" : "rsuscs",
                        "TOA Incident Shortwave Radiation" : "rsdt",
                        "TOA Outgoing Clear-Sky Longwave Radiation" : "rlutcs",
                        "TOA Outgoing Longwave Radiation" : "rlut",
                        "TOA Outgoing Clear-Sky Shortwave Radiation" : "rsutcs",
                        "TOA Outgoing Shortwave Radiation" : "rsut"}
        a1 = re.sub('/', '_', str(self.ds.currentText()))
        a2 = var_dict[str(self.var.currentText())]
        a3 = re.sub('-', '', str(self.sdate.toPlainText()))
        a4 = re.sub('-', '',str(self.edate.toPlainText()))
        a5 = self.slon.toPlainText()
        a6 = self.elon.toPlainText()
        a7 = self.slat.toPlainText()
        a8 = self.elat.toPlainText()
        months = [self.cb1, self.cb2, self.cb3, self.cb4, self.cb5, self.cb6, self.cb7, self.cb8, self.cb9, self.cb10, self.cb11, self.cb12]
        months = [x.isChecked() for x in months]
        a9 = []
        for i in range(0,12):
            if months[i]:
                a9.append(str(i+1))
        a9 = ",".join(a9)
        a10 = 0 if self.rb1.isChecked() else 4
        r = requests.get(self.SERVICE_URL.format(a1,a2,a3,a4,a5,a6,a7,a8,a9, a10))
        print r.text
        

        
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
                model.setData(model.index(row, 0), QVariant(get_api_name(obj)))
                model.setData(model.index(row, 1), QVariant(obj['protocols']))
                model.setData(model.index(row, 2), QVariant(obj['provider']))
            else:
                model.setData(model.index(row, 3), QVariant(get_mashup_name(obj)))
            row += 1

        model.setHeaderData(0, Qt.Horizontal, QVariant("API"))
        model.setHeaderData(1, Qt.Horizontal, QVariant("Protocols"))
        model.setHeaderData(2, Qt.Horizontal, QVariant("Provider"))
        model.setHeaderData(3, Qt.Horizontal, QVariant("Mashup"))
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
                model.setData(model.index(row, 1), QVariant(get_api_name(obj)))
                model.setData(model.index(row, 2), QVariant(obj['protocols']))
                model.setData(model.index(row, 3), QVariant(obj['provider']))
                model.setData(model.index(row, 4), QVariant(obj['version']))
                trust  = requests.get('http://localhost:9000/getReputation/Luis Ramos').content
                #model.setData(model.index(row, 5), QVariant(str(random.random())))
                model.setData(model.index(row, 5), QVariant(trust))
            else:
                model.setData(model.index(row, 0), QVariant(get_mashup_name(obj)))
            row += 1

        model.setHeaderData(0, Qt.Horizontal, QVariant("Mashup"))
        model.setHeaderData(1, Qt.Horizontal, QVariant("API"))
        model.setHeaderData(2, Qt.Horizontal, QVariant("Protocols"))
        model.setHeaderData(3, Qt.Horizontal, QVariant("Provider"))
        model.setHeaderData(4, Qt.Horizontal, QVariant("Version"))
        model.setHeaderData(5, Qt.Horizontal, QVariant("Trust"))

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
            #pass?
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

