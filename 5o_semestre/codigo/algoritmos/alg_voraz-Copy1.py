import copy
import random
from algoritmos.distances import haversine_distance

def algoritmo_voraz(veh_factory):
    vehicle_factory_v1 = copy.deepcopy(veh_factory)
    sharing = vehicle_factory_v1.veh_sharing
    sharing_not = vehicle_factory_v1.veh_not_sharing
    G = vehicle_factory_v1.G
    random.shuffle(sharing_not)
    final_vehicles = []
    total_people_walk = 0
    for veh_not in sharing_not:
        ox_route =  veh_not.get_attribute('route').ox_route
        veh_id_not = veh_not.get_attribute('id')
        s = ox_route.orig
        s_data = G.nodes[s]
        lat_s = s_data['y']
        lon_s = s_data['x']
        
        t = ox_route.dest_sharing
        t_data = G.nodes[t]
        lat_t = t_data['y']
        lon_t = t_data['x']
        
        final_shortest_path = []
        for veh_sh in sharing:
            veh_att = veh_sh.get_attribute('route')
            veh_id_sh = veh_sh.get_attribute('id')
            v_route_ox = veh_att.ox_route.route
            veh_current_capacity = veh_sh.get_attribute("personNumber")
            
            veh_att = veh_sh.get_attribute("type")
            veh_capacity = veh_att.get_attribute("personCapacity")
            s_all_shortest_path = []
            t_all_shortest_path = []
            if veh_current_capacity != veh_capacity: #check vehicle max capacity
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
                aux = (user_distance_walk,(s, t), (min_s_path[1], min_t_path[1]), (veh_not, veh_sh), (veh_id_not, veh_id_sh)) #usuario, carro 
                final_shortest_path.append(aux)
        if final_shortest_path:
            min_final = min(final_shortest_path, key=lambda x: x[0])
            final_vehicles.append(min_final)
            veh_sh_x = min_final[-2][1]            
            veh_person_cap = veh_sh_x.get_attribute('personNumber')
            veh_sh_x.set_attribute('personNumber', veh_person_cap+1)
            v_not = min_final[-2][0]
            v_not.user_dist_walk = min_final[0]
            total_people_walk += v_not.user_dist_walk 
            veh_sh_x.vehicles_sharing= v_not
        else:
            vehicle_factory_v1.veh_not_get = veh_not
            l_path = veh_not.get_attribute('route').ox_route.path_len
            total_people_walk += l_path
            
    # v_not_get = vehicle_factory_v1.veh_not_get
    # if v_not_get:
    #     for v in v_not_get:
    #         l_path = v.get_attribute('route').ox_route.path_len
    #         total_people_walk += l_path
        
    return vehicle_factory_v1, total_people_walk, final_vehicles