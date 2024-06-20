#!/usr/bin/env python
# coding: utf-8

# In[1]:


import osmnx as ox
import uuid
import random
from abc import ABC, abstractmethod

class Route(ABC):
    """
    An abstract base class for creating routes.

    Attributes:
        _route (list): The list of edges representing the route.

    Methods:
        create_route(G):
            Creates a route on the given graph.
    """

    def __init__(self):
        self._route = []

    @abstractmethod
    def create_route(self):
        """
        Creates a route on the given graph.

        Args:
            G: The graph on which to create the route.
        """
        pass

    @property
    def route(self):
        """
        Returns the list of edges representing the route.

        Returns:
            list: The list of edges representing the route.
        """
        return self._route


# In[3]:


class RouteOx(Route):
    """
    A class for creating routes using OpenStreetMap data.

    Attributes:
        dest_name (str): The name of the destination.
        init_orig (tuple): The initial origin coordinates.
        init_dest (tuple): The initial destination coordinates.
        orig (int): The nearest node to the initial origin coordinates.
        dest (int): The nearest node to the initial destination coordinates.
        orig_dist (float): The distance from the initial origin coordinates to the nearest node.
        dest_dist (float): The distance from the initial destination coordinates to the nearest node.

    Methods:
        create_route(G):
            Creates a route on the given graph.
    """

    def __init__(self, dest_name, init_orig, init_dest):
        """
        Initializes a new RouteOx object.

        Args:
            dest_name (str): The name of the destination.
            init_orig (tuple): The initial origin coordinates.
            init_dest (tuple): The initial destination coordinates.
        """
        super().__init__()
        self._id = uuid.uuid4().int
        self._dest_name = dest_name
        self._init_orig = init_orig #coordinates
        self._init_dest = init_dest #coordinates
        self._path_len = None
        self._orig = None # node id
        self._dest = None # node id
        self._orig_dist = None #distance to walk from orig to nearest node
        self._dest_dist = None #distance to walk from dests to nearest node
    
    def create_route(self, G):
        """
        Creates a route on the given graph.

        Args:
            G: The graph on which to create the route.
        """
        long = self._init_orig[0]
        lat = self._init_orig[1]
        long_dest = self._init_dest[0]
        lat_dest = self._init_dest[1]
        self._orig, self._orig_dist = ox.distance.nearest_nodes(
            G, X=long, Y=lat, return_dist=True
        )
        self._dest, self._dest_dist = ox.distance.nearest_nodes(
            G, X=long_dest, Y=lat_dest, return_dist=True
        )
        self._route = ox.shortest_path(G, self._orig, self._dest, weight="length")

    @property
    def path_len(self):
        return self._path_len

    @path_len.setter
    def path_len(self, path_len):
        self._path_len = path_len

    @property
    def id(self):
        return self._id

    @property
    def orig_dist(self):
        return self._orig_dist

    @property
    def dest_dist(self):
        return self._dest_dist

class RouteSumo(Route):
    """
    A class for creating routes using SUMO data.

    Methods:
        create_route(df, ox_route, netReader):
            Creates a route on the given SUMO network.

        _get_nodes_to_from(df, ox_route, positive=True):
            Returns the nodes corresponding to the given edges.

        _convert_nodes_to_sumo_edge(node_from, node_to, netReader):
            Converts the given nodes to a SUMO edge.
    """

    def __init__(self):
        """
        Initializes a new RouteSumo object.
        """
        super().__init__()
        self._id = uuid.uuid4().int
        self._ox_route = None

    def __eq__(self, other):
        if isinstance(other, RouteSumo):
            return self._id == other.id
        return False
    
    def create_route(self, df, ox_route, netReader):
        """
        Creates a route on the given SUMO network.

        Args:
            df: The SUMO network data.
            ox_route: The Osmnx route.
            netReader: The SUMO network reader.
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
        Returns the nodes corresponding to the given edges.

        Args:
            df: The SUMO network data.
            ox_route: The Osmnx route.
            positive (bool): Whether to search for nodes in the positive or negative direction.

        Returns:
            tuple: The nodes corresponding to the given edges.
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
        Converts the given nodes to a SUMO edge.

        Args:
            node_from: The starting node.
            node_to: The ending node.
            netReader: The SUMO network reader.

        Returns:
            Edge: The SUMO edge corresponding to the given nodes.
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
        Returns the Osmnx route.

        Returns:
            list: The Osmnx route.
        """
        return self._ox_route

    @ox_route.setter
    def ox_route(self, ox_route):
        """
        Sets the Osmnx route.

        Args:
            value (list): The new Osmnx route.
        """
        self._ox_route = ox_route

    @property
    def id(self):
        return self._id
