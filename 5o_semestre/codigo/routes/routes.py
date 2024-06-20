import osmnx as ox
import uuid
import random
from abc import ABC, abstractmethod

class Route(ABC):
    """
    Clase abstracta que define la estructura básica de una ruta.

    Atributos:
    ----------
    _route : list
        Lista que almacena los nodos de la ruta.
    """
    def __init__(self):
        """
        Inicializa una instancia de Route.
        """
        self._route = []

    @abstractmethod
    def create_route(self):
        """
        Método abstracto para crear una ruta.
        """
        pass

    @property
    def route(self):
        """
        Devuelve la lista de nodos de la ruta.

        Devuelve:
        ---------
        list
            Lista de nodos de la ruta.
        """
        return self._route

class RouteOx(Route):
    """
    Clase que representa una ruta utilizando OpenStreetMap (osmnx).

    Atributos:
    ----------
    _id : int
        Identificador único de la ruta.
    _dest_name : str
        Nombre del destino.
    _dest_sharing : int
        Nodo de destino compartido.
    _dest_sharing_dist : float
        Distancia a pie desde el destino compartido hasta el nodo más cercano.
    _init_orig : tuple
        Coordenadas de origen.
    _path_len : float
        Longitud del camino.
    _orig : int
        Nodo de origen.
    _dest : int
        Nodo de destino.
    _orig_dist : float
        Distancia a pie desde el origen hasta el nodo más cercano.
    """

    def __init__(self, init_orig):
        """
        Inicializa una instancia de RouteOx.

        Parámetros:
        -----------
        init_orig : tuple
            Coordenadas de origen.
        """
        super().__init__()
        self._id = uuid.uuid4().int
        self._dest_name = None
        self._dest_sharing = None #nodo de destino compartido (metro)
        self._dest_sharing_dist = None #distance to walk from dest_sharing to nearest node
        self._init_orig = init_orig #coordinates
        self._path_len = None
        self._orig = None # node id
        self._dest = None # node id
        self._orig_dist = None #distance to walk from orig to nearest node
    
    def create_route(self, G):
        """
        Crea una ruta en el grafo proporcionado.

        Parámetros:
        -----------
        G : networkx.MultiDiGraph
            Grafo del mapa de la clase Map.
        """
        nodes = list(G.nodes)
        flag = True
        
        long = self._init_orig[0]
        lat = self._init_orig[1]
        self._orig, self._orig_dist = ox.distance.nearest_nodes(
            G, X=long, Y=lat, return_dist=True
        )
        
        while flag:
            random_node = random.choice(nodes)
            if self._orig != random_node:
                self._dest = random_node
                flag = False
        
        self._route = ox.shortest_path(G, self._orig, self._dest, weight="length")
    
    @property
    def path_len(self):
        """
        Devuelve la longitud del camino.

        Devuelve:
        ---------
        float
            Longitud del camino.
        """
        return self._path_len

    @path_len.setter
    def path_len(self, path_len):
        """
        Establece la longitud del camino.

        Parámetros:
        -----------
        path_len : float
            Longitud del camino.
        """
        self._path_len = path_len

    @property
    def id(self):
        """
        Devuelve el identificador único de la ruta.

        Devuelve:
        ---------
        int
            Identificador único de la ruta.
        """
        return self._id
        
    @property
    def orig(self):
        """
        Devuelve el nodo de origen.

        Devuelve:
        ---------
        int
            Nodo de origen.
        """
        return self._orig 
    
    @property
    def dest(self):
        """
        Devuelve el nodo de destino.

        Devuelve:
        ---------
        int
            Nodo de destino.
        """
        return self._dest
        
    @property
    def orig_dist(self):
        """
        Devuelve la distancia a pie desde el origen hasta el nodo más cercano.

        Devuelve:
        ---------
        float
            Distancia a pie desde el origen hasta el nodo más cercano.
        """
        return self._orig_dist

    @property
    def dest_dist(self):
        """
        Devuelve la distancia a pie desde el destino hasta el nodo más cercano.

        Devuelve:
        ---------
        float
            Distancia a pie desde el destino hasta el nodo más cercano.
        """
        return self._dest_dist

    @property
    def dest_name(self):
        """
        Devuelve el nombre del destino.

        Devuelve:
        ---------
        str
            Nombre del destino.
        """
        return self._dest_name

    @dest_name.setter
    def dest_name(self, dest_name):
        """
        Establece el nombre del destino.

        Parámetros:
        -----------
        dest_name : str
            Nombre del destino.
        """
        self._dest_name = dest_name
    
    @property
    def dest_sharing(self):
        """
        Devuelve el nodo de destino compartido.

        Devuelve:
        ---------
        int
            Nodo de destino compartido.
        """
        return self._dest_sharing

    @dest_sharing.setter
    def dest_sharing(self, dest_sharing):
        """
        Establece el nodo de destino compartido.

        Parámetros:
        -----------
        dest_sharing : int
            Nodo de destino compartido.
        """
        self._dest_sharing = dest_sharing

    @property
    def dest_sharing_dist(self):
        """
        Devuelve la distancia a pie desde el destino compartido hasta el nodo más cercano.

        Devuelve:
        ---------
        float
            Distancia a pie desde el destino compartido hasta el nodo más cercano.
        """
        return self._dest_sharing_dist

    @dest_sharing_dist.setter
    def dest_sharing_dist(self, dest_sharing_dist):
        """
        Establece la distancia a pie desde el destino compartido hasta el nodo más cercano.

        Parámetros:
        -----------
        dest_sharing_dist : float
            Distancia a pie desde el destino compartido hasta el nodo más cercano.
        """
        self._dest_sharing_dist = dest_sharing_dist


