from ...connection_hub import ConnectionHub
from ..classes import Property, Service


class AnalyserService(Service):

    def __init__(self, connection_hub: ConnectionHub):
        super().__init__(connection_hub)
        self.add_property("oscillation", OscillationProperty(self.hub))
        self.add_property("activity", ActivityProperty(self.hub))


class OscillationProperty(Property[list[int, int]]):

    async def on_callback(self, args):
        value = args[0]["value"]
        self.set(value, push=False)
        await self.notify_listeners(value)

    def __init__(self, parent: Service):
        super().__init__(parent)
        self.value = [0, 0]

    def pull(self):
        self.hub.send_serialized_data("GetOscillation")

    def register(self):
        self.hub.client.on("GetOscillationCallback", self.on_callback)


class ActivityProperty(Property[int]):

    async def on_callback(self, args):
        value = args[0]["value"]
        self.set(value, push=False)
        await self.notify_listeners(value)

    def __init__(self, parent: Service):
        super().__init__(parent)
        self.value = 0

    def pull(self):
        self.hub.send_serialized_data("GetActivity")

    def register(self):
        self.hub.client.on("GetActivityCallback", self.on_callback)
