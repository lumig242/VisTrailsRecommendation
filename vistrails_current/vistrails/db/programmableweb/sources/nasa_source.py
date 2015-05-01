'''
Created on Sep 30, 2012

@author: xiaoxiao
'''
from pymongo import Connection
import numpy
from scipy.sparse import coo_matrix
import scipy as sp
import string

class DataSource(object):
    '''
    classdocs
    '''
    db = None
    #Mashup x API. 0/1 for containment
    Q_matrix = None
    #Cols are terms in description, rows are API indices.
    description_matrix = None
    api_tag_to_index = {}
    api_link_to_index = {}
    api_ix_to_link = []

    def __init__(self):
        '''
        Constructor
        '''
        self.db = Connection().Nasa
#        self.another_db = Connection().programmable_web

    def get_member_mashups_collections(self):
        member_mashups = self.another_db.member_mashup.find()
        return [member_mashup for member_mashup in member_mashups]

    def search_api(self, key):
        """
        Search api by key word
        """
        apis = self.db.nasadatasets.find({"dataset": {"$regex": key}})
        return [api for api in apis]

    def search_api_similarity(self, selected_api, K = 10):
        """
        Search for APIs using similarity and past history.
        """
        return None
        

    def search_mashup(self, key):
        """
        Search mashup by key word
        """
        mashups = self.db.nasadatasets.find({"dataset": {"$regex": key}})
        return [mashup for mashup in mashups]

    def mashup_with_apis(self):
        """
        All mashups with the apis they are using
        """
        pairs = self.pairs()
        mashup_map = {}
        for pair in pairs:
            if mashup_map.get(pair["mashup"]) == None:
                mashup_map[pair["mashup"]] = []
            mashup_map[pair["mashup"]].append(pair["api"])
        return mashup_map

    def api_with_mashups(self):
        """
        All apis with the mashups which are used.
        """
        pairs = self.pairs()
        api_map = {}
        for pair in pairs:
            if api_map.get(pair["api"]) == None:
                api_map[pair["api"]] = []
            api_map[pair["api"]].append(pair["mashup"])
        return api_map

    def apis(self):
        """
        All apis
        """
        apis = self.db.nasadatasets.find()
        return [api for api in apis]
    
    def mashups(self):
        """
        All mashups
        """
        mashups = self.db.nasadatasets.find()
        return [mashup for mashup in mashups]

    def pairs(self):
        """
        All pairs.
        A pair is entry indicating a mashup using a certain api.
        """
        pairs = self.db.pairs.find()
        return [pair for pair in pairs]
    
    def api_by_id(self, _id):
        """
        Find api by id
        """
        apis = self.db.apis.find({"id": _id})
        result = [api for api in apis]
        if result:
            return result[0]

    def mashup_by_id(self, _id):
        """
        Find mashup by id
        """
        mashups = self.db.mashups.find({"id": _id})
        result = [mashup for mashup in mashups]
        if result:
            return result[0]

    def mashups_by_api(self, api):
        """
        Find mashups which use the given api
        """
        pairs = self.db.pairs.find({"api": api["id"]})
        mashups = []
        for pair in pairs:
            mashups.extend([mashup for mashup in self.db.mashups.find({"id": pair["mashup"]})])
        return mashups

    def apis_by_mashup(self, mashup):
        """
        Find the apis which is used by the given mashup
        """
        pairs = self.db.pairs.find({"mashup": mashup["id"]})
        apis = []
        for pair in pairs:
            apis.extend([api for api in self.db.apis.find({"id": pair["api"]})])
        return apis

    def apis_by_category(self, category):
        apis = self.db.apis.find({"category": category})
        return [api for api in apis]

