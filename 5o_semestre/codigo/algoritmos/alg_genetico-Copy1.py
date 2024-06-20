import copy
import random
import numpy as np
from algoritmos.distances import haversine_distance

def _generar_grupo_inicial(veh_sharing, veh_not_sharing):
    veh_not_sharing_indexes = []
    veh_sharing_indexes = []
    l_veh_not_sharing = len(veh_not_sharing)
    for idx, veh_sh in enumerate(veh_sharing):
        veh_att = veh_sh.get_attribute("type")
        veh_capacity = veh_att.get_attribute("personCapacity") - 1
        veh_not_sharing_indexes += [idx]*veh_capacity
        
        
    l_veh_not_indexes = len(veh_not_sharing_indexes)
    l_total = l_veh_not_sharing - l_veh_not_indexes
    if l_total > 0:
        veh_not_sharing_indexes += [-1]*l_total
    # print(veh_not_sharing_indexes)
    # print(len(veh_not_sharing_indexes))
    # print(distances_dict)
    return veh_not_sharing_indexes

def _generar_poblacion(veh_sharing, veh_not_sharing, sizeP):
    population = []
    veh_not_sh_idx = _generar_grupo_inicial(veh_sharing, veh_not_sharing)
    for _ in range(sizeP):
        copied_list = veh_not_sh_idx[:]
        random.shuffle(copied_list)
        if copied_list not in population:
            population.append(copied_list)
    return population

def _ruleta_ponderada(poblacion, fitness_poblacion, n_padres=2):
    total_fitness = sum(fitness_poblacion)
    probabilidades = [f / total_fitness for f in fitness_poblacion]
    padres = random.choices(poblacion, weights=probabilidades, k=n_padres)
    return padres
    
def _ruleta_simple(poblacion, n_padres=2):
    padres = random.sample(poblacion, n_padres)
    return padres

def _seleccion_padres(poblacion, fitness_poblacion, n_padres=2, estrategia='mixta'):
    if estrategia == 'simple':
        return _ruleta_simple(poblacion, n_padres)
    elif estrategia == 'ponderada':
        return _ruleta_ponderada(poblacion, fitness_poblacion, n_padres)
    elif estrategia == 'mixta':
        if random.random() < 0.7:
            return _ruleta_ponderada(poblacion, fitness_poblacion, n_padres)
        else:
            return _ruleta_simple(poblacion, n_padres)

def _contar_elementos(lista):
    return {x: lista.count(x) for x in lista}

def _cruza_orden_mantener_cantidades(padre1, padre2):
    tamaño = len(padre1)
    
    # Seleccionar dos puntos de cruza al azar
    punto1, punto2 = sorted(random.sample(range(tamaño), 2))
    
    # Inicializar hijos con None
    hijo1 = [None] * tamaño
    hijo2 = [None] * tamaño
    
    # Copiar el segmento entre los puntos de cruza
    hijo1[punto1:punto2] = padre1[punto1:punto2]
    hijo2[punto1:punto2] = padre2[punto1:punto2]
    
    # Contar elementos para rellenar los espacios restantes
    cuenta_p1 = _contar_elementos(padre1)
    cuenta_p2 = _contar_elementos(padre2)
    # Actualizar las cuentas basadas en los segmentos ya copiados
    for i in range(punto1, punto2):
        cuenta_p1[hijo1[i]] -= 1
        cuenta_p2[hijo2[i]] -= 1

    def rellenar_espacios_restantes(hijo, otro_padre, cuenta_dic):
        pos_actual = 0
        
        for elem in otro_padre:
            # print('elem', elem)
            flag = True
            while flag:
                if pos_actual != len(hijo):
                    if hijo[pos_actual] is not None:
                        pos_actual += 1
                        flag = True
                    else:
                        flag = False
                else:
                    flag = False
                    # print('cuenta_dic', cuenta_dic)
                    # print('pos_actual', pos_actual)
            if cuenta_dic[elem] > 0:
                hijo[pos_actual] = elem
                cuenta_dic[elem] -= 1
    
    # Rellenar los espacios restantes manteniendo la frecuencia
    rellenar_espacios_restantes(hijo1, padre2, cuenta_p1)
    rellenar_espacios_restantes(hijo2, padre1, cuenta_p2)
    
    return hijo1, hijo2

def _mutacion(hijo1, hijo2, p_m):
    hijos = [hijo1, hijo2]
    hijos_nuevos = []
    for hijo in hijos:
        hijo_nuevo = hijo[:]
        idx1, idx2 = random.sample(range(len(hijo_nuevo)), 2)
        r = random.random()
        if r < p_m :
            hijo_nuevo[idx1], hijo_nuevo[idx2] = hijo_nuevo[idx2], hijo_nuevo[idx1]
        hijos_nuevos.append(hijo_nuevo)
    return hijos_nuevos[0], hijos_nuevos[1]

