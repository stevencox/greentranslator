import json
import logging
import os
import traceback
import swagger_client
import unittest
from string import Template
from swagger_client.rest import ApiException
from SPARQLWrapper import SPARQLWrapper2, JSON
from greentranslator.provenance import provenance
from greentranslator.provenance import ProvenanceQuery

class LoggingUtil(object):
    """ Logging utility controlling format and setting initial logging level """
    @staticmethod
    def init_logging (name):
        FORMAT = '%(asctime)-15s %(filename)s %(funcName)s %(levelname)s: %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.INFO)
        return logging.getLogger(name)
logger = LoggingUtil.init_logging (__file__)

class TripleStore(object):
    """ Connect to a SPARQL endpoint and provide services for loading and executing queries."""
    def __init__(self, hostname):
        self.service =  SPARQLWrapper2 (hostname)

    @provenance()
    def execute_query (self, query):
        """ Execute a SPARQL query.

        :param query: A SPARQL query.
        :return: Returns a JSON formatted object.
        """
        self.service.setQuery (query)
        self.service.setReturnFormat (JSON)
        return self.service.query().convert ()
    def execute_query_file (self, query_file):
        """ Execute a SPARQL query based on a file.

        :param query_file: The file containing th query.
        :return: Returns a JSON formatted object.
        """
        result = None
        with open (query_file, "r") as stream:
            query = stream.read ()
            result = self.execute_query (query)
        return result

class DataLake(object):
    def __init__(self, name):
        self.name = name

class Translator (DataLake):
    def __init__(self, name):
        DataLake.__init__(self, name)

class Exposures (object):

    """ Services relating to environmental exposures. """
    def __init__(self, exposures):
        self.exposures = exposures

    def get_by_coordinates (self, exposure_type, latitude, longitude, radius):
        """ Returns paginated list of available latitude, longitude coordinates for given exposure_type.
            Optionally the user can provide a latitude, longitude coordinate with a radius in meters to
            discover if an exposure location is within the requested range
        :param exposure_type: Type of exposure (pm25, o3)
        :param latitude: Float representing a latitude.
        :param longitude: Float representing a longitude.
        :param radius: Radius in meters."""
        result = self.exposures. \
                  exposures_exposure_type_coordinates_get(exposure_type,
                                                          latitude=latitude,
                                                          longitude=longitude,
                                                          radius=radius)
        return json.loads ("{}".format (result).replace ("'", '"'))

    def get_scores (self, exposure_type, start_date, end_date, exposure_point):
        """ Retrieve the computed exposure score(s) for a given environmental exposure factor, time period, and location(s)

        :param exposure_type: The name of the exposure factor (pm25, o3)
        :param start_date: The starting date to obtain exposures for (example 1985-04-12 is April 12th 1985). Time of day is ignored.
        :param end_date: The ending date to obtain exposures for (example 1985-04-13 is April 13th 1985)
        :param exposure_point: A description of the location(s) to retrieve the exposure for. Locaton may be a single geocoordinate (example '35.720278,-79.176389') or a semicolon separated list of geocoord:dayhours giving the start and ending hours on specific days of the week at that location (example '35.720278,-79.176389,Sa0813;35.720278,-79.176389,other') 
        """
        return self.exposures. \
            exposures_exposure_type_scores_get (exposure_type = exposure_type,
                                                start_date = start_date,
                                                end_date = end_date,
                                                exposure_point = exposure_point)

    def get_values (self, exposure_type, start_date, end_date, exposure_point):
        """ Retrieve the computed exposure value(s) for a given environmental exposure factor, time period, and location(s)

        :param exposure_type: The name of the exposure factor (pm25, o3)
        :param start_date: The starting date to obtain exposures for (example 1985-04-12 is April 12th 1985). Time of day is ignored.
        :param end_date: The ending date to obtain exposures for (example 1985-04-13 is April 13th 1985)
        :param exposure_point: A description of the location(s) to retrieve the exposure for. Locaton may be a single geocoordinate (example '35.720278,-79.176389') or a semicolon separated list of geocoord:dayhours giving the start and ending hours on specific days of the week at that location (example '35.720278,-79.176389,Sa0813;35.720278,-79.176389,other')
        """
        return self.exposures. \
                exposures_exposure_type_values_get (exposure_type = exposure_type,
                                                    start_date = start_date,
                                                    end_date = end_date,
                                                    exposure_point = exposure_point)
