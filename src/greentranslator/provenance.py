""" This part is generic provenance infrastructure """

import importlib
from functools import wraps
import json 
import prov.model as prov
from datetime import datetime
from datetime import date
import re
import threading
from threading import current_thread
import traceback
import uuid

class QueryResponseProvenance(object):
    """ Abstract W3C PROV model of the provenance of components of a complex query. """
    def __init__(self, default_ns, namespaces=[]):
        """ Specify a default namespace and associated sub namespaces """
        self.document = prov.ProvDocument ()
        self.default_ns = default_ns
        self.document.set_default_namespace (self.default_ns)
        self.namespaces = namespaces
        self.subspaces = {}
        for namespace in self.namespaces:
            self.subspaces[namespace] = self.add_namespace (self.default_ns, namespace)
    def add_namespace (self, root, qualifier):
        subspace = "{0}{1}".format (root, qualifier)
        self.document.add_namespace (qualifier, subspace)
        return subspace
    def add_entity (self, name, tuples):
        self.document.entity (name, tuples)
    def add_data_source (self, name, entity):
        self.entity (name, entity.to_tuple ())
    def add_algorithm (self, name, start, end=None):
        #assert name in self.namespaces, "Name must be in list of namespaces"
        attributes = [ ( "TODO:id", get_provenance_id () ) ]
        if end:
            self.document.activity (name, start, end, other_attributes=attributes)
        else:
            self.document.activity (name, start, other_attributes=attributes)
    def get_time (self):
        return datetime.now ().strftime ("%Y-%m-%dT%H:%M:%S")
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.document.get_provn ()
 
class AbstractEntity(object):
    def __init__(self, type, namespace, attributes=[]):
        self.attributes = []
        self.namespace = namespace
        self.attr_keys = {}
        self.add_attribute (prov.PROV_TYPE, type)
        for a in attributes:
            assert len(a) == 2, "Attribute components must be len==2 arrays"
            self.add_attribute (a[0], a[1])
    def add_attribute (self, iri, value):
        key = '{0}@{1}'.format (iri, value)
        if not key in self.attr_keys:
            self.attributes.append ((iri, value))
            self.attr_keys[key] = 1
    def to_tuple (self):
        return tuple(self.attributes)
  
""" DataLake Support - encapsulate provenance behaviors specific to
    specific classes of data resources """
 
class DataLakeProvenance(QueryResponseProvenance):
    PREFIX = re.compile ('^prefix ', re.I)
    def __init__(self, default_ns, namespaces=[]):
        QueryResponseProvenance.__init__(self, default_ns, namespaces)
 
    def parse_sparql (self, text, source_map, type="data"):
        sources = {}
        for line in text.split ('\n'):
            line = ' '.join (line.strip ().split ())
            match = self.PREFIX.match (line)
            if match is None:
                continue
            if True:
                parts = line.strip().split (' ')
                if len(parts) >= 3:
                    iri = parts[2].strip ()
                    e = None
                    for k, v in source_map.items ():
                        if k in iri:
                            if v in sources:
                                e = sources[v]
                            else:
                                e = AbstractEntity (type, '{0}{1}'.format (self.default_ns, v))
                                sources[v] = e
                            e.add_attribute ('TODO:id', get_provenance_id ())
                            e.add_attribute ('src', v)
                    if e is None:
                        e = AbstractEntity (type, 'http://purl.data.org/')
                        e.add_attribute ('TODO:id', get_provenance_id ())
                        e.add_attribute ('src', iri)
                        self.add_entity ('data', e.to_tuple ())
        for k, v in sources.items ():
            self.add_entity ('data', v.to_tuple ())
 
""" And now we get really specific about one data lake, the green translator. """
 
class GreenTranslatorProvenance (DataLakeProvenance):
    def __init__(self):
        DataLakeProvenance.__init__(
            self,
            default_ns = 'http://purl.translator.org/prov/',
            namespaces = [
                'expo', 'biochem', 'TODO',                          # data sources
                'expo.pm25-o3', 'clinical.med.prescribed', 'blazegraph' # algorithms / assumptions
            ])
    def parse_sparql (self, query):
        super(GreenTranslatorProvenance, self).parse_sparql (
            query,
            source_map = {
                '<http://chem2bio2rdf.org/ctd/' : 'c2b2r.ctd',
                'GO_' : 'GO',
                '<http://chem2bio2rdf.org/drugbank' : 'c2b2r.drugbank',
                'monarch' : 'monarch'
            },
            type="biochem:data")

