import os
import sys
import subprocess
import xml.etree.ElementTree as ET

def _add_path_sumo():
    path_sumo_tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    if not os.path.exists(path_sumo_tools):
        try:
            sys.path.append(path_sumo_tools)
        except Exception as error:
            print(
                "SUMO_HOME is not an environment variable. Function _add_path_sumo"
            )
            raise error

def _create_directory(route_dir):
    route_aux = os.path.dirname(route_dir)
    if not(os.path.isdir(route_aux)):
        os.makedirs(route_aux, exist_ok=True)
    return True

#############################################################
def save_net_file(osm_file):
    try:
        _add_path_sumo()
        import osmBuild
        _create_directory(osm_file)
        prefix = osm_file.replace(".osm.xml", "")
        file_net_name = f"{prefix}.net.xml"
        
        
        args = [
            "--osm-file",
            f"{osm_file}",
            "--vehicle-classes=road",
            f"--prefix={prefix}",
        ]
        osmBuild.build(args)
        return file_net_name
    except Exception as error:
        print("Sumo dictionary creation failed. Function save_net_file")
        raise error

##################################################################

def _rout_file(vehicle_types, vehicles, file_name):
    root = ET.Element(
        "routes",
        {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd",
        },
    )
    
    for veh_type in vehicle_types:
        veh_type_keys = veh_type.get_keys()
        vtype = ET.SubElement(root, "vType")
        for key in veh_type_keys:
            vtype.set(key, str(veh_type.get_attribute(key)))

    for vehicle in vehicles:
        vehicle_keys = vehicle.get_keys()
        veh_xml = ET.SubElement(root, "vehicle")
        for key in vehicle_keys:
            if key == "route":
                route = ET.SubElement(veh_xml, "route")
                veh_route = vehicle.get_attribute(key)
                veh_route_sumo = veh_route.route
                route.set("edges", " ".join(map(str, veh_route_sumo)))

            elif key == "type":
                veh_type = vehicle.get_attribute(key)
                id_veh_type = veh_type.get_attribute("id")
                veh_xml.set(key,id_veh_type)
            else:
                veh_xml.set(key,str(vehicle.get_attribute(key)))
            
    tree = ET.ElementTree(root)
    
    tree.write(file_name, xml_declaration=True)
    return True

def _check_file_exists(file):
    if os.path.isfile(file):
        return True
    else:
        return False

#################################################################
def save_rou_file(veh_factory, rou_orig, rou_sim):
    vehicle_types = veh_factory.veh_types
    veh_total = veh_factory.vehicles
    veh_sharing = veh_factory.veh_sharing
    veh_not_get = veh_factory.veh_not_get
    veh_ignore = veh_factory.veh_ignore
    vehicles_total_sharing = []

    vehicles_total_sharing = veh_sharing + veh_not_get + veh_ignore

    rou_orig_exists = _check_file_exists(rou_orig)
    rou_sim_exists = _check_file_exists(rou_sim)

    if not(rou_orig_exists):
        _create_directory(rou_orig)
        _rout_file(vehicle_types, veh_total, rou_orig)

    if not(rou_sim_exists):
        _create_directory(rou_sim)
        _rout_file(vehicle_types, vehicles_total_sharing, rou_sim)
    return True



def _config_file(id, config_file, rou_file, net_file, sharing):
    directorio = os.getcwd()
    net_aux = os.path.join(directorio, net_file)
    net_aux = os.path.normpath(net_aux)
    
    rou_aux = rou_file.split("/")[-1]
    
    if not(sharing):    
        trip_aux = f"tripinfo.xml"
        emiss_aux = f"emissions.xml"
        sum_aux = f"summary.xml"
        stat_aux = f"statistics.xml"
            
    else:
        trip_aux = f"{id}_tripinfo_sh.xml"
        emiss_aux = f"{id}_emissions_sh.xml"
        sum_aux = f"{id}_summary_sh.xml"
        stat_aux = f"{id}_statistics_sh.xml"
        
    root = ET.Element("configuration")
    
    input_elem = ET.SubElement(root, "input")
    net_file = ET.SubElement(input_elem, "net-file")
    net_file.set("value", net_aux)
    route_files = ET.SubElement(input_elem, "route-files")
    route_files.set("value", rou_aux)
     
    # Create the output element
    output_elem = ET.SubElement(root, "output")
    tripinfo_output = ET.SubElement(output_elem, "tripinfo-output")
    tripinfo_output.set("value", trip_aux)
    emission_output = ET.SubElement(output_elem, "emission-output")
    emission_output.set("value",emiss_aux)
    summary_output = ET.SubElement(output_elem, "summary-output")
    summary_output.set("value", sum_aux)
    statistics_output = ET.SubElement(output_elem, "statistic-output")
    statistics_output.set("value", stat_aux)
    ignore_route_errors = ET.SubElement(output_elem, "ignore-route-errors")
    ignore_route_errors.set("value", "true")
    
    tree = ET.ElementTree(root)            
    tree.write(config_file, xml_declaration=True)
    return True

