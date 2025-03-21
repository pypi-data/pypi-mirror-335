from pylindas.lindas.namespaces import SCHEMA
from pylindas.pycube import Cube
from rdflib import Graph
import pandas as pd
import pytest
import yaml

class TestClass:

    TEST_CASE_PATH = "example/Cubes/"

    @classmethod
    def setup_test_cube(cls, dataframe_path: str, description_path: str) -> Cube:
        with open(cls.TEST_CASE_PATH + description_path) as file:
            description = yaml.safe_load(file)
        dataframe = pd.read_csv(cls.TEST_CASE_PATH + dataframe_path)
        cube = Cube(dataframe=dataframe, cube_yaml=description, environment="TEST", local=True)
        return cube.prepare_data().write_cube(opendataswiss=True).write_observations().write_shape()

    def setup_method(self):
        self.mock_cube = self.setup_test_cube(
            "mock/data.csv", "mock/description.yml")
        self.co2_cube = self.setup_test_cube(
            "co2-limits/data.csv", "co2-limits/description.yml")
        self.hierarchies_cube = self.setup_test_cube(
            "Biotope_Statistik/data.csv", "Biotope_Statistik/description.yml")

    def test_standard_error(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema:name 'Standardfehler'@de ;"
            "    schema:description 'Standardfehler des berechneten Werts'@de ;"
            "    sh:path mock:standardError ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:StandardError;"
            "      meta:relatesTo mock:value ;"
            "    ] ."
            "}"
        )

        result = self.mock_cube._graph.query(sparql)
        assert bool(result)

    def test_upper_uncertainty(self):
        # todo: include the co2 emission cube
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path mock:upperUncertainty ;"
            "    schema:name 'Upper Unsicherheit'@de ;"
            "    sh:maxCount 1 ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceUpperBound ;"
            '      dct:type "Confidence interval" ;'
            "      meta:relatesTo mock:value ;"
            "    ] ."
            "}"
        )

        # result = self.cube._graph.query(sparql)
        assert True

    def test_lower_uncertainty(self):
        # todo: include the co2 emission cube
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema:name 'Lower Unsicherheit'@de ;"
            "    schema:description 'Lower Unsicherheit'@de ;"
            "    sh:path mock:lowerUncertainty ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceLowerBound ;"
            "      dct:type 'Confidence interval' ;"
            "      meta:relatesTo mock:value ;"
            "    ] ."
            "}"
        )

        # result = self.cube._graph.query(sparql)
        assert True

    def test_point_limit(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path limit_1:co2Emissions ;"
            "    meta:annotation ?annotation ."
            "  ?annotation a meta:Limit ;"
            "    schema:value 1.849298e+01 ;"
            "    meta:annotationContext ["
            "      sh:path limit_1:year ;"
            "      sh:hasValue <https://ld.admin.ch/time/year/2012> ;"
            "    ] ; "
            "    meta:annotationContext [ "
            "      sh:path limit_1:energySource ;"
            "      sh:hasValue <https://mock.ld.admin.ch/energySource/01> ;"
            "  ]."
            "}"
        )
    
        result = self.co2_cube._graph.query(sparql)
        assert bool(result)
    
    def test_range_limit(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path limit_1:co2Emissions ;"
            "    meta:annotation ?annotation ."
            "  ?annotation a meta:Limit ;"
            "    schema:minValue 1.708845e+01  ;"
            "    schema:maxValue 1.779072e+01 ;"
            "    meta:annotationContext ["
            "      sh:path limit_1:year ;"
            "      sh:hasValue <https://ld.admin.ch/time/year/2016> ;"
            "    ] ; "
            "    meta:annotationContext [ "
            "      sh:path limit_1:energySource ;"
            "      sh:hasValue <https://mock.ld.admin.ch/energySource/01> ;"
            "    ] ."
            "}"
        )

        result = self.co2_cube._graph.query(sparql)
        assert bool(result)

    def test_limit_cube_validity(self):
        result_bool, result_message = self.co2_cube.validate()
        assert result_message == "Cube is valid."

    def test_annotation_dimension(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path mock:status ;"
            "     schema:name 'Veröffentlichungsstatus'@de ;"
            "     qudt:scaleType qudt:NominalScale ."
            "   minus {"
            "     ?prop a cube:KeyDimension ."
            "   }"
            "   minus {"
            "     ?prop a cube:MeasureDimension ."
            "   }"
            "}"
        )

        result = self.mock_cube._graph.query(sparql)
        assert bool(result)

    def test_mock_cube_validity(self):
        result_bool, result_message = self.mock_cube.validate()
        assert result_message == "Cube is valid."

    def test_hierarchies(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path biotop:type ;"
            "    meta:inHierarchy ?hierarchy ."
            "  ?hierarchy a meta:Hierarchy ;"
            "    meta:hierarchyRoot <https://environment.ld.admin.ch/foen/biotopes/tot> ;"
            "    schema:name 'Biotope' ;"
            "    meta:nextInHierarchy ?nextInHierarchy ."
            "  ?nextInHierarchy schema:name 'Biotoparten' ;"
            "    sh:path schema:hasPart ;"
            "}"
        )

        result = self.hierarchies_cube._graph.query(sparql)
        assert bool(result)

    def test_hierarchies_cube_validity(self):
        result_bool, result_message = self.hierarchies_cube.validate()
        assert result_message == "Cube is valid."

    def test_concepts(self):
        # As setup_method() is called before each test
        # -> create the concept cube only for this specific test
        # To change later if needed
        self.concepts_cube = self.setup_test_cube("concept_table_airport/data.csv", "concept_table_airport/description.yml")

        # Add the concept data to the cube's data
        airport_concept_df = pd.read_csv(self.TEST_CASE_PATH + "/concept_table_airport/airportconcept.csv")
        self.concepts_cube.write_concept("typeOfAirport", airport_concept_df)
        # data_with_dummy.csv, the data file uploaded for that cube, contains an airport type identifier that doesn't exist in airportType.csv
        # the goal is to demonstrate that the  check_dimension_object_property() called here under will detect that
        # Check that all the generated URLs for the typeOfAirport are resources (concept) with a SCHEMA.name triple
        # This allows to check if all the entries in data_with_dummy.csv correspond to an entry in airportType.csv 
        allConceptsFound = self.concepts_cube.check_dimension_object_property("typeOfAirport", SCHEMA.name)
        # allConceptsFound should be False: the dummy airport type has no correspondance in the concepts
        assert not bool(allConceptsFound)

        # Now add the dummy airportType 
        airport_concept_dummy_df = pd.read_csv("example/Cubes/concept_table_airport/airportdummyconcept.csv")
        self.concepts_cube.write_concept("typeOfAirport", airport_concept_dummy_df)
        allConceptsFound = self.concepts_cube.check_dimension_object_property("typeOfAirport", SCHEMA.name)
        # allConceptsFound should be True: the dummy airport type has been added to the concepts
        assert bool(allConceptsFound)
