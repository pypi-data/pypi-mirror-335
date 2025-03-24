import importlib.metadata
from typing import Tuple
def get_module_info() -> Tuple[str, str]:
    """
    Determine which client module is using this function and get its version.
    
    Returns:
        Tuple containing (module_name, module_version)
    """
    for module_name in ['lattica_deployer', 'lattica_query', 'lattica_management']:
        try:
            version = importlib.metadata.version(module_name)
            return module_name, version
        except importlib.metadata.PackageNotFoundError:
            continue
    
    # Default fallback if we can't determine the module
    return "unknown", "0.0.0"