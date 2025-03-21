from quark.plugin_manager import factory

from quark_plugin_mis.mis_graph_provider import MisGraphProvider
from quark_plugin_mis.mis_qubo_mapping_dnx import MisQuboMappingDnx
from quark_plugin_mis.classical_mis_solver import ClassicalMisSolver

def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """
    factory.register("mis_graph_provider", MisGraphProvider)
    factory.register("mis_qubo_mapping_dnx", MisQuboMappingDnx)
    factory.register("classical_mis_solver", ClassicalMisSolver)
