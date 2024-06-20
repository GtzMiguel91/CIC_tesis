from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
import bisect
import random
import os
import sys
import subprocess

from routes.routes import RouteSumo, RouteOx

class RoutesFactory(ABC):
    """
    Clase abstracta para la creación de rutas.

    Atributos:
    ----------
    _routes : list
        Lista de rutas creadas.
    """
    def __init__(self):
        """
        Inicializa una instancia de la clase RoutesFactory.
        """
        self._routes = []

    @abstractmethod
    def create_routes(self):
        """
        Método abstracto para la creación de rutas.
        """
        pass

    @property
    def routes(self):
        """
        Devuelve la lista de rutas creadas.

        Devuelve:
        ---------
        list
            Lista de rutas creadas.
        """
        return self._routes

    def get_routes_length(self):
        """
        Devuelve la cantidad de rutas creadas.

        Devuelve:
        ---------
        int
            Cantidad de rutas creadas.
        """
        return len(self._routes)


class RoutesFactoryOx(RoutesFactory):
    """
    Clase para la creación de rutas utilizando un grafo de OpenStreetMap (osmnx).

    Atributos:
    ----------
    _min_nodes_route : int
        Número mínimo de nodos que debe tener una ruta.
    seed : int
        Semilla para la generación de números aleatorios.
    n_rutas : int
        Número de rutas a crear.
    _G : networkx.MultiDiGraph
        Grafo del mapa creado con la clase Map.
    """
    def __init__(self, G, n_rutas, min_nodes_route, seed):
        """
        Inicializa una instancia de la clase RoutesFactoryOx.

        Parámetros:
        -----------
        G : networkx.MultiDiGraph
            Grafo del mapa.
        n_rutas : int
            Número de rutas a crear.
        min_nodes_route : int
            Número mínimo de nodos que debe tener una ruta.
        seed : int
            Semilla para la generación de números aleatorios.
        """
        super().__init__()
        self._min_nodes_route = min_nodes_route
        self.seed = seed
        np.random.seed(seed)
        self.n_rutas = n_rutas
        self._G = G

    def _sample_points(self, G3):
        """
        Muestra puntos de un grafo no dirigido.

        Parámetros:
        -----------
        G3 : networkx.Graph
            Grafo no dirigido.

        Devuelve:
        ---------
        geopandas.GeoSeries
            Serie de puntos muestreados.
        """
        G = G3  # El grafo ha sido procesado, no es el original
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

    def _get_destinations_coordinates(self):
        """
        Obtiene las coordenadas de los destinos a partir del grafo.

        Devuelve:
        ---------
        list
            Lista de coordenadas de los destinos.
        """
        G = self._G
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

    def create_routes(self):
        """
        Crea rutas origen-destino a partir de las coordenadas de los destinos.
        """
        _G = self._G
        points_coordinates = self._get_destinations_coordinates()
        # Obtener rutas origen-destino
        for point in points_coordinates:
            #dest_aleatorio = np.random.choice(len(dest))
            #init_orig, dest_node
            route = RouteOx(point)
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

    def update_destinations(self, destinos, vehicles):
        """
        Actualiza las coordenadas de los destinos y asigna destinos aleatorios a los vehículos.

        Parámetros:
        -----------
        destinos : list
            Lista de destinos con sus coordenadas.
        vehicles : list
            Lista de vehículos a los que se les asignarán destinos.
        
        Devuelve:
        ---------
        bool
            True si la operación fue exitosa.
        """
        nodes_dest = []
        G = self._G
        for destino in destinos:
            dest_name = destino[0]
            coordinates = destino[1]
            long_dest = coordinates[0]
            lat_dest = coordinates[1]
            try:
                node_sharing, node_distance = ox.distance.nearest_nodes(
                    G, X=long_dest, Y=lat_dest, return_dist=True
                )
                nodes_dest.append((dest_name, node_sharing, node_distance))
            except Exception as e:
                raise Exception(f"Se ha producido un error inesperado: {e}")
        for vehicle in vehicles:
            dest_ran = random.choice(nodes_dest)
            veh_ox = vehicle.get_attribute('route').ox_route
            veh_ox.dest_name = dest_ran[0]
            veh_ox.dest_sharing = dest_ran[1]
            veh_ox.dest_sharing_dist = dest_ran[2]
            vehicle.user_dist_walk = veh_ox.orig_dist + veh_ox.dest_sharing_dist
        return True
    
    def dist_nodes(self, source, target):
        """
        Calcula la distancia más corta entre dos nodos en el grafo.

        Parámetros:
        -----------
        source : int
            Nodo de origen.
        target : int
            Nodo de destino.

        Devuelve:
        ---------
        int
            Distancia más corta entre los nodos.
        """
        return nx.shortest_path_length(self._G, source, target, weight="distance")

    
    
class RoutesFactorySumo(RoutesFactory):
    """
    Clase para la creación de rutas utilizando SUMO.

    Métodos:
    --------
    create_routes(file_net, ox_routes)
        Crea rutas a partir de un archivo de red de SUMO y rutas de osmnx.
    """
    
    def __init__(self):
        """
        Inicializa una instancia de la clase RoutesFactorySumo.
        """
        super().__init__()
        
    
    def create_routes(self, file_net, ox_routes):
        """
        Crea rutas a partir de un archivo de red de SUMO y rutas de osmnx.

        Parámetros:
        -----------
        file_net : str
            Ruta del archivo de red de SUMO.
        ox_routes : list
            Lista de rutas de osmnx.
        """
        import sumolib.net as snet
        
        netReader = snet.readNet(file_net)
        nodes_dict = netReader.getNodesDict()
        df = pd.DataFrame(list(nodes_dict.items()), columns=["key", "value"])
        
        for ox_route in ox_routes:
            try:
                route = ox_route.route
                route_sumo = RouteSumo()
                route_sumo.create_route(df, route, netReader)
                route_sumo_f = route_sumo._route
                temp = ()
                if route_sumo_f:
                    route_sumo.ox_route = ox_route
                    self._routes.append(route_sumo)
            except Exception as error:
                print("Log: Error en la creacion de la ruta sumo")
                