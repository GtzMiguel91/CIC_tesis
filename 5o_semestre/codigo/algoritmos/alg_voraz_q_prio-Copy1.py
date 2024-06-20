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

def _generar_combinaciones(vehicle_factory_v2):
    sharing = vehicle_factory_v2.veh_sharing
    sharing_not = vehicle_factory_v2.veh_not_sharing
    G = vehicle_factory_v2.G
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

def _ordenar_rutas(min_paths):
    q=PriorityQueue()  #Crear cola de prioridades
    for min_path in min_paths:
        item = PrioritizedItem(priority=min_path[0], data=min_path)
        q.put(item)
    return q

def _procesar_rutas(vehicle_factory_v2, q):
    flag = True
    v_not_sharing = vehicle_factory_v2.veh_not_sharing
    v_sharing = vehicle_factory_v2.veh_sharing
    l_v_not_sharing = len(v_not_sharing)
    l_v_sharing = len(v_sharing)
    v_sharing_aux = []
    v_not_aux = []
    total_people_walk = 0
    vehicles_final = []
    while flag:
        l_sharing_aux = len(v_sharing_aux)
        l_v_not_aux = len(v_not_aux)
        if l_v_sharing != l_sharing_aux and l_v_not_sharing != l_v_not_aux:
            data = q.get()
            item = data.data
            id_not = item[-1][0]
            id_sh = item[-1][1]
            v_not = vehicle_factory_v2.get_vehicle_by_id(id_not)
            v_sh = vehicle_factory_v2.get_vehicle_by_id(id_sh)
            
            v_current_capa = v_sh.get_attribute("personNumber")
            v_att = v_sh.get_attribute("type")
            v_capacity = v_att.get_attribute("personCapacity")
            
            if v_current_capa != v_capacity: #aqui esta mal
                if not(v_not in v_not_aux):
                    veh_person_cap = v_sh.get_attribute('personNumber')
                    v_sh.set_attribute('personNumber', veh_person_cap + 1)
                    
                    v_not.user_dist_walk = item[0]
                    total_people_walk += v_not.user_dist_walk 
                    v_sh.vehicles_sharing= v_not
                    v_not_aux.append(v_not)
                    vehicles_final.append(item)
                # else:
                #     print(v_not)
                #     ids = [veh.get_attribute("id") for veh in v_not_aux]
                #     print(ids)
                #     print(id_not)
            else:
                if not(v_sh in v_sharing_aux):
                    v_sharing_aux.append(v_sh)
        else:
            # print(len(v_sharing_aux))
            # print(len(v_not_aux))
            flag = False
    
    #checar si existen personas sin vehiculo
    if l_v_not_sharing>len(v_not_aux):
        for v in v_not_sharing:
            if not(v in v_not_aux):
                vehicle_factory_v2.veh_not_get = v
                l_path = v.get_attribute('route').ox_route.path_len
                total_people_walk += l_path
                
    return total_people_walk, vehicles_final

def algoritmo_voraz_q_prioridades(veh_factory):
    vehicle_factory_v2 = copy.deepcopy(veh_factory)
    combinations = _generar_combinaciones(vehicle_factory_v2)
    cpus = mp.cpu_count()/2
    cpus = print("Ejecutando distancias con cpus:", cpus)
    print("El numero de combinaciones es: ", len(combinations))
    with mp.get_context("spawn").Pool(cpus) as pool:
        min_paths = pool.starmap_async(_calculate_min_distances, combinations).get()

    print("Ejecutando cola de prioridades")
    q = _ordenar_rutas(min_paths)
    print("Obteniendo distancia total")
    total_people_walk, vehicles_final = _procesar_rutas(vehicle_factory_v2, q)
    return vehicle_factory_v2, total_people_walk, vehicles_final