class BioChemical(object):
    """ Generic service endpoints for medical and bio-chemical data. This set comprises portions of
    chem2bio2rdf, Monarch, and CTD environmental exposures."""
    def __init__(self, triplestore):
        self.triplestore = triplestore
    def get_template (self, query_name):
        query = None
        fn = os.path.join(os.path.dirname(__file__), 'query', '{0}.sparql'.format (query_name))
        with open (fn, 'r') as stream:
            text = stream.read ()
            query = Template (text)
            logger.debug ('query template: {0}', query)
        return query
    @provenance()
    def query_biochem (self, query):
        """ Execute and return the result of a SPARQL query. """
        return self.triplestore.execute_query (query)

    def get_exposure_conditions (self, chemicals):
        """ Identify conditions (MeSH IDs) triggered by the specified stressor agent ids (also MeSH IDs).

        :param chemicals: List of IDs for substances of interest.
        :type chemicals: list of MeSH IDs, eg. D052638
        """
        id_list = ' '.join (list(map (lambda d : "( mesh:{0} )".format (d), chemicals)))
        text = self.get_template ("ctd_gene_expo_disease").safe_substitute (chemicals=id_list)
        results = self.triplestore.execute_query (text)
        return list(map (lambda b : {
            "chemical" : b['chemical'].value,
            "gene"     : b['gene'].value,
            "pathway"  : b['kegg_pathway'].value,
            "pathName" : b['pathway_name'].value,
            "pathID"   : b['pathway_id'].value,
            "human"    : '(human)' in b['pathway_name'].value
        },
                         results.bindings))
        
    def get_drugs_by_condition (self, conditions):
        """ Get drugs associated with a set of conditions.

        :param conditions: Conditions to find associated drugs for.
        :type conditions: List of MeSH IDs for conditions, eg.: D001249
        """
        condition_list = ' '.join (list(map (lambda d : "( mesh:{0} )".format (d), conditions)))
        text = self.get_template ("get_drugs_by_disease").substitute (conditions=condition_list)
        results = self.triplestore.execute_query (text)
        return list(map (lambda b : b['generic_name'].value, results.bindings))

    def get_genes_pathways_by_disease (self, diseases):
        """ Get genes and pathways associated with specified conditions.
        
        :param diseases: List of conditions designated by MeSH ID.
        :return: Returns a list of dicts containing gene and path information.
        """
        diseaseMeshIDList = ' '.join (list(map (lambda d : "( mesh:{0} )".format (d), diseases)))
        text = self.get_template ("genes_pathways_by_disease").safe_substitute (diseaseMeshIDList=diseaseMeshIDList)
        results = self.triplestore.execute_query (text)
        return list(map (lambda b : {
            "uniprotGene" : b['uniprotGeneID'].value,
            "keggPath"    : b['keggPath'].value,
            "pathName"    : b['pathwayName'].value,
            "human  "     : '(human)' in b['pathwayName'].value
        },
        results.bindings))

class GreenQuery(ProvenanceQuery):

    def __init__(self, translator):
        ProvenanceQuery.__init__(self)
        self.translator = translator

    @provenance()
    def query_biochem (self, query):
        """ Execute and return the result of a SPARQL query. """
        return self.translator.biochem.query_biochem (query)

    @provenance()
    def get_exposure_conditions (self, chemicals):
        """ Identify conditions (MeSH IDs) triggered by the specified stressor agent ids (also MeSH IDs).

        :param chemicals: List of IDs for substances of interest.
        :type chemicals: list of MeSH IDs, eg. D052638
        """
        return self.translator.biochem.get_exposure_conditions (chemicals)
        
    @provenance()
    def get_drugs_by_condition (self, conditions):
        """ Get drugs associated with a set of conditions.

        :param conditions: Conditions to find associated drugs for.
        :type conditions: List of MeSH IDs for conditions, eg.: D001249
        """
        return self.translator.biochem.get_drugs_by_condition (conditions)

    @provenance()
    def get_genes_pathways_by_disease (self, diseases):
        return self.translator.biochem.get_genes_pathways_by_disease (diseases)

    @provenance()
    def expo_get_by_coordinates (self, exposure_type, latitude, longitude, radius):
        """ Returns paginated list of available latitude, longitude coordinates for given exposure_type.
            Optionally the user can provide a latitude, longitude coordinate with a radius in meters to
            discover if an exposure location is within the requested range
        :param exposure_type: Type of exposure (pm25, o3)
        :param latitude: Float representing a latitude.
        :param longitude: Float representing a longitude.
        :param radius: Radius in meters."""
        return self.translator.exposures.get_by_coordinates (exposure_type = exposure_type,
                                                             latitude = latitude,
                                                             longitude = longitude,
                                                             radius = radius)
    @provenance()
    def expo_get_scores (self, exposure_type, start_date, end_date, exposure_point):
        """ Retrieve the computed exposure score(s) for a given environmental exposure factor, time period, and location(s)

        :param exposure_type: The name of the exposure factor (pm25, o3)
        :param start_date: The starting date to obtain exposures for (example 1985-04-12 is April 12th 1985). Time of day is ignored.
        :param end_date: The ending date to obtain exposures for (example 1985-04-13 is April 13th 1985)
        :param exposure_point: A description of the location(s) to retrieve the exposure for. Locaton may be a single geocoordinate (example '35.720278,-79.176389') or a semicolon separated list of geocoord:dayhours giving the start and ending hours on specific days of the week at that location (example '35.720278,-79.176389,Sa0813;35.720278,-79.176389,other') 
        """
        return self.translator.exposures.get_scores (exposure_type=exposure_type,
                                                     start_date=start_date,
                                                     end_date=end_date,
                                                     exposure_point=exposure_point)

    @provenance()
    def expo_get_values (self, exposure_type, start_date, end_date, exposure_point):
        return self.translator.exposures.get_values (exposure_type = exposure_type,
                                                     start_date = start_date,
                                                     end_date = end_date,
                                                     exposure_point = exposure_point)


