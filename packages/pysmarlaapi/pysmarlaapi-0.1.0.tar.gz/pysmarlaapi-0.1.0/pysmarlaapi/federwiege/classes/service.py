from ...connection_hub import ConnectionHub
from .property import Property


class Service:

    async def on_connection_change(self, value):
        if value:
            self.sync()

    def __init__(self, connection_hub: ConnectionHub):
        self.hub = connection_hub
        self.registered = False
        self.props: dict[str, Property] = {}

    def add_property(self, key: str, prop: Property):
        self.props[key] = prop

    def get_properties(self):
        return self.props

    def get_property(self, key: str):
        return self.props[key]

    def register(self):
        for prop in self.props.values():
            prop.register()
        self.hub.add_listener(self.on_connection_change)
        self.registered = True

    def sync(self):
        for prop in self.props.values():
            prop.pull()