##################################################################

def save_config_file(id, config_file, rou_file, net_file, sharing):
    try:
        config_file_exists = _check_file_exists(config_file)
        rou_file_exists = _check_file_exists(rou_file)
        net_file_exists = _check_file_exists(net_file)

        if not(rou_file_exists):
            print("----Crea archivo rou primero-----")
            print(rou_file)
            return

        if not(net_file_exists):
            print("----Crea archivo net primero-----")
            print(net_file)
            return

        if config_file_exists:
            print("----Archivo config ya existe-----")
            print(config_file)
            return 

        _create_directory(config_file)
        _config_file(id, config_file, rou_file, net_file, sharing)    
        dir1 = os.getcwd()
        config_final = os.path.join(dir1, config_file)
        config_final = os.path.normpath(config_final)
        return config_final
        
    except Exception as error:
        print(error)


def get_statistics(stats_file):
    dir1 = os.getcwd()
    stats_file_f = os.path.join(dir1, stats_file)
    stats_file_f = os.path.normpath(stats_file_f)
    
    tree = ET.parse(stats_file_f)
    root = tree.getroot()
    veh_stats = {}
    
    veh_stats_element = root.find('vehicleTripStatistics')
    veh_stats['count'] = int(veh_stats_element.get('count'))
    veh_stats['routeLength'] = float(veh_stats_element.get('routeLength'))
    veh_stats['speed'] = float(veh_stats_element.get('speed'))
    veh_stats['duration'] = float(veh_stats_element.get('duration'))
    veh_stats['waitingTime'] = float(veh_stats_element.get('waitingTime'))
    veh_stats['timeLoss'] = float(veh_stats_element.get('timeLoss'))
    veh_stats['departDelay'] = float(veh_stats_element.get('departDelay'))
    veh_stats['departDelayWaiting'] = float(veh_stats_element.get('departDelayWaiting'))
    veh_stats['totalTravelTime'] = float(veh_stats_element.get('totalTravelTime'))
    veh_stats['totalDepartDelay'] = float(veh_stats_element.get('totalDepartDelay'))
    
    return veh_stats

def get_emissions(emiss_file):
    dir1 = os.getcwd()
    emiss_file_f = os.path.join(dir1, emiss_file)
    emiss_file_f = os.path.normpath(emiss_file_f)
    
    tree = ET.parse(emiss_file_f)
    root = tree.getroot()
    vehicles = []
    co2_emissions = []
    co_emissions = []
    hc_emissions = []
    nox_emissions = []
    
    for timestep in root.findall('timestep'):
        for vehicle in timestep.findall('vehicle'):
            vehicles.append(vehicle.get('id'))
            co2_emissions.append(float(vehicle.get('CO2')))
            co_emissions.append(float(vehicle.get('CO')))
            hc_emissions.append(float(vehicle.get('HC')))
            nox_emissions.append(float(vehicle.get('NOx')))
    
    total_co2 = sum(co2_emissions)
    total_co = sum(co_emissions)
    total_hc = sum(hc_emissions)
    total_nox = sum(nox_emissions)

    return {'total_co2':total_co2, 'total_co':total_co, 'total_hc':total_hc, 'total_nox':total_nox}


def run_sumo_simulation(file_config_name): 
    try:
        # Verificar que la variable de entorno SUMO_HOME esté configurada
        if 'SUMO_HOME' not in os.environ:
            raise EnvironmentError("La variable de entorno SUMO_HOME no está configurada.")

        # Construir la ruta al ejecutable de SUMO
        sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo')
        subprocess.call([sumo_binary, "-c", file_config_name])
        return True
    except Exception as error:
        print(f"Error al ejecutar la simulación de SUMO: {error}")
        return False