class RouteSumo(Route):
    """
    Clase que representa una ruta utilizando SUMO.

    Atributos:
    ----------
    _id : int
        Identificador único de la ruta.
    _ox_route : RouteOx
        Ruta de OpenStreetMap asociada.
    """
    
    def __init__(self):
        """
        Inicializa una instancia de RouteSumo.
        """
        super().__init__()
        self._id = uuid.uuid4().int
        self._ox_route = None

    def __eq__(self, other):
        """
        Compara si dos rutas SUMO son iguales basándose en su identificador.

        Parámetros:
        -----------
        other : RouteSumo
            Otra instancia de RouteSumo.

        Devuelve:
        ---------
        bool
            True si las rutas son iguales, False en caso contrario.
        """
        if isinstance(other, RouteSumo):
            return self._id == other.id
        return False
    
    def create_route(self, df, ox_route, netReader):
        """
        Crea una ruta en SUMO utilizando una ruta de OpenStreetMap.

        Parámetros:
        -----------
        df : pandas.DataFrame
            DataFrame con información de los nodos.
        ox_route : RouteOx
            Ruta de OpenStreetMap.
        netReader : sumolib.net.Net
            Lector de red de SUMO.
        """
        node_from = node_to = None
        node_dfrom = node_dto = None
        node_from, node_to = self._get_nodes_to_from(df, ox_route)
        if node_from:
            node_dfrom, node_dto = self._get_nodes_to_from(df, ox_route, positive=False)

        edge_from = edge_to = None
        if node_dfrom:
            edge_from = self._convert_nodes_to_sumo_edge(node_from, node_to, netReader)
            edge_to = self._convert_nodes_to_sumo_edge(node_dfrom, node_dto, netReader)

        if edge_from and edge_to:
            optPath = netReader.getOptimalPath(edge_from, edge_to)
            for edge in optPath[0]:
                self._route.append(edge.getID())

    def _get_nodes_to_from(self, df, ox_route, positive=True):
        """
        Obtiene los nodos de origen y destino desde el DataFrame.

        Parámetros:
        -----------
        df : pandas.DataFrame
            DataFrame con información de los nodos.
        ox_route : RouteOx
            Ruta de OpenStreetMap.
        positive : bool, opcional
            Indica si se deben buscar los nodos en orden positivo. Por defecto es True.

        Devuelve:
        ---------
        tuple
            Tupla con los nodos de origen y destino.
        """
        idx = 0 if positive else -1
        idx_next = idx + 1 if positive else idx - 1
        node_from = node_to = None
        while True:
            if positive:
                filtered_df = df[df["key"].str.contains(str(ox_route[idx]))]
                filtered_df1 = df[df["key"].str.contains(str(ox_route[idx_next]))]
            else:
                filtered_df = df[df["key"].str.contains(str(ox_route[idx_next]))]
                filtered_df1 = df[df["key"].str.contains(str(ox_route[idx]))]

            if not filtered_df.empty and not filtered_df1.empty:
                if not filtered_df["key"].equals(filtered_df1["key"]):
                    df_key = filtered_df.loc[:, "value"]
                    node_from = df_key.tolist()[0]
                    df1_key = filtered_df1.loc[:, "value"]
                    node_to = df1_key.tolist()[0]
                    return node_from, node_to
                else:
                    idx = idx + 1 if positive else idx - 1
                    idx_next = idx + 1 if positive else idx - 1
            else:
                return None, None

    def _convert_nodes_to_sumo_edge(self, node_from, node_to, netReader):
        """
        Convierte los nodos de OpenStreetMap a aristas de SUMO.

        Parámetros:
        -----------
        node_from : sumolib.net.Node
            Nodo de origen.
        node_to : sumolib.net.Node
            Nodo de destino.
        netReader : sumolib.net.Net
            Lector de red de SUMO.

        Devuelve:
        ---------
        sumolib.net.Edge
            Arista correspondiente en SUMO.
        """
        edges_from = node_from.getOutgoing()
        edges_to = node_to.getIncoming()
        edge = None
        edges_ids = []
        for edge_from in edges_from:
            edges_ids.append(edge_from.getID())
            if edge_from in edges_to:
                edge = edge_from

        if edge is None:
            for edge_to in edges_to:
                edges_ids.append(edge_to.getID())

            while True:
                for edge0 in edges_ids:
                    for edge1 in edges_ids:
                        if edge0 != edge1:
                            if edge0 in edge1:
                                edge = netReader.getEdge(edge0)
                                return edge
                            elif edge1 in edge0:
                                edge = netReader.getEdge(edge1)
                                return edge
                return edge
        return edge

    @property
    def ox_route(self):
        """
        Devuelve la ruta de OpenStreetMap asociada.

        Devuelve:
        ---------
        RouteOx
            Ruta de OpenStreetMap asociada.
        """
        return self._ox_route

    @ox_route.setter
    def ox_route(self, ox_route):
        """
        Establece la ruta de OpenStreetMap asociada.

        Parámetros:
        -----------
        ox_route : RouteOx
            Ruta de OpenStreetMap a asociar.
        """
        self._ox_route = ox_route

    @property
    def id(self):
        """
        Devuelve el identificador único de la ruta.

        Devuelve:
        ---------
        int
            Identificador único de la ruta.
        """
        return self._id
