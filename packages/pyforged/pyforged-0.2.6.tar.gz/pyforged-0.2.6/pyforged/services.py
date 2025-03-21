"""
This module provides a service registry for managing the lifecycle of services in a Python application.
It includes functionality for registering services, factories, middleware, and health checks, as well as
injecting dependencies and managing service lifecycles.

**Classes:**
    - ServiceNotRegisteredException:
      Exception raised when a requested service is not registered.

    - ServiceInitializationException:
      Exception raised when a service fails to initialize.

    - ServiceRegistry:
      A registry for managing services, factories, middleware, and health checks.


**Functions:**
    - *check_all_services_health:*
      Checks the health of all registered services.

    - *periodic_health_check:*
      Periodically checks the health of all registered services.
"""

import inspect
import logging
import asyncio
from typing import Any, Callable, Dict, Type, Optional, Union, List
from threading import RLock

from pyforged.__errors__ import PyForgedException

logging.basicConfig(level=logging.INFO)

__all__ = [
    'ServiceRegistry',
    'ServiceInitializationException',
    'ServiceNotRegisteredException'
]


class ServiceNotRegisteredException(PyForgedException):
    """Exception raised when a requested service is not registered."""
    pass


class ServiceInitializationException(PyForgedException):
    """Exception raised when a service fails to initialize."""
    pass