class GreenTranslator (Translator):

    def __init__(self, name="greentranslator", config={}):
        """Initialize the GreenTranslator.

        :param config: Dict of configuration options. Empty by default. 'blaze_uri' can be configured to the SPARQL
                       endpoint for the Med-BioChem service.
        """
        Translator.__init__(self, name)
        self.config = config
        blaze_uri = None
        if 'blaze_uri' in config:
            blaze_uri = self.config ['blaze_uri']
        if not blaze_uri:
            blaze_uri = 'http://stars-blazegraph.renci.org/bigdata/sparql'
        self.blazegraph = TripleStore (blaze_uri)
        #self.exposures_uri = self.config ['exposures_uri']
        self.exposures = Exposures (swagger_client.DefaultApi ())
        self.biochem = BioChemical (self.blazegraph)

    def get_query (self):
        return GreenQuery (translator=self)

class TestExposures(unittest.TestCase):
    query = GreenTranslator().get_query ()
    def test_coordinates(self):
        print ("Get available exposure coordinates.")
        exposure = self.query. \
                   expo_get_by_coordinates (exposure_type = 'pm25',
                                            latitude      = '',
                                            longitude     = '',
                                            radius        = '0')
        self.assertEqual (exposure[0]['latitude'], '35.7795897')
    def test_scores(self):
        print ("Get exposure scores.")
        scores = self.query. \
                 expo_get_scores (exposure_type = 'pm25',
                                  start_date = '2010-01-07',
                                  end_date = '2010-01-31',
                                  exposure_point = '35.9131996,-79.0558445')
        self.assertEqual (scores[0].value, '4.714285714285714')
    def test_values(self):
        print ("Get exposure values")
        values = self.query. \
                 expo_get_values (exposure_type = 'pm25',
                                  start_date = '2010-01-07',
                                  end_date = '2010-01-31',
                                  exposure_point = '35.9131996,-79.0558445')
        self.assertEqual (values[0].value, '17.7199974060059')
    def test_show_provenance (self):
        print (self.query.prov_json ())

class TestBioChem (unittest.TestCase):
    query = GreenTranslator().get_query ()
    def test_drugs_by_condition (self):
        print ("Test get drugs by condition")
        drugs = self.query. \
                get_drugs_by_condition (conditions=[ "d001249" ])
        self.assertEqual (sorted(drugs)[0], '(11-BETA)-11,21-DIHYDROXY-PREGN-4-ENE-3,20-DIONE')
    def test_genes_pathways (self):
        print ("Test get genes/pathways by condition")
        conditions = [ 'd001249', 'd003371', 'd001249' ]
        genes_paths = self.query.get_genes_pathways_by_disease (diseases = conditions)
        genes = sorted (map(lambda gp: gp['uniprotGene'], genes_paths))
        self.assertEqual (genes[0], 'http://chem2bio2rdf.org/uniprot/resource/gene/ABCB1')
    def test_get_exposure_conditions (self):
        print ("Test get exposure conditions")
        exposures = self.query.get_exposure_conditions (chemicals = [ 'D052638' ])
        self.assertEqual (exposures[0]['chemical'], 'http://bio2rdf.org/mesh:D052638')
    def test_show_provenance (self):
        print ("BioChem query provenance:")
        print (self.query.prov_json ())

if __name__ == '__main__':
    unittest.main()
