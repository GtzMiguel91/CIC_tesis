import copy
import multiprocessing as mp
from queue import PriorityQueue
from algoritmos.distances import haversine_distance

class PrioritizedItem:
    def __init__(self, priority, data):
        self.priority = priority
        self.data = data
    
    def __lt__(self, other):
        return self.priority < other.priority

def _generar_combinaciones(vehicle_factory):
    sharing = vehicle_factory.veh_sharing
    sharing_not = vehicle_factory.veh_not_sharing
    G = vehicle_factory.G
    veh_combinations = []
    for veh_not in sharing_not:
       for veh_sh in sharing:
           veh_combinations.append((G, veh_not, veh_sh))
    return veh_combinations

def _calculate_min_distances(G, veh_not, veh_sh):
    veh_id_not = veh_not.get_attribute('id')
    ox_route =  veh_not.get_attribute('route').ox_route
    s = ox_route.orig
    s_data = G.nodes[s]
    lat_s = s_data['y']
    lon_s = s_data['x']
    
    t = ox_route.dest_sharing
    t_data = G.nodes[t]
    lat_t = t_data['y']
    lon_t = t_data['x']
    
    final_shortest_path = []
    s_all_shortest_path = []
    t_all_shortest_path = []
    
    veh_att = veh_sh.get_attribute('route')
    veh_id_sh = veh_sh.get_attribute('id')
    v_route_ox = veh_att.ox_route.route    
    for node in v_route_ox:
        node_data = G.nodes[node]
        lat_veh = node_data['y']
        lon_veh = node_data['x']
        dist_s = haversine_distance(lat_s, lon_s, lat_veh, lon_veh)
        dist_t = haversine_distance(lat_t, lon_t, lat_veh, lon_veh)
        if dist_s is not None:
            s_all_shortest_path.append((dist_s, node))
        if dist_t is not None:
            t_all_shortest_path.append((dist_t, node))
    min_s_path = min(s_all_shortest_path, key=lambda x: x[0])
    min_t_path = min(t_all_shortest_path, key=lambda x: x[0])
    user_distance_walk = min_s_path[0]+min_t_path[0]+ veh_not.user_dist_walk
    aux = (user_distance_walk,(s, t), (min_s_path[1], min_t_path[1]), (veh_not, veh_sh), (veh_id_not, veh_id_sh))              
    return aux

def _ordenar_rutas(min_paths, vehicle_factory):
    q=PriorityQueue()  #Crear cola de prioridades

    dict_distances = {}
    veh_not_sharing = vehicle_factory.veh_not_sharing
    l_v_sharing = len(veh_not_sharing)
    idx_dictionary_sharing = {}
    dict_distances = {}
    
    for idx, v in enumerate(veh_not_sharing):
        idx_dictionary_sharing[v.get_attribute('id')] = idx
    
    for min_path in min_paths:
        item = PrioritizedItem(priority=min_path[0], data=min_path)
        q.put(item)
        id_sh = min_path[-1][1]
        if not(id_sh in dict_distances):
            dict_distances[id_sh] = [-1]*l_v_sharing
        
        id_not = min_path[-1][0]
        index = idx_dictionary_sharing[id_not]
        dict_distances[id_sh][index] = min_path[0]
    return q, dict_distances                      


def all_people_distances(veh_factory):
    vehicle_factory = copy.deepcopy(veh_factory)
    combinations = _generar_combinaciones(vehicle_factory)
    cpus = mp.cpu_count()/2
    cpus = print("Ejecutando distancias con cpus:", cpus)
    print("El numero de combinaciones es: ", len(combinations))
    with mp.get_context("spawn").Pool(cpus) as pool:
        min_paths = pool.starmap_async(_calculate_min_distances, combinations).get()
    q, dict_distances = _ordenar_rutas(min_paths, vehicle_factory)
        
    return q, dict_distances