class ServiceRegistry:
    """
    A registry for managing services, factories, middleware, and health checks.

    Attributes:
        _services (dict): A dictionary to store registered services.
        _factories (dict): A dictionary to store service factories.
        _singletons (dict): A dictionary to store singleton services.
        _aliases (dict): A dictionary to store service aliases.
        _lifecycle_hooks (dict): A dictionary to store lifecycle hooks for services.
        _lock (RLock): A reentrant lock for thread-safe operations.
        _middleware (dict): A dictionary to store middleware functions.
        _health_checks (dict): A dictionary to store health check functions.
        _service_versions (dict): A dictionary to store service versions.
        _service_metadata (dict): A dictionary to store service metadata.
        _scoped_services (dict): A dictionary to store scoped services.
    """

    def __init__(self):
        """Initializes a new instance of the ServiceRegistry class."""
        self._services = {}
        self._factories = {}
        self._singletons = {}
        self._aliases = {}
        self._lifecycle_hooks = {}
        self._lock = RLock()
        self._middleware = {'before_init': [],
                            'after_init': [],
                            'before_service_access': [],
                            'after_service_access': []
                            }
        self._health_checks = {}
        self._service_versions = {}
        self._service_metadata = {}
        self._scoped_services = {}

    def register(self, service_name: str, instance: Any, singleton: bool = False,
                 scope: Optional[str] = None, dependencies: Optional[List[str]] = None,
                 aliases: Optional[List[str]] = None, on_init: Optional[Callable] = None,
                 on_shutdown: Optional[Callable] = None, version: str = "1.0.0",
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Registers a service instance.

        Args:
            service_name (str): The name of the service.
            instance (Any): The service instance.
            singleton (bool, optional): Whether the service is a singleton. Defaults to False.
            scope (Optional[str], optional): The scope of the service. Defaults to None.
            dependencies (Optional[List[str]], optional): A list of dependencies. Defaults to None.
            aliases (Optional[List[str]], optional): A list of aliases for the service. Defaults to None.
            on_init (Optional[Callable], optional): A callback function to be called on initialization. Defaults to None.
            on_shutdown (Optional[Callable], optional): A callback function to be called on shutdown. Defaults to None.
            version (str, optional): The version of the service. Defaults to "1.0.0".
            metadata (Optional[Dict[str, Any]], optional): Metadata for the service. Defaults to None.
        """
        with self._lock:
            logging.info(f"Registering service: {service_name}")
            if singleton:
                self._singletons[service_name] = instance
            elif scope:
                self._scoped_services[service_name] = {'scope': scope, 'instance': instance}
            self._services[service_name] = instance
            self._lifecycle_hooks[service_name] = {'on_init': on_init, 'on_shutdown': on_shutdown}
            self._service_versions[service_name] = version
            self._service_metadata[service_name] = metadata or {}
            if aliases:
                for alias in aliases:
                    self._aliases[alias] = service_name
            if dependencies:
                for dependency in dependencies:
                    self.get(dependency)


    def register_factory(self, service_name: str, factory: Union[Callable[..., Any], Callable[..., asyncio.Future]],
                         singleton: bool = True, scope: Optional[str] = None, aliases: Optional[List[str]] = None,
                         on_init: Optional[Callable] = None, on_shutdown: Optional[Callable] = None,
                         version: str = "1.0.0", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Registers a service factory.

        Args:
            service_name (str): The name of the service.
            factory (Union[Callable[..., Any], Callable[..., asyncio.Future]]): The factory function.
            singleton (bool, optional): Whether the service is a singleton. Defaults to True.
            scope (Optional[str], optional): The scope of the service. Defaults to None.
            aliases (Optional[List[str]], optional): A list of aliases for the service. Defaults to None.
            on_init (Optional[Callable], optional): A callback function to be called on initialization. Defaults to None.
            on_shutdown (Optional[Callable], optional): A callback function to be called on shutdown. Defaults to None.
            version (str, optional): The version of the service. Defaults to "1.0.0".
            metadata (Optional[Dict[str, Any]], optional): Metadata for the service. Defaults to None.
        """
        with self._lock:
            logging.info(f"Registering factory for service: {service_name}")
            self._factories[service_name] = factory
            if singleton:
                self._singletons[service_name] = None
            elif scope:
                self._scoped_services[service_name] = {'scope': scope, 'instance': None}
            self._lifecycle_hooks[service_name] = {'on_init': on_init, 'on_shutdown': on_shutdown}
            self._service_versions[service_name] = version
            self._service_metadata[service_name] = metadata or {}
            if aliases:
                for alias in aliases:
                    self._aliases[alias] = service_name


    def middleware(self, hook_name: str, middleware_func: Callable[[Any], Any]) -> None:
        """
        Registers a middleware function for a specific hook.

        Args:
            hook_name (str): The name of the hook.
            middleware_func (Callable[[Any], Any]): The middleware function.
        """
        if hook_name in self._middleware:
            logging.info(f"Registering middleware for: {hook_name}")
            self._middleware[hook_name].append(middleware_func)


    async def get(self, service_name: str) -> Any:
        """
        Retrieves a service instance by name.

        Args:
            service_name (str): The name of the service.

        Returns:
            Any: The service instance.

        Raises:
            ServiceNotRegisteredException: If the service is not registered.
            ServiceInitializationException: If the service fails to initialize.
        """
        resolved_name = self._aliases.get(service_name, service_name)
        with self._lock:
            for hook in self._middleware['before_service_access']:
                hook(resolved_name)

            if resolved_name in self._singletons and self._singletons[resolved_name]:
                return self._singletons[resolved_name]

            if resolved_name in self._factories:
                try:
                    instance = self._factories[resolved_name]()
                    if asyncio.iscoroutine(instance):
                        instance = await instance
                    for hook in self._middleware['after_init']:
                        instance = hook(instance)
                    if self._lifecycle_hooks[resolved_name]['on_init']:
                        await self._lifecycle_hooks[resolved_name]['on_init'](instance)
                    if resolved_name in self._singletons:
                        self._singletons[resolved_name] = instance
                    return instance
                except Exception as e:
                    raise ServiceInitializationException(f"Failed to initialize service {resolved_name}") from e

            if resolved_name in self._services:
                return self._services[resolved_name]

        raise ServiceNotRegisteredException(f"Service {service_name} not registered.")

    async def shutdown(self) -> None:
        """
        Shuts down all services by calling their on_shutdown hooks.
        """
        with self._lock:
            for service_name, hooks in self._lifecycle_hooks.items():
                if hooks['on_shutdown'] and service_name in self._singletons:
                    result = hooks['on_shutdown'](self._singletons[service_name])
                    if asyncio.iscoroutine(result):
                        await result

    def check_health(self, service_name: str) -> bool:
        """
        Checks the health of a registered service.

        Args:
            service_name (str): The name of the service.

        Returns:
            bool: True if the service is healthy, False otherwise.

        Raises:
            ServiceNotRegisteredException: If the health check for the service is not registered.
        """
        with self._lock:
            if service_name in self._health_checks:
                return self._health_checks[service_name]()
            raise ServiceNotRegisteredException(f"Health check for service {service_name} not registered.")

    async def periodic_health_check(self, interval: int):
        """
        Periodically checks the health of all registered services.

        Args:
            interval (int): The interval in seconds between health checks.
        """
        while True:
            for service_name in self.list_services():
                try:
                    health_status = self.check_health(service_name)
                    logging.info(f"Health check for {service_name}: {'Healthy' if health_status else 'Unhealthy'}")
                except ServiceNotRegisteredException as e:
                    logging.error(e)
            await asyncio.sleep(interval)
