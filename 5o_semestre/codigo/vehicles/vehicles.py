import numpy as np
import random
import uuid

class DynamicAttributes:
    """
    Clase que permite manejar atributos dinámicos para sus instancias.

    Atributos:
    ----------
    _attributes : dict
        Diccionario que almacena los atributos dinámicos.
    """

    def __init__(self):
        """
        Inicializa una instancia de DynamicAttributes.
        """
        self._attributes = {}

    def get_attribute(self, key):
        """
        Obtiene el valor de un atributo específico.

        Parámetros:
        -----------
        key : str
            Clave del atributo a obtener.

        Devuelve:
        ---------
        any
            Valor del atributo, o None si no existe.
        """
        return self._attributes.get(key)

    def set_attribute(self, key, value):
        """
        Establece el valor de un atributo.

        Parámetros:
        -----------
        key : str
            Clave del atributo a establecer.
        value : any
            Valor del atributo a establecer.
        """
        self._attributes[key] = value

    def get_keys(self):
        """
        Obtiene todas las claves de los atributos.

        Devuelve:
        ---------
        list o None
            Lista de claves de los atributos, o None si no hay atributos.
        """
        if self._attributes:
            return list(self._attributes.keys())
        else:
            return None

class VehicleType(DynamicAttributes):
    """
    Clase que representa el tipo de un vehículo, hereda de DynamicAttributes.
    """
    pass

class Vehicle(DynamicAttributes):
    """
    Clase que representa un vehículo, hereda de DynamicAttributes.

    Atributos:
    ----------
    _id: int
        Id del vehículo
    _sharing : bool
        Indica si el vehículo es compartido.
    _vehicles_sharing : list
        Lista de vehículos compartidos.
    _user_dist_walk : float
        Distancia total que el usuario debe caminar.
    """
    def __init__(self, p_sharing):
        """
        Inicializa una instancia de Vehicle.

        Parámetros:
        -----------
        p_sharing : float
            Probabilidad de que el vehículo sea compartido.
        """
        super().__init__()
        self._id = uuid.uuid4().int
        self._sharing = None
        self._vehicles_sharing = []
        if p_sharing is not None:
            self._sharing = True if random.random() > p_sharing else False
        self._user_dist_walk = 0 # if sharing, total distance

    def __eq__(self, other):
        """
        Compara si dos vehículos son iguales basándose en su identificador.

        Parámetros:
        -----------
        other : Vehicle
            Otra instancia de Vehicle.

        Devuelve:
        ---------
        bool
            True si los vehículos son iguales, False en caso contrario.
        """
        if isinstance(other, Vehicle):
            return self._id == other.id
        return False
    
    @property
    def user_dist_walk(self):
        """
        Obtiene la distancia total que el usuario debe caminar.

        Devuelve:
        ---------
        float
            Distancia total que el usuario debe caminar.
        """
        return self._user_dist_walk

    @user_dist_walk.setter
    def user_dist_walk(self, value):
        """
        Establece la distancia total que el usuario debe caminar.

        Parámetros:
        -----------
        value : float
            Distancia total que el usuario debe caminar.
        """
        self._user_dist_walk = value

    @property
    def sharing(self):
        """
        Indica si el vehículo es compartido.

        Devuelve:
        ---------
        bool
            True si el vehículo es compartido, False en caso contrario.
        """
        return self._sharing

    @property
    def vehicles_sharing(self):
        """
        Obtiene la lista de vehículos que comparten la misma trayectoria.

        Devuelve:
        ---------
        list
            Lista de vehículos que comparten la misma trayectoria.
        """
        return self._vehicles_sharing

    @vehicles_sharing.setter
    def vehicles_sharing(self, vehicle):
        """
        Añade un vehículo a la lista de vehículos compartidos.

        Parámetros:
        -----------
        vehicle : Vehicle
            Vehículo que compartira trayectoria.
        """
        self._vehicles_sharing.append(vehicle)

    @property
    def id(self):
        """
        Devuelve el identificador único del vehículo.

        Devuelve:
        ---------
        int
            Identificador único del vehículo.
        """
        return self._id

