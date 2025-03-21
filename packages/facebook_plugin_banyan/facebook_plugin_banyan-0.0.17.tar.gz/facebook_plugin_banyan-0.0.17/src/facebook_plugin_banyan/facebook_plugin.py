from datetime import datetime

from xcmap.cores.plugins.interface import PluginProtocol


class AccountPromotionPlugin(PluginProtocol):
    def initialize(self, config: dict) -> None:
        pass

    def execute(self, *args, **kwargs) -> dict:
        if args:
            print(f'this is 0.0.17 -> {args[0]}')
        return {
            "timestamp": datetime.now().isoformat(),
            "message": "Hello from demo plugin"
        }

