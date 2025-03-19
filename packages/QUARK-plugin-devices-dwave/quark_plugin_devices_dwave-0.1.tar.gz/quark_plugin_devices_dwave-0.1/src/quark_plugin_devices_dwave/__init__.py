from quark.plugin_manager import factory

from quark_plugin_devices_dwave.simulated_annealer import SimulatedAnnealer

def register() -> None:
    factory.register("simulated_annealer", SimulatedAnnealer)
