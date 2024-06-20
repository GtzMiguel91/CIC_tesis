import os
import sys
import subprocess
import xml.etree.ElementTree as ET

class SumoFiles:
    def __init__(self, directory_orig=None, directory_alg=None):
        try:
            self._add_path_sumo()
            self._osm_file = ""
            self._file_net_name = ""
            self._file_rou_orig = "" 
            self._file_rou_sh = ""
            self._file_config_orig = ""
            self._file_config_sh = ""
            self._prefix = ""
            self._outputs_orig = {}
            self._outputs_sh = {}
            self._directory_orig = directory_orig
            self._directory_alg = directory_alg
            self._exists_files_orig = False
            self._create_directory()
        
        except Exception as error:
            print("Log: Error in constructor")
            print(error)

    def _add_path_sumo(self):
        path_sumo_tools = os.path.join(os.environ["SUMO_HOME"], "tools")
        if not os.path.exists(path_sumo_tools):
            try:
                sys.path.append(path_sumo_tools)
            except Exception as error:
                print(
                    "SUMO_HOME is not an environment variable. Function _add_path_sumo"
                )
                raise error
    
    def _create_directory(self):
        if self._directory_orig:
            os.makedirs(self._directory_orig, exist_ok=True)
        if self._directory_alg:
            os.makedirs(self._directory_alg, exist_ok=True)

#############################################################
    def _get_prefix(self, directory):
        # Dividir la cadena utilizando el delimitador "/"
        prefix = directory.split("/")[-1]
            
        prefix = prefix.replace(".net.xml", "")
        prefix = prefix.replace(".osm.xml", "")
        self._prefix = prefix
    
#############################################################
    def save_net_file(self, osm_file):
        try:
            import osmBuild
            prefix = osm_file.replace(".osm.xml", "")
            self._file_net_name = f"{prefix}.net.xml"
            self._get_prefix(osm_file)
            
            args = [
                "--osm-file",
                f"{osm_file}",
                "--vehicle-classes=road",
                f"--prefix={prefix}",
            ]
            osmBuild.build(args)
            return self._file_net_name
        except Exception as error:
            print("Sumo dictionary creation failed. Function save_net_file")
            raise error

##################################################################
    
    def _rout_file(self, vehicle_types, vehicles, file_name):
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
        f = file_name
        
        if "_compartiendo" in f:
            if self._directory_alg:
                f = f"{self._directory_alg}/{file_name}"
            self._file_rou_sh = f
            
        else:
            if self._directory_orig:
                f = f"{self._directory_orig}/{file_name}"
            self._file_rou_orig = f
        
        tree.write(f, xml_declaration=True)
        return True

#################################################################
    def save_rou_file(self, veh_factory, id):
        vehicle_types = veh_factory.veh_types
        veh_total = veh_factory.vehicles
        veh_sharing = veh_factory.veh_sharing
        veh_not_get = veh_factory.veh_not_get
        veh_ignore = veh_factory.veh_ignore
        vehicles_total_sharing = []

        vehicles_total_sharing = veh_sharing + veh_not_get + veh_ignore
        f = f"{id}_{self._prefix}.rou.xml"
        direct_aux = os.getcwd()
        if self._directory_orig:
            direct_aux = os.path.join(direct_aux, self._directory_orig)
        files_names = os.listdir(direct_aux)
        files_names = [file for file in files_names if os.path.isfile(os.path.join(direct_aux, file))]

        if f not in files_names:
            self._rout_file(vehicle_types, veh_total, f)
        else:
            self._exists_files_orig = True
        
        f = f"{id}_{self._prefix}_compartiendo.rou.xml"
        self._rout_file(vehicle_types, vehicles_total_sharing, f)
        return self._file_rou_orig, self._file_rou_sh

    
    
    def _config_file(self, file_name, id):
        net_aux = self._file_net_name
        f = file_name
                    
        if not("_compartiendo" in f):
            trip_aux = f"{id}_tripinfo.xml"
            emiss_aux = f"{id}_emissions.xml"
            sum_aux = f"{id}_summary.xml"
            stat_aux = f"{id}_statistics.xml"
                
        else:
            trip_aux = f"{id}_tripinfo_compartiendo.xml"
            emiss_aux = f"{id}_emissions_compartiendo.xml"
            sum_aux = f"{id}_summary_compartiendo.xml"
            stat_aux = f"{id}_statistics_compartiendo.xml"
            
        if not("_compartiendo" in f):
            if self._directory_orig:
                f = f"{self._directory_orig}/{file_name}"
                trip_aux = f"{self._directory_orig}/{tripinfo_aux}"
                emiss_aux = f"{self._directory_orig}/{emiss_aux}"
                sum_aux = f"{self._directory_orig}/{sum_aux}"
                stat_aux = f"{self._directory_orig}/{stat_aux}"
            self._outputs_orig["trip_info_file"] = trip_aux
            self._outputs_orig["emissions_file"] = emiss_aux
            self._outputs_orig["summary_file"] = sum_aux
            self._outputs_orig["statistics_file"] = stat_aux
            self._file_config_orig = f
            rou_aux = self._file_rou_orig
        else:
            if self._directory_alg:
                f = f"{self._directory_alg}/{file_name}"
                trip_aux = f"{self._directory_alg}/{tripinfo_aux}"
                emiss_aux = f"{self._directory_alg}/{emiss_aux}"
                sum_aux = f"{self._directory_alg}/{sum_aux}"
                stat_aux = f"{self._directory_alg}/{stat_aux}"
            self._outputs_sh["trip_info_file_sh"] = trip_aux
            self._outputs_sh["emissions_file_sh"] = emiss_aux
            self._outputs_sh["summary_file_sh"] = sum_aux
            self._outputs_sh["statistics_file"] = stat_aux
            self._file_config_sh = f
            rou_aux = self._file_rou_sh

        net_aux = net_aux.replace('/', '\\')
        rou_aux = rou_aux.replace('/', '\\')
        trip_aux = trip_aux.replace('/', '\\')
        emiss_aux = emiss_aux.replace('/', '\\')
        sum_aux = sum_aux.replace('/', '\\')
        stat_aux = stat_aux.replace('/', '\\')
        
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
        tree.write(f, xml_declaration=True)
        return True
    
    def save_config_file(self, id):
        try:
            if not(self._file_net_name and self._file_rou_orig):
                raise Exception("Error. Los archivos net y rutas deben ser creados primero!!!")

            file_name = self._prefix
            aux = self._exists_files_orig

            if not(aux):
                f = f"{id}_{file_name}.sumocfg"
                self._config_file(f, id)
            
            f = f"{id}_{file_name}_compartiendo.sumocfg"
            self._config_file(f, id)
            return self._file_config_orig, self._file_config_sh
            
        except Exception as error:
            print(error)


    @property
    def file_net_name(self):
        return self._file_net_name

    @file_net_name.setter
    def file_net_name(self, file_net_name):
        self._get_prefix(self, file_net_name)
        self._file_net_name = file_net_name

    @property
    def directory_orig(self):
        return self._directory_orig

    @directory_orig.setter
    def directory_orig(self, directory_orig):
        self._directory_orig = directory_orig
        self._create_directory()

    @property
    def directory_alg(self):
        return self._directory_alg

    @directory_alg.setter
    def directory_alg(self, directory_alg):
        self._directory_alg = directory_alg
        self._create_directory()
    
    
    
    
