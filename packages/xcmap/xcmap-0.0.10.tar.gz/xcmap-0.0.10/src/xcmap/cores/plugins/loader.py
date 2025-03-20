from importlib_metadata import entry_points
from typing import Iterable, Type, Dict
from xcmap.cores.plugins.interface import PluginProtocol


class PluginLoader:
    def __init__(self, group: str = "banyan.plugins"):
        self.group = group
        self._plugins: dict[str, Type[PluginProtocol]] = {}

    def discover(self) -> None:
        """发现所有可用插件"""
        try:
            eps = entry_points(group=self.group)
        except Exception as e:
            raise RuntimeError(f"Entry points loading failed: {str(e)}") from e

        for ep in eps:
            try:
                plugin_cls: Type[PluginProtocol] = ep.load()
                if not isinstance(plugin_cls, type):
                    raise TypeError(f"Invalid plugin type: {ep.name}")

                # 创建临时实例并检查协议
                temp_instance = plugin_cls()
                if not isinstance(temp_instance, PluginProtocol):
                    raise TypeError(f"Plugin {ep.name} does not conform to protocol")

                self._plugins[ep.name] = plugin_cls
            except (ImportError, AttributeError, TypeError) as e:
                print(f"Skipping invalid plugin {ep.name}: {str(e)}")

    def get_plugin(self, name: str) -> tuple[str, PluginProtocol]:
        """获取插件实例"""
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} not found")
        cls_obj = self._plugins[name]()
        return cls_obj.__module__.split(".")[0], cls_obj

    def get_all_plugins(self) -> dict[str, PluginProtocol]:
        """获取所有插件实例"""
        return {key: cls() for key, cls in self._plugins.items()}
