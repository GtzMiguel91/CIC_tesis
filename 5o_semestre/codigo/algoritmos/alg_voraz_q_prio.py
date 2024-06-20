import copy

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
            
            if v_current_capa != v_capacity:
                if not(v_not in v_not_aux):
                    veh_person_cap = v_sh.get_attribute('personNumber')
                    v_sh.set_attribute('personNumber', veh_person_cap + 1)
                    
                    v_not.user_dist_walk = item[0]
                    total_people_walk += v_not.user_dist_walk 
                    v_sh.vehicles_sharing= v_not
                    v_not_aux.append(v_not)
                    vehicles_final.append(item)
            else:
                if not(v_sh in v_sharing_aux):
                    v_sharing_aux.append(v_sh)
        else:
            flag = False
    
    #checar si existen personas sin vehiculo
    if l_v_not_sharing>len(v_not_aux):
        for v in v_not_sharing:
            if not(v in v_not_aux):
                vehicle_factory_v2.veh_not_get = v
                l_path = v.get_attribute('route').ox_route.path_len
                total_people_walk += l_path
                
    return total_people_walk, vehicles_final

def algoritmo_voraz_q_prioridades(veh_factory, q):
    vehicle_factory_v2 = copy.deepcopy(veh_factory)
    print("Obteniendo distancia total")
    total_people_walk, vehicles_final = _procesar_rutas(vehicle_factory_v2, q)
    return vehicle_factory_v2, total_people_walk, vehicles_final