def _reemplazo_generacional(poblacion, fitness_poblacion, hijos, fitness_hijos):
    n_poblacion = len(poblacion)
    
    poblacion_total = np.array(poblacion + hijos)
    fitness_total = np.array(fitness_poblacion + fitness_hijos)
    mejores = np.argsort(fitness_total) # multiplicando por -1 ordena de mayor a menor
    p_indices = mejores[0:n_poblacion]    
    nueva_poblacion = poblacion_total[p_indices].tolist()
    
    return nueva_poblacion

def _fitness(G, cromosoma, veh_sharing, veh_not_sharing, distances_dict):
    total_people_walk = 0
    l_veh_not_sharing = len(veh_not_sharing)
    new_cromosoma = cromosoma[0:l_veh_not_sharing]
    
    for idx, gen in enumerate(new_cromosoma): #idx seria vehicle_not_sharing y gen vehicle_sharing
        #print('idx, gen', idx, ',',gen)
        if gen != -1: #significa q no existen suficientes vehiculos a compartir y estos usuarios tendrian q ir en su vehiculo.
            dict_distance = distances_dict[gen][idx]
            if dict_distance == -1:
                s_all_shortest_path = []
                t_all_shortest_path = []
                veh_not = veh_not_sharing[idx]
                v_not_route_ox =  veh_not.get_attribute('route').ox_route
                
                #obtener coordenadas del nodo source
                s = v_not_route_ox.orig
                s_data = G.nodes[s]
                lat_s = s_data['y']
                lon_s = s_data['x']
    
                #obtener coordenadas del nodo target
                t = v_not_route_ox.dest_sharing
                t_data = G.nodes[t]
                lat_t = t_data['y']
                lon_t = t_data['x']
                
                veh_sh = veh_sharing[gen]
                veh_att = veh_sh.get_attribute('route')
                v_route_ox = veh_att.ox_route.route
        
                for node in v_route_ox:
                    node_data = G.nodes[node]
                    lat_veh = node_data['y']
                    lon_veh = node_data['x']
                    
                    dist_s = haversine_distance(lat_s, lon_s, lat_veh, lon_veh)
                    dist_t = haversine_distance(lat_t, lon_t, lat_veh, lon_veh)
                    
                    if dist_s is not None:
                        s_all_shortest_path.append(dist_s)
                    if dist_t is not None:
                         t_all_shortest_path.append(dist_t)
                
                min_s_path = min(s_all_shortest_path)
                min_t_path = min(t_all_shortest_path)
                person_walk = veh_not.user_dist_walk + min_s_path + min_t_path
                distances_dict[gen][idx] = person_walk
            
            total_people_walk += distances_dict[gen][idx]
        else:
            veh_not = veh_not_sharing[idx]
            v_not_route_ox =  veh_not.get_attribute('route').ox_route
            total_people_walk += v_not_route_ox.path_len
            
    return total_people_walk

def _fitness_tot(G, poblacion, veh_sharing, veh_not_sharing, distances_dict):
    score_pob = []
    for cromosoma in poblacion:
        fitness_cromosoma = _fitness(G, cromosoma, veh_sharing, veh_not_sharing, distances_dict)
        score_pob.append(fitness_cromosoma)
    return score_pob

def algoritmo_genetico(veh_factory, n_poblacion, n_generaciones, p_m):
    vehicle_factory_gen = copy.deepcopy(veh_factory)
    veh_sharing = vehicle_factory_gen.veh_sharing
    veh_not_sharing = vehicle_factory_gen.veh_not_sharing
    G = vehicle_factory_gen.G
    fitness_poblacion = []
    distances_dict = {}
    
    #inicialización de la población
    poblacion_inicial, veh_sh_idx, distances_dict = _generar_poblacion(veh_sharing, veh_not_sharing, n_poblacion)
    # print(poblacion_inicial)
    poblacion = poblacion_inicial
    for generacion in range(n_generaciones):
        # print(f"#####Generación {generacion+1}########")
        fitness_poblacion = _fitness_tot(G, poblacion, veh_sharing, veh_not_sharing, distances_dict)
        # print(min(fitness_poblacion))
        hijos = []
        for _ in range(int(n_poblacion/2)):
            #Seleccion de padres
            padre1, padre2 = _seleccion_padres(poblacion, fitness_poblacion, n_padres=2, estrategia='mixta')
            #operador cruce
            hijo1, hijo2 = _cruza_orden_mantener_cantidades(padre1, padre2)
            #operador mutación
            hijo1_m, hijo2_m = _mutacion(hijo1, hijo2, p_m)
            hijos.append(hijo1_m)
            hijos.append(hijo2_m)
        
        fitness_hijos = _fitness_tot(G, hijos, veh_sharing, veh_not_sharing, distances_dict)
        
        #Reemplazo de individuos
        nueva_poblacion = _reemplazo_generacional(poblacion, fitness_poblacion, hijos, fitness_hijos)
        poblacion = nueva_poblacion
        
    return min(fitness_poblacion)
