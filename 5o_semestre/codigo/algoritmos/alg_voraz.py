import copy
import random

def algoritmo_voraz(veh_factory, dict_distances):
    vehicle_factory_v1 = copy.deepcopy(veh_factory)
    sharing = vehicle_factory_v1.veh_sharing
    sharing_not = vehicle_factory_v1.veh_not_sharing
    random.shuffle(sharing_not)
    final_vehicles = []
    total_people_walk = 0
    for idx, veh_not in enumerate(sharing_not):
        veh_id_not = veh_not.get_attribute('id')        
        final_shortest_path = []
        for veh_sh in sharing:
            veh_id_sh = veh_sh.get_attribute('id')
            veh_current_capacity = veh_sh.get_attribute("personNumber")
            
            veh_att = veh_sh.get_attribute("type")
            veh_capacity = veh_att.get_attribute("personCapacity")
            # s_all_shortest_path = []
            # t_all_shortest_path = []
            if veh_current_capacity != veh_capacity: #check vehicle max capacity
                user_distance_walk = dict_distances[veh_id_sh][idx]
                aux = (user_distance_walk,(veh_not, veh_sh), (veh_id_not, veh_id_sh)) #usuario, carro 
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
        
    return vehicle_factory_v1, total_people_walk, final_vehicles