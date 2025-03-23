"""
----------------------------------------------------------------------------

   METADATA:

       File:    manager.py
        Project: paperap
       Created: 2025-03-04
        Version: 0.0.7
       Author:  Jess Mann
       Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

   LAST MODIFIED:

       2025-03-04     By Jess Mann

"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Self, Set, TypedDict

import pydantic

from paperap.client import PaperlessClient
from paperap.plugins.base import Plugin

logger = logging.getLogger(__name__)


class PluginConfig(TypedDict):
    """
    Configuration settings for a plugin.
    """

    enabled_plugins: list[str]
    settings: dict[str, Any]


class PluginManager(pydantic.BaseModel):
    """Manages the discovery, configuration and initialization of plugins."""

    plugins: dict[str, type[Plugin]] = {}
    instances: dict[str, Plugin] = {}
    config: PluginConfig = {
        "enabled_plugins": [],
        "settings": {},
    }
    client: PaperlessClient

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        validate_default=True,
        validate_assignment=True,
    )

    @property
    def enabled_plugins(self) -> list[str]:
        """
        Get the list of enabled plugins.

        Returns:
            List of enabled plugin names

        """
        # TODO: There's a bug here... disabling every plugin will then enable every plugin
        if enabled := self.config.get("enabled_plugins"):
            return enabled

        return list(self.plugins.keys())

    def discover_plugins(self, package_name: str = "paperap.plugins") -> None:
        """
        Discover available plugins in the specified package.

        Args:
            package_name: Dotted path to the package containing plugins.

        """
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.warning("Could not import plugin package: %s", package_name)
            return

        # Find all modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if is_pkg:
                # Recursively discover plugins in subpackages
                self.discover_plugins(module_name)
                continue

            try:
                module = importlib.import_module(module_name)

                # Find plugin classes in the module
                for _name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Plugin) and obj is not Plugin and obj.__module__ == module_name:
                        plugin_name = obj.__name__
                        self.plugins[plugin_name] = obj
                        logger.debug("Discovered plugin: %s", plugin_name)
            except Exception as e:
                logger.error("Error loading plugin module %s: %s", module_name, e)

    def configure(self, config: PluginConfig | None = None, **kwargs) -> None:
        """
        Configure the plugin manager with plugin-specific configurations.

        Args:
            config: dictionary mapping plugin names to their configurations.

        """
        if config:
            self.config = config

        if kwargs:
            if enabled_plugins := kwargs.pop("enabled_plugins", None):
                self.config["enabled_plugins"] = enabled_plugins
            if settings := kwargs.pop("settings", None):
                self.config["settings"] = settings
            if kwargs:
                logger.warning("Unexpected configuration keys: %s", kwargs.keys())

    def get_plugin_config(self, plugin_name: str) -> dict[str, Any]:
        """Get the configuration for a specific plugin."""
        return self.config["settings"].get(plugin_name, {})

    def initialize_plugin(self, plugin_name: str) -> Plugin | None:
        """
        Initialize a specific plugin.

        Args:
            plugin_name: Name of the plugin to initialize.

        Returns:
            The initialized plugin instance or None if initialization failed.

        """
        if plugin_name in self.instances:
            return self.instances[plugin_name]

        if plugin_name not in self.plugins:
            logger.warning("Plugin not found: %s", plugin_name)
            return None

        plugin_class = self.plugins[plugin_name]
        plugin_config = self.get_plugin_config(plugin_name)

        try:
            # Initialize the plugin with plugin-specific config
            plugin_instance = plugin_class(manager=self, **plugin_config)
            self.instances[plugin_name] = plugin_instance
            logger.info("Initialized plugin: %s", plugin_name)
            return plugin_instance
        except Exception as e:
            # Do not allow plugins to interrupt the normal program flow.
            logger.error("Failed to initialize plugin %s: %s", plugin_name, e)
            return None

    def initialize_all_plugins(self) -> dict[str, Plugin]:
        """
        Initialize all discovered plugins.

        Returns:
            Dictionary mapping plugin names to their initialized instances.

        """
        # Get enabled plugins from config
        enabled_plugins = self.enabled_plugins

        # Initialize plugins
        initialized = {}
        for plugin_name in enabled_plugins:
            instance = self.initialize_plugin(plugin_name)
            if instance:
                initialized[plugin_name] = instance

        return initialized
