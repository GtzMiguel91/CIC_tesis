#!/usr/bin/env python
# coding: utf-8

# In[16]:


from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
import bisect
from routes.routes import RouteSumo, RouteOx

class RoutesFactory(ABC):
    """
    An abstract base class for creating routes.

    Attributes:
        _routes (list): The list of created routes.

    Methods:
        create_routes(Map):
            Creates routes on the given map.
    """

    def __init__(self):
        self._routes = []

    @abstractmethod
    def create_routes(self):
        """
        Creates routes on the given map.

        Args:
            Map: The map on which to create the routes.
        """
        pass

    @property
    def routes(self):
        """
        Returns the list of created routes.

        Returns:
            list: The list of created routes.
        """
        return self._routes

    def get_routes_length(self):
        """
        Returns the number of routes in the routes list.

        Returns:
            int: The number of routes in the routes list.
        """
        return len(self._routes)


# In[21]:


class RoutesFactoryOx(RoutesFactory):
    """
    A class for creating routes using OpenStreetMap data.

    Attributes:
        n_rutas (int): The number of routes to create.
        destinations (list): The list of possible destinations.
        seed (int): The random seed to use.

    Methods:
        _sample_points(G):
            Samples points on the given graph.
        _get_destinations_coordinates(_G):
            Returns the coordinates of the destinations.
        create_routes(Map):
            Creates routes on the given map.
    """

    def __init__(self, n_rutas, destinations, min_nodes_route, seed):
        """
        Initializes a new RoutesFactoryOx object.

        Args:
            n_rutas (int): The number of routes to create.
            destinations (list): The list of possible destinations.
            seed (int): The random seed to use.
        """
        super().__init__()
        self._min_nodes_route = min_nodes_route
        self.seed = seed
        np.random.seed(seed)
        self.n_rutas = n_rutas
        self.destinations = destinations
        self._G = None

    def _sample_points(self, G):
        """
        Samples points on the given graph.

        Args:
            G: The graph on which to sample points.

        Returns:
            Series: The sampled points.
        """
        n = self.n_rutas
        if nx.is_directed(G):
            warnings.warn(
                "graph should be undirected to not oversample bidirectional edges"
            )

        gdf_edges = ox.utils_graph.graph_to_gdfs(G, nodes=False)[["geometry", "length"]]
        weights = gdf_edges["length"] / gdf_edges["length"].sum()
        idx = np.random.choice(gdf_edges.index, size=n, p=weights)
        lines = gdf_edges.loc[idx, "geometry"]
        return lines.interpolate(np.random.rand(n), normalized=True)

    def _get_destinations_coordinates(self, _G):
        """
        Returns the coordinates of the destinations.

        Args:
            _G: The graph on which to get the destinations.

        Returns:
            list: The coordinates of the destinations.
        """
        G = _G
        # Re-proyectar el grafo a un CRS proyectado
        G2 = ox.projection.project_graph(G)
        G3 = ox.utils_graph.get_undirected(G2)

        points = self._sample_points(G3)

        # Convertir a coordenadas
        points_to_sg = ox.projection.project_gdf(points, to_latlong=True)
        points_frame = points_to_sg.to_frame()
        points_frame = points_frame.reset_index()
        points_coordinates = [(point.x, point.y) for point in points_frame[0]]
        return points_coordinates

    def create_routes(self, Map):
        """
        Creates routes on the given map.

        Args:
            Map: The map on which to create the routes.
        """
        self._G = Map
        _G = self._G
        points_coordinates = self._get_destinations_coordinates(_G)
        dest = self.destinations
        # Obtener rutas origen-destino
        for point in points_coordinates:
            dest_aleatorio = np.random.choice(len(dest))
            dest_name = dest[dest_aleatorio][0]
            dest_coord = dest[dest_aleatorio][1]
            
            route = RouteOx(dest_name, point, dest_coord)
            route.create_route(_G)
            ids_route = route.route
            if not (ids_route) is None:
                ids_route_len = len(ids_route)
                if ids_route_len > self._min_nodes_route:
                    self._routes.append(route)
                    total_length = 0
                    for i in range(ids_route_len-1):
                        edge_weight = _G[ids_route[i]][ids_route[i+1]][0]['length']
                        total_length += edge_weight
                    route.path_len = total_length

    def dist_nodes(self, source, target):
        return nx.shortest_path_length(self._G, source, target, weight="distance")
        
# In[20]:


class RoutesFactorySumo(RoutesFactory):
    """
    A class for creating routes using SUMO data.

    Methods:
        create_routes(file_net, ox_routes):
            Creates routes on the given SUMO network.
    """

    def __init__(self):
        """
        Initializes a new RoutesFactorySumo object.
        """
        super().__init__()
        # self._routes_sort = []
        # self._dict_routes = {}
    
    # def _find_position(self, sorted_list, tuple_to_insert):
    #     # Extract the distances for comparison
    #     distances = [x[0] for x in sorted_list]
        
    #     # Use bisect to find the insertion point based on the first element of the tuple
    #     return bisect.bisect_left(distances, tuple_to_insert[0])
    
    def create_routes(self, file_net, ox_routes):
        """
        Creates routes on the given SUMO network.

        Args:
            file_net: The SUMO network file.
            ox_routes: The osmnx routes.
        """
        import sumolib.net as snet

        netReader = snet.readNet(file_net)
        nodes_dict = netReader.getNodesDict()
        df = pd.DataFrame(list(nodes_dict.items()), columns=["key", "value"])

        for ox_route in ox_routes:
            route = ox_route.route
            route_sumo = RouteSumo()
            route_sumo.create_route(df, route, netReader)
            route_sumo_f = route_sumo._route
            temp = ()
            if route_sumo_f:
                route_sumo.ox_route = ox_route
                self._routes.append(route_sumo)
                # self._dict_routes[ox_route.id] = route_sumo
                ## Los que esta en comentarios es para ordentar rutas en caso de que se necesite.
                # try:
                #     print('try en rutas', self._routes)
                
                #     temp = (ox_route._path_len, route_sumo)
                #     position = self._find_position(self._routes_sort, temp)
                #     self._routes_sort.insert(position, temp)
                    
                # except Exception as e:
                #     print('exception rutas',self._routes)
                #     print('temp exception',temp)
                #     print(e)
                #     return
        
    # @property
    # def routes_ox_sort(self):
    #     return self._routes_ox_sort