import osmnx as ox
import logging
import warnings

class Map:
    """
    Clase para manejar la creación y manipulación de grafos de mapas utilizando osmnx.
    
    Atributos:
    ----------
    _G : networkx.MultiDiGraph
        Grafo del mapa.
    _osm_file_name : str
        Nombre del archivo OSM.
    _graphml_file_name : str
        Nombre del archivo GraphML.
    """

    def __init__(self, value, arg="coordinates"):
        """
        Inicializa una instancia de la clase Map.
        
        Parámetros:
        -----------
        value : str o tuple
            Valor que se utilizará para crear el mapa. Puede ser un nombre de lugar, coordenadas o una ruta a un archivo GraphML.
        arg : str, opcional
            Tipo de argumento proporcionado en value. Puede ser "place_name", "coordinates" o "ox_graphml". Por defecto es "coordinates".
        """
        try:
            self._G = None  
            get_ox_map = {
                "place_name": self._map_place_name,  
                "coordinates": self._map_coordinates,  
                "ox_graphml": self._map_ox_graphml,
            }

            if arg in get_ox_map:  
                self._G = get_ox_map[arg](value)  
            self._osm_file_name = "" 
            self._graphml_file_name = "" 
            
        except Exception as error: 
            print("Error in Map constructor")
            logging.error(error) 

    def save_map_osm(self, file_name):
        """
        Guarda el grafo del mapa en un archivo OSM.

        Parámetros:
        -----------
        file_name : str
            Nombre del archivo donde se guardará el grafo en formato OSM.

        Devuelve:
        ---------
        bool
            True si la operación fue exitosa, de lo contrario lanza una excepción.
        """
        self._osm_file_name = f"{file_name}.osm.xml" 
        try:
            # Ajusta las configuraciones de osmnx para incluir etiquetas útiles y atributos de nodos y vías.
            utn = ox.settings.useful_tags_node
            oxna = ox.settings.osm_xml_node_attrs
            oxnt = ox.settings.osm_xml_node_tags
            utw = ox.settings.useful_tags_way
            oxwa = ox.settings.osm_xml_way_attrs
            oxwt = ox.settings.osm_xml_way_tags
            utn = list(set(utn + oxna + oxnt))
            utw = list(set(utw + oxwa + oxwt))
            ox.settings.all_oneway = True
            ox.settings.useful_tags_node = utn
            ox.settings.useful_tags_way = utw
            ox.save_graph_xml(self._G, filepath=self._osm_file_name)
            return self._osm_file_name  
        except Exception as error:  
            print("Graph convertion to OSM failed. Function save_map_osm")  
            raise error 

    def save_map_graphml(self, file_name):
        """
        Guarda el grafo del mapa en un archivo GraphML.

        Parámetros:
        -----------
        file_name : str
            Nombre del archivo donde se guardará el grafo en formato GraphML.

        Devuelve:
        ---------
        bool
            True si la operación fue exitosa, de lo contrario lanza una excepción.
        """
        self._graphml_file_name = f"{file_name}.graphml.xml"
        try:
            ox.save_graphml(self._G, self._graphml_file_name) 
            return self._graphml_file_name 
        except Exception as error:
            print("Graph convertion to GRAPHML failed. Function save_map_graphml")
            raise error

    @property
    def graph(self):
        """
        Devuelve el grafo del mapa.

        Devuelve:
        ---------
        networkx.MultiDiGraph
            El grafo del mapa.
        """
        return self._G


    @property
    def osm_file_name(self):
        """
        Devuelve el nombre del archivo OSM.

        Devuelve:
        ---------
        str
            El nombre del archivo OSM.
        """
        return self._osm_file_name

    @property
    def graphml_file_name(self):
        """
        Devuelve el nombre del archivo GraphML.

        Devuelve:
        ---------
        str
            El nombre del archivo GraphML.
        """
        return self._graphml_file_name
    
    def _map_place_name(self, place_name):
        """
        Crea un grafo del mapa a partir del nombre de un lugar.

        Parámetros:
        -----------
        place_name : str
            Nombre del lugar a partir del cual se creará el grafo del mapa.

        Devuelve:
        ---------
        networkx.MultiDiGraph
            El grafo del mapa.

        Lanza:
        ------
        Exception
            Si ocurre un error durante la creación del grafo.
        """
        try:
            return ox.graph_from_place(place_name, network_type='drive')
        except Exception as error:
            print("Map G creation error. Function _map_place_name") 
            raise error 

    def _map_coordinates(self, coordinates):
        """
        Crea un grafo del mapa a partir de coordenadas geográficas.

        Parámetros:
        -----------
        coordinates : tuple
            Tupla con las coordenadas (west, south, east, north) que delimitan el área del mapa.

        Devuelve:
        ---------
        networkx.MultiDiGraph
            El grafo del mapa.

        Lanza:
        ------
        Exception
            Si ocurre un error durante la creación del grafo.
        """
        try:
            west, south, east, north = coordinates
            return ox.graph_from_bbox(
                north, south, east, west, network_type="drive"
            )
        except Exception as error: 
            print("Map G creation error. Function _map_coordinates")
            raise error

    def _map_ox_graphml(self, path):
        """
        Carga un grafo del mapa a partir de un archivo GraphML.

        Parámetros:
        -----------
        path : str
            Ruta del archivo GraphML.

        Devuelve:
        ---------
        networkx.MultiDiGraph
            El grafo del mapa.

        Lanza:
        ------
        Exception
            Si ocurre un error durante la carga del grafo.
        """
        try:
            return ox.io.load_graphml(path)
        except Exception as error: 
            print("Map G creation error. Function _map_ox_graphml") 
            raise error