class ProvenanceQuery(object):

    """ Query with provenance """
    def __init__(self):
        self.provenance = GreenTranslatorProvenance ()

    def get_prov (self):
        return json.loads (self.provenance.document.serialize(format='json'))

    def prov_json (self):
        return json.dumps (json.loads (self.provenance.document.serialize(format='json')),
                           indent=2)

threadProvenance = threading.local()

def get_thread_prov_container (initialize=False):
    result = None
    initialized = getattr(threadProvenance, 'initialized', None)
    if initialized is None:
        if initialize:
            print("Initializing thread provenance @thread: {0}".format (current_thread().name))
            threadProvenance.initialized = True
            result = threadProvenance
        else:
            raise "Thread provenance not initialized and initialize set to false @thread: {0}".format (current_thread().name)
    else:
        #print ("Provenance already initialized @thread: {0}".format (current_thread().name))
        result = threadProvenance
    return result
def register_provenance (p):
    container = get_thread_prov_container (initialize=True)
    container.provenance = p
    container.uuid = "http://id.org/{0}".format (uuid.uuid4())
def get_provenance ():
    return get_thread_prov_container ().provenance
def get_provenance_id ():
    return get_thread_prov_container ().uuid
def unregister_provenance ():
    container = get_thread_prov_container()
    container.provenance = None
    container.uuid = None

provenance_conf = {

    "expo_get_scores" : {
        "type" : "expo:score",
        "sources" : {
            "expo" : "http://purl.expo.org/unc/cdwh",
            "expo" : "http://purl.expo.org/unc/ie"
        }
    },
    "expo_get_values" : {
        "type" : "expo:value",
        "sources" : {
            "expo" : "http://purl.expo.org/unc/cdwh",
            "expo" : "http://purl.expo.org/unc/ie"
        }
    },

    # BioChem

    "execute_query" : {
        "handler" : {
            "module" : "greentranslator.provenance",
            "function_name" : "parse_sparql_query_provenance"
        },
        "type" : "biochem:sparql",
        "sources" : {
            "biochem" : "http://purl.biochem.org/c2b2r"
        }
    },

    "get_exposure_conditions" : {
        "type" : "biochem:exposures",
        "sources" : {
            "biochem" : "http://purl.biochem.org/c2b2r"
        }
    },
    "get_genes_pathways_by_disease" : {
        "type" : "biochem:genes_pathways_by_disease",
        "sources" : {
            "biochem" : "http://purl.biochem.org/c2b2r"
        }
    },
    "get_drugs_by_condition" : {
        "type" : "biochem:get_drugs_by_condition",
        "sources" : {
            "biochem" : "http://purl.biochem.org/c2b2r"
        }
    }
}

def parse_sparql_query_provenance (prov_obj, function, args, kwargs, start, end):
    prov_obj.add_algorithm ('blazegraph', start, end)
    prov_obj.parse_sparql (args[1])

def provenance (data_source=None):
    def provenance_aspect (function):
        @wraps(function)
        def wrapper (*args, **kwargs):
            func_name = function.__name__
            a_self = args[0]
            if isinstance (a_self, ProvenanceQuery):
                prov_obj = a_self.provenance                
                register_provenance (a_self.provenance)
            else:
                prov_obj = get_provenance ()

            start = prov_obj.get_time ()
            val = function(*args, **kwargs)
            end = prov_obj.get_time ()
            
            try:
                if prov_obj:
                    for op, desc in provenance_conf.items ():
                        if op == func_name:
                            prov_obj.add_algorithm (func_name, start, end)
                            e = AbstractEntity (func_name, 'TODO:schema')
                            e.add_attribute ('TODO:id', get_provenance_id ())
                            e.add_attribute (desc['type'], '{0}({1}{2})'.format (func_name, args[1:], kwargs))
                            prov_obj.add_entity ("TODO:schema", e.to_tuple ())

                            if 'handler' in desc:
                                handler = desc['handler']
                                module = importlib.import_module (handler['module'])
                                handler_func = getattr (module, handler['function_name'])
                                handler_func (prov_obj, function, args, kwargs, start, end)

                            for source, iri in desc['sources'].items ():
                                e = AbstractEntity (source, iri)
                                e.add_attribute ('src', source)
                                e.add_attribute ('TODO:id', get_provenance_id ())
                                prov_obj.add_entity (source, e.to_tuple ())
            except:
                traceback.print_exc ()
                print ("Error recording provenance")

            unregister_provenance ()
            return val            
        return wrapper
    return provenance_aspect

