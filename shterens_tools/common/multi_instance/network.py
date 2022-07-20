import os
import time
import socket
import typing
import inspect
import crossplane
import subprocess
from threading import Thread
from ..resources.config import config
from ..resources.paths import rootPath
from multiprocessing.managers import SyncManager, State

class ExManager(SyncManager):
    '''
    Custom multiprocessing.SyncManager
    '''
    def __init__(self, address=None, authkey=None, serializer="pickle", ctx=None, isClient=False):
        if not isClient:
            address = ("127.0.0.1", get_available_port(address[1]))
            authkey = inspect.getmodule(inspect.stack()[1][0]).__name__.encode()
        super().__init__(address, authkey, serializer, ctx)
    
    @classmethod
    def create_object(cls, objectName: str, ClassType: typing.Type, *args, **kwargs):
        '''
        Creates object inside ExManager

        :param objectName: Object name
        :param ClassType: Class type
        :param args: Args for class constructor
        :param kwargs: Kwargs for class constructor

        cls.objectName = ClassType(*args, **kwargs)
        '''
        setattr(cls, objectName, ClassType(*args, **kwargs))
    
    @classmethod
    def get_object(cls, objectName: str) -> typing.Any:
        '''
        Returns object with name

        :param objectName: Object name
        '''
        if not hasattr(cls, objectName):
            raise AttributeError(f"Create object \"{objectName}\" with create_object() before accessing it")
        
        return getattr(cls, objectName)
    
    @property
    def authkey(self):
        return self._authkey
    
    @classmethod
    def register_access_method(cls, methodName: str, objectName: str):
        '''
        Creates access method for existing object

        :param methodName: Method name
        :param objectName: Object name

        def methodName(): return cls.objectName

        Register objects in the order they are used in your code
        '''
        sharedObject = cls.get_object(objectName)
        def accessMethod() -> sharedObject.__class__: return sharedObject
        cls.register(methodName, callable=accessMethod)
    
    @classmethod
    def parse_shared_objects(cls) -> typing.Dict[str, type]:
        '''
        Parses shared objects added via register_access_method() or register()

        Returns a dictionary { objName : objType }
        
        Make sure your registered functions have a return type hint, 
        otherwise objType will be set as a function reference
        '''
        sharedObjects = {}

        for objName, objValues in cls._registry.items():
            obj = objValues[0]

            if inspect.isroutine(obj):
                typeHints = inspect.get_annotations(obj)
                if "return" in typeHints:
                    sharedObjects[objName] = typeHints["return"]
                else:
                    sharedObjects[objName] = obj

            elif inspect.isclass(obj):
                sharedObjects[objName] = obj
        
        return sharedObjects
    
    def run_server(self):
        '''
        Runs ExManager server in new threading.Thread
        '''
        server = self.get_server()
        self._state.value = State.STARTED
        Thread(target=server.serve_forever, daemon=True).start()


class NginxManager():
    
    serverPort = 8000
    cwdPath = rootPath
    configPath = "nginx.conf"
    
    @classmethod
    def __init_subclass__(cls):
        #  Change current working directory on Windows
        #  Because Nginx for Windows uses relative paths like conf/nginx.conf, logs/error.log
        if os.name == "nt":
            cls.cwdPath = config.get("MultipleInstances", "nginxFolderPath")
        else:
            cls.cwdPath = os.curdir

    @staticmethod
    def generate_config(ports: typing.List[int]):
        config = [{"directive": "events",
                   "args": [],
                   "block": [{
                       "directive": "worker_connections",
                       "args": ["10000"]
                   }]
                  },
                  {"directive": "http",
                   "args": [],
                   "block": [{
                       "directive": "upstream",
                       "args": ["bot"],
                       "block": []
                   },
                   {
                       "directive": "server",
                       "args": [],
                       "block": [
                       {
                           "directive": "listen",
                           "args": []
                       },
                       {
                           "directive": "location",
                           "args": ["/"],
                           "block": [{
                               "directive": "proxy_pass",
                               "args": ["http://bot"]
                           }]
                       }]
                   }]}]
        
        #  Add bot servers
        for port in ports:
            config[1]["block"][0]["block"].append({"directive": "server", "args": [f"127.0.0.1:{port}"]})
        
        #  Set listen port
        NginxManager.serverPort = get_available_port(NginxManager.serverPort)
        config[1]["block"][1]["block"][0]["args"].append(f"{NginxManager.serverPort}")
        
        #  Build and save config
        NginxManager.configPath = os.path.join(rootPath, NginxManager.configPath)
        with open(NginxManager.configPath, "w") as configFile:
            configFile.write(crossplane.build(config))
    
    @staticmethod
    def start():
        #  Non-blocking start nginx call
        popenKwargs = {}

        popenKwargs.update(
            args=["nginx", "-c", NginxManager.configPath],
            shell=True, 
            cwd=NginxManager.cwdPath
        )
        
        if os.name == "nt":
            popenKwargs.update(creationflags=subprocess.DETACHED_PROCESS)

        subprocess.Popen(**popenKwargs)
        time.sleep(2)

    @staticmethod
    def stop():
        subprocess.run(
            args=["nginx", "-s", "stop"], 
            shell=True, 
            cwd=NginxManager.cwdPath
        )


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_available_port(port: int) -> int:
    while is_port_in_use(port):
        port += 1
    return port
