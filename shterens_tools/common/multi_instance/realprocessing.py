'''
Realprocessing v0.0.1

Light self-made multiprocessing library

Just for fun
'''
import os
import time
import uuid
import typing
import signal
import inspect
import asyncio
import subprocess
from .network import ExManager
from multiprocessing import get_context
from multiprocessing.queues import Queue
from ..utils.regex import uuid_to_varname, oneliner_to_multiliner

class RealProcess():
    '''
    RealProcess is a oneliner launched on the command line

    Generated with the following arguments:
    
    :param target: Function to be run, a tuple matching
        pattern: ( "func", func )
    :param targetKwargs: Function kwargs, to use synchronized
        objects registered in ExManager specify argument value as
        object type: { "name": "SlimShady", "age": 12, "queue": ExQueue }
    :param targetGlobals: Global variables that need to be declared
        in the namespace, they are passed in the same way as targetKwargs
    :param manager: ExManager object that RealProcess will access
        for shared variables

    To pass routines and classes as arguments, use tuples:
    * ( "func(args, kwargs)", func )
    * ( "Class(args, kwargs)", Class )
    * ( "object.method(args, kwargs)", object.method )

    Classes with no arguments in the constructor can be passed as types,
        but this approach is not recommended:
    * instead of { "person": Person } use { "person": ( "Person()", Person ) }

    Don't use multiprocessing or threading Lock and Event, they are out of sync
    between RealProcesses, use RealLock and RealEvent instead
    '''
    def __init__(
        self,
        target: typing.Tuple[str, typing.Callable],
        targetKwargs: typing.Dict[str, object]={},
        targetGlobals: typing.Dict[str, object]={},
        manager: ExManager=None
    ):
        calledFrom = inspect.getmodule(inspect.stack()[1][0])
        
        calledFromName = calledFrom.__name__
        if calledFromName == "__main__":
            calledFromName = inspect.getmodulename(calledFrom.__file__)

        self.cwdPath = calledFrom.__file__

        for name in calledFromName.split("."):
            self.cwdPath = os.path.split(self.cwdPath)[0]
        
        self.oneliner = RealProcessParser.create_oneliner(
            calledFromName,
            target,
            targetKwargs,
            targetGlobals,
            manager
        )

    def start(self):
        popenKwargs = {}

        popenKwargs.update(
            args=["python", "-c", f"{self.oneliner}"],
            shell=True,
            cwd=self.cwdPath
        )

        if os.name == "nt":
            popenKwargs.update(creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            popenKwargs.update(start_new_session=True)

        self.process = subprocess.Popen(**popenKwargs)

    def join(self):
        while self.process.poll() is None:
            time.sleep(1)

    def terminate(self):
        if os.name == "nt":
            self.process.send_signal(signal.CTRL_C_EVENT)
        else:
            self.process.send_signal(signal.SIGINT)


class RealProcessParser():
    '''
    Parser for creating oneliners of the RealProcess
    '''
    @staticmethod
    def create_oneliner(
        moduleName: str,
        target: typing.Tuple[str, typing.Callable],
        targetKwargs: typing.Dict[str, object],
        targetGlobals: typing.Dict[str, object],
        manager: ExManager
    ) -> str:
        '''
        Builds oneliner with given RealProcess arguments
        '''
        oneliner = [
            f"import {moduleName}",
            f"{moduleName}.__realprocess__ = 1"
        ]
        
        if manager is not None:
            oneliner.append("from multiprocessing.managers import SyncManager")
        
        targetKwargs, targetHints = RealProcessParser.parse_kwargs(targetKwargs)
        targetGlobals, globalsHints = RealProcessParser.parse_kwargs(targetGlobals)
        
        if manager is not None:
            sharedObjects = manager.parse_shared_objects()
            targetKwargs.update(
                RealProcessParser.create_associations(
                    objects=sharedObjects,
                    hints=targetHints,
                    objectsPrefix="manager."
                )
            )
            targetGlobals.update(
                RealProcessParser.create_associations(
                    objects=sharedObjects,
                    hints=globalsHints,
                    objectsPrefix="manager."
                )
            )
        else:
            sharedObjects = None

        targetKwargs.update(
            RealProcessParser.wrap_undefined_hints(targetHints)
        )
        targetGlobals.update(
            RealProcessParser.wrap_undefined_hints(globalsHints)
        )
        
        targetHints = RealProcessParser.parse_globals(
            oneliner=oneliner,
            targetGlobals=targetKwargs,
            sharedObjects=sharedObjects,
            useUUID=True
        )
        globalsHints = RealProcessParser.parse_globals(
            oneliner=oneliner,
            targetGlobals=targetGlobals,
            sharedObjects=sharedObjects,
            useGlobal=True
        )

        if manager is not None:
            targetHints["__manager__"] += globalsHints["__manager__"] - 3

            oneliner.insert(
                targetHints["__manager__"],
                f"manager = SyncManager(address={manager.address}, authkey={manager.authkey})"
            )
            oneliner.insert(
                targetHints["__manager__"] + 1,
                "manager.connect()"
            )
            targetHints.pop("__manager__")
        
        targetKwargs = ", ".join([f"{kwargName}={varname}" for kwargName, varname in targetHints.items()])
        oneliner.append(f"{moduleName}.{target[0]}({targetKwargs})")
        
        return "; ".join(oneliner)

    @staticmethod
    def parse_kwargs(
        targetKwargs: typing.Dict[str, object]
    ) -> typing.Tuple[typing.Dict[str, object], typing.Dict[str, type]]:
        '''
        Parses kwargs, separates values from classes and routines
        
        Values are added in kwargs and the rest in hints,
        which will be used by create_associations() and wrap_undefined_hints()
        
        Functions and classes passed in the correct format are added to kwargs,
        see RealProcess

        Returns parsedKwargs, parsedHints
        '''
        parsedKwargs = {}
        parsedHints = {}
        
        for kwargName, kwargObject in targetKwargs.items():
            if inspect.isclass(kwargObject) or inspect.isroutine(kwargObject):
                parsedHints[kwargName] = kwargObject
            elif isinstance(kwargObject, str):
                parsedKwargs[kwargName] = f"'{kwargObject}'"
            elif isinstance(kwargObject, tuple):
                parsedKwargs[kwargName] = kwargObject[0]
            else:
                parsedKwargs[kwargName] = kwargObject

        return parsedKwargs, parsedHints

    @staticmethod
    def create_associations(
        objects: typing.Dict[str, type],
        hints: typing.Dict[str, type],
        objectsPrefix: str = ""
    ) -> typing.Dict[str, str]:
        '''
        Builds associations between the given objects and hints
        
        If the object type matches the hint type, an association
        is built that the hint can be obtained by creating an object from objects
        
        Whether it's creating a class or calling a function
        
        :param objectsPrefix: Prefix used to address objects,
            for example, if the objects are in a class, you can specify
            the name of the instance "instance."

        for a class access method the association looks like this:
        { "queue": ( "get_queue", "ExQueue", "prefix.get_queue()" ) }
        
        or just for class:
        { "person": ( "Person", "Person", "prefix.Person()" ) }

        for the function like this:
        { "lock": ( "create_lock", "create_lock", "prefix.create_lock()" ) }
        '''
        associations = {}

        for objName, objType in objects.items():
            for varName, varType in hints.items():
                if varName in associations:
                    continue
                if varType is objType:
                    if inspect.isclass(objType):
                        associations[varName] = (objName, objType.__name__, f"{objectsPrefix}{objName}()")
                    else:
                        associations[varName] = (objName, objName, f"{objectsPrefix}{objName}()")
        
        for varName in associations.keys():
            hints.pop(varName)

        return associations
    
    @staticmethod
    def wrap_undefined_hints(hints: typing.Dict[str, type]) -> typing.Dict[str, str]:
        '''
        Builds associations for objects that are not values and were not found in the ExManager namespace
        
        This most likely means that:
        * you passed a class or function in the wrong format, see RealProcess
        * you forgot to register the type in ExManager
        * you forgot to pass the ExManager instance to the RealProcess manager argument
        
        The associations looks like this:
        { "person": "Person()" }
        { "x": "int()" }
        '''
        associations = {}

        for varName, varType in hints.items():
            associations[varName] = f"{varType.__name__}()"

        return associations

    @staticmethod
    def parse_globals(
        oneliner: typing.List[str],
        targetGlobals: typing.Dict[str, object],
        sharedObjects: typing.Dict[str, type]=None,
        useGlobal: bool=False,
        useUUID: bool=False
    ) -> typing.Dict[str, int | str]:
        '''
        Parses globals, creates new variables in the global namespace,
        the values are taken from already parsed kwargs
        
        Assigning values and registering shared ExManager objects
        is added to the oneliner list
        
        Returns associations, where each function argument corresponds
        to the name of a global variable

        :param sharedObjects: Shared ExManager objects, if set to None,
            it means that ExManager instance wasn't passed to RealProcess
            manager. So, there are no shared objects between processes
        :param useGlobal: Analogue of the global keyword, creates variables
            in the module's namespace
        :param useUUID: Names will be generated using UUID, which is
            useful for avoiding conflicts and overwriting existing values

        Creation of objects in the global namespace is done for clarity
        and to make parser debugging easier
        '''
        associations = {}

        if sharedObjects is not None:
            associations["__manager__"] = 3

        if useGlobal:
            moduleName = oneliner[0].split()[1]
        
        for kwargName, kwargValue in targetGlobals.items():
            if useUUID:
                varname = f"{uuid_to_varname(uuid.uuid4())}"
            else:
                varname = kwargName
            
            associations[kwargName] = varname

            if isinstance(kwargValue, tuple) and sharedObjects is not None:
                if kwargValue[1] not in sharedObjects.keys():
                    oneliner.insert(3, f"SyncManager.register('{kwargValue[0]}')")
                    associations["__manager__"] += 1
                if useGlobal:
                    oneliner.append(f"{moduleName}.{varname} = {kwargValue[2]}")
                else:
                    oneliner.append(f"{varname} = {kwargValue[2]}")
            else:
                if useGlobal:
                    oneliner.append(f"{moduleName}.{varname} = {kwargValue}")
                else:
                    oneliner.append(f"{varname} = {kwargValue}")

        return associations

    @staticmethod
    def oneliner_to_multiliner(oneliner: str) -> str:
        '''
        Just in case you need to read oneliner

        :param oneliner: RealProcess.oneliner to convert

        Returns a block of code from oneliner
        '''
        return oneliner_to_multiliner(oneliner)


class RealLock():
    '''
    Simple Lock implementation

    Sorry I'm tired XD
    '''
    def __init__(self):
        self._value = False
        self.accessCounter = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value:
            self.accessCounter += 1
        
            if self.accessCounter == 1:
                self._value = value
                self.accessCounter = 0
            else:
                self.acquire()
        else:
            self._value = value

    def __enter__(self):
        self.acquire()

    def __exit__(self):
        self.release()

    def acquire(self):
        while self.value:
            time.sleep(1)
        else:
            self.value = True

    def release(self):
        self.value = False

    def locked(self):
        return self.value


class RealEvent():
    '''
    Simple Event implementation
    '''
    def __init__(self):
        self.value = False

    def is_set(self):
        return self.value

    def set(self):
        self.value = True

    def clear(self):
        self.value = False

    def wait(self):
        while not self.value:
            time.sleep(1)


class ExQueue(Queue):
    '''
    Extended multiprocessing.Queue
    '''
    def __init__(self):
        super().__init__(maxsize=0, ctx=get_context())
    
    def put(self, obj, block=True, timeout=None, amount=1):
        '''
        Puts object into the queue and saves it to _lastObj variable,
        that is returned by get() and get_last(), in case if the queue is empty

        :param amount: Amount of times to put an object into the queue

        Updates counter used by wait() and wait_async()
        '''
        self._lastObj = obj
        for _ in range(amount):
            if hasattr(self, "counter"):
                self.counter.put(obj)
            super().put(obj, block, timeout)
    
    def get(self, block=True, timeout=None) -> typing.Any:
        '''
        Reads next object from the queue

        If queue is empty, then last putted value is returned
        '''
        if self.not_empty():
            return super().get(block, timeout)
        elif hasattr(self, "_lastObj"):
            return self._lastObj
        else:
            return None

    def get_last(self, block=True, timeout=None, shift: int=0) -> typing.Any:
        '''
        Reads entire queue and returns last object

        :param shift: Get last object from the end with shift

        If queue is empty, then last putted value is returned
        '''
        if self.not_empty():
            for _ in range(self.qsize()-1-shift):
                super().get(block, timeout)
            return self.get(block, timeout)
        elif hasattr(self, "_lastObj"):
            return self._lastObj
        else:
            return None

    def not_empty(self) -> bool:
        '''
        Missing function in multiprocessing.Queue
        Returns inverse value of Queue.empty()
        '''
        return self._poll()

    def to_list(self) -> typing.List[typing.Any]:
        '''
        Reads all objects from the queue and returns them as a list
        '''
        return [self.get() for _ in range(self.qsize())]
    
    def wait_init(self, counter: "ExQueue"):
        '''
        Multiprocessing attributes sync bug, because of underlying GIL threads
        https://stackoverflow.com/questions/11685936/why-am-i-getting-attributeerror-object-has-no-attribute

        So, use this function to synchronize counter between all processes

        :param counter: ExQueue object for counting
        '''
        self.counter = counter
    
    def _check_counter(self, message: str):
        '''
        Checks if the counter attribute exists
        If not, raises an AttributeError

        :param message: AttributeError message
        '''
        if not hasattr(self, "counter"):
            raise AttributeError(message)

    def wait(self, amount: int) -> typing.List[typing.Any]:
        '''
        Wait until a certain amount of objects are put into the queue

        :param amount: Amount of objects to wait

        Returns a list of objects putted into the queue during the wait()
        Objects are not removed from the parent queue
        '''
        self._check_counter("Call wait_init() before wait()")

        while self.counter.qsize() != amount:
            time.sleep(1)

        return self.counter.to_list()
    
    async def wait_async(self, amount: int) -> typing.List[typing.Any]:
        '''
        Wait until a certain amount of objects are put into the queue
        But asynchronously

        :param amount: Amount of objects to wait

        Returns a list of objects putted into the queue during the wait_async()
        Objects are not removed from the parent queue
        '''
        self._check_counter("Call wait_init() before wait_async()")

        while self.counter.qsize() != amount:
            await asyncio.sleep(0)

        return self.counter.to_list()

    def wait_reset(self):
        '''
        Reads all objects from counter, resetting it to zero thus

        Use this before wait() or wait_async(), if needed
        '''
        self._check_counter("Call wait_init() before wait_reset()")
        self.counter.get_last()
    
    def wait_end(self):
        '''
        Disables counter, after that you need to call wait_init() again if needed
        '''
        self._check_counter("Call wait_init() before wait_end()")
        delattr(self, "counter")


def current_realprocess() -> str:
    '''
    Returns name of the current RealProcess

    Can be: MainProcess or ChildProcess
    '''
    calledFrom = inspect.getmodule(inspect.stack()[1][0])
    
    if "__realprocess__" in calledFrom.__dict__:
        return "ChildProcess"
    else:
        return "MainProcess"