class VehicleFactory:
    """
    Clase para la creación de vehículos.

    Atributos:
    ----------
    _G : networkx.MultiDiGraph
        Grafo del mapa.
    _vehicles : list
        Lista de vehículos creados.
    _sharing_type : str
        Tipo de compartición de vehículos.
    _veh_ignore : list
        Lista de vehículos ignorados.
    _veh_sharing : list
        Lista de vehículos compartidos.
    _veh_not_sharing : list
        Lista de vehículos que quieren viajar en vehículo.
    _p_ignore : float
        Probabilidad de ignorar un vehículo.
    _p_sharing : float
        Probabilidad de que un vehículo sea compartido.
    _distribution : str
        Tipo de distribución del trafico de vehículos..
    _scale : float
        Escala para la distribución exponencial.
    _elements_to_ignore : list
        Lista de elementos a ignorar.
    _veh_not_get : list
        Personas que no alcanzaron vehículo por falta de personas que quisieran compartir.
    _veh_types : list
        Lista de tipos de vehiculos de tipo VehicleType.
    _total_vehicles_capacity : int
        Capacidad total de todos los vehiculos
    """
    def __init__(self, G, veh_types, sharing_type=None, p_ignore=None, p_sharing=None, distribution=None, scale=None):
        """
        Inicializa una instancia de VehicleFactory.

        Parámetros:
        -----------
        G : networkx.MultiDiGraph
            Grafo del mapa de la clase Map.
        veh_types: list
            Lista de tipo de vehículos de tipo VehicleType
        sharing_type : str, opcional
            Tipo de compartición de vehículos.
        p_ignore : float, opcional
            Probabilidad de ignorar un vehículo.
        p_sharing : float, opcional
            Probabilidad de que un vehículo sea compartido.
        distribution : str, opcional
            Tipo de distribución del trafico de vehículos.
        scale : float, opcional
            Escala para la distribución exponencial.
        """
        if sharing_type is not None:
            if not(p_ignore and p_sharing):
                raise ValueError("p_ignore y p_sharing son obligatorios si sharing_type es diferente de None.")
        if distribution is not None:
            if not(scale):
                raise ValueError("scale es obligatorio si distribution es diferente de None.")
        self._G = G
        self._vehicles = []
        self._sharing_type = sharing_type
        self._veh_ignore = []
        self._veh_sharing = []
        self._veh_not_sharing = []
        self._veh_not_get = []
        self._veh_types = veh_types
        self._p_ignore = p_ignore
        self._p_sharing = p_sharing
        self._distribution = distribution
        self._scale = scale
        self._dict_vehicles = {}
        self._elements_to_ignore = None
        self._total_vehicles_capacity = 0
        
        
    
    def _create_vehicle(self, id, veh_type, route, depart=0):
        """
        Crea un vehículo y lo añade a la lista de vehículos.

        Parámetros:
        -----------
        id : str
            Identificador del vehículo.
        veh_type : str
            Tipo del vehículo creado de la clase VehicleType.
        route : Route
            Ruta del vehículo creado en la fabrica Sumo.
        depart : int, opcional
            Tiempo de salida del vehículo. Por defecto es 0.
        """
        vehicle = Vehicle(self._p_sharing)
        vehicle.set_attribute("id", id)
        vehicle.set_attribute("type", veh_type)
        vehicle.set_attribute("route", route)
        vehicle.set_attribute("depart", depart)
        vehicle.set_attribute("personNumber", 1) #1 porque incluye al conductor por default
        vehicle.user_dist_walk = route.ox_route._orig_dist
        self._vehicles.append(vehicle)
        self._dict_vehicles[id] = vehicle
        if self._sharing_type == 'random':
            if route in self._elements_to_ignore:
                self._veh_ignore.append(vehicle)
            else:
                if vehicle.sharing:
                    veh_type = vehicle.get_attribute("type")
                    veh_capacity = veh_type.get_attribute("personCapacity") - 1 #se descuenta al chofer
                    self._total_vehicles_capacity += veh_capacity
                    self._veh_sharing.append(vehicle)
                else:
                    self._veh_not_sharing.append(vehicle)

    
    def _exponential_distribution(self, routes):
        """
        Crea vehículos utilizando una distribución exponencial para los tiempos de salida.

        Parámetros:
        -----------
        routes : list
            Lista de rutas para los vehículos.
        veh_types : list
            Lista de tipos de vehículos.
        """
        size = len(routes)
        depart = np.random.exponential(self._scale, size)
        # order_depart = np.sort(depart)

        if self._sharing_type == 'random':
            num_elements_to_ignore = int(len(routes) * self._p_ignore)
            self._elements_to_ignore = random.sample(routes, num_elements_to_ignore)
        
        for idx, route in enumerate(routes):
            veh_type = np.random.choice(self._veh_types)
            self._create_vehicle(f"veh{idx}", veh_type, route, depart[idx])
            

    def _none_distribution(self, routes):
        """
        Crea vehículos sin utilizar una distribución específica para los tiempos de salida.

        Parámetros:
        -----------
        routes : list
            Lista de rutas para los vehículos.
        veh_types : list
            Lista de tipos de vehículos.
        """
        if self._sharing_type == 'random':
            num_elements_to_ignore = int(len(routes) * self._p_ignore)
            self._elements_to_ignore = random.sample(routes, num_elements_to_ignore)
            
        for idx, route in enumerate(routes):
            veh_type = np.random.choice(self._veh_types)
            self._create_vehicle(f"veh{idx}", veh_type, route)

    def create_vehicles(self, routes):
        """
        Crea vehículos utilizando la distribución especificada.

        Parámetros:
        -----------
        routes : list
            Lista de rutas para los vehículos.
        """
        if self._distribution == "exponential":
            self._exponential_distribution(routes)
        else:
            self._none_distribution(routes)

    def get_vehicles_length(self):
        """
        Obtiene la cantidad de vehículos creados.

        Devuelve:
        ---------
        int
            Cantidad de vehículos creados.
        """
        return len(self._vehicles)

    def get_vehicle_by_id(self, id):
        """
        Obtiene vehicle por id.

        Devuelve:
        ---------
        Vehicle
            Vehículo.
        """
        return self._dict_vehicles[id]
    
    @property
    def veh_sharing(self):
        """
        Obtiene la lista de vehículos compartidos.

        Devuelve:
        ---------
        list
            Lista de vehículos compartidos.
        """
        return self._veh_sharing

    @property
    def veh_not_sharing(self):
        """
        Obtiene la lista de vehículos no compartidos.

        Devuelve:
        ---------
        list
            Lista de vehículos no compartidos.
        """
        return self._veh_not_sharing
    
    @property
    def veh_ignore(self):
        """
        Obtiene la lista de vehículos ignorados.

        Devuelve:
        ---------
        list
            Lista de vehículos ignorados.
        """
        return self._veh_ignore
    
    @property
    def vehicles(self):
        """
        Obtiene la lista de todos los vehículos creados.

        Devuelve:
        ---------
        list
            Lista de todos los vehículos creados.
        """
        return self._vehicles

    @property
    def G(self):
        """
        Obtiene el grafo del mapa.

        Devuelve:
        ---------
        networkx.MultiDiGraph
            Grafo del mapa de la clase Map.
        """
        return self._G

    @property
    def total_vehicles_capacity(self):
        """
        Capacidad total de todos los vehiculos.

        Devuelve:
        ---------
        int
            Total de todos los vehiculos.
        """
        return self._total_vehicles_capacity
    
    @property
    def veh_not_get(self):
        """
        Obtiene el número de personas que no alcanzaron vehículo por falta de personas que quisieran compartir.
        
        Devuelve:
        ---------
        list
            El número de personas que no alcanzaron vehículo.
        """
        return self._veh_not_get

    @veh_not_get.setter
    def veh_not_get(self, veh):
        """
        Establece el número de personas que no alcanzaron vehículo por falta de personas que quisieran compartir.
    
        Parámetros:
        -----------
        veh : Vehicle
            Vehículo tipo Vehicle
        """
        self._veh_not_get.append(veh)
    
    @property
    def veh_types(self):
        """
        Obtiene la lista de tipo de vehículos.
        
        Devuelve:
        ---------
        list
            La lista de tipo de vehículos.
        """
        return self._veh_types
