"""
Manage 3 software categories:

1. Remote Houdini version.
2. Plugin for the connected driver.
3. Extra plugins.


"""

import hou

from ciocore import data as coredata
from ciohoudini import driver, rops

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def populate_host_menu_original(node):
    """Populate houdini version menu.

    This is called by the UI whenever the user clicks the Houdini Version button.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()

    # hostnames will have the platform specifier (houdini 19.0 linux). We want to strip the platform.
    # logger.debug("host_names 1: {}".format(host_names))
    # logger.debug("host_names 2: {}".format([el for i in host_names for el in (i," ".join(i.split()[:2]).capitalize() )]))
    return [el for i in host_names for el in (i," ".join(i.split()[:2]).capitalize() )]

def version_distance(host, current_version_parts):
    """
    Calculate the distance between the current Houdini version and a host version.

    :param host: A host name string from the host_names list.
    :param current_version_parts: A list of integers representing the current version [major, minor, build].
    :return: A numerical distance value (lower is better).
    """
    try:
        # Extract the version part from the host string
        # Example host: "houdini 20.5.370.gcc9.3 linux"
        host_version = host.split(" ")[1].split(".gcc")[0]  # Extract "20.5.370"
        host_version_parts = list(map(int, host_version.split(".")))  # Example: [20, 5, 370]

        # Compute the distance based on absolute difference for each component
        major_diff = abs(current_version_parts[0] - host_version_parts[0]) * 1000000
        minor_diff = abs(current_version_parts[1] - host_version_parts[1]) * 1000
        build_diff = abs(current_version_parts[2] - host_version_parts[2])

        # Total distance
        total_distance = major_diff + minor_diff + build_diff

        # Debug: logger.debug calculation details
        # logger.debug(f"Comparing with host: {host}")
        # logger.debug(f"  Host version parts: {host_version_parts}")
        # logger.debug(f"  Current version parts: {current_version_parts}")
        # logger.debug(f"  Major diff: {major_diff}, Minor diff: {minor_diff}, Build diff: {build_diff}")
        # logger.debug(f"  Total distance: {total_distance}")

        return total_distance
    except (IndexError, ValueError) as e:
        logger.debug(f"Error parsing host version: {host}. Error: {e}")
        return float('inf')  # If parsing fails, assign a large distance

def find_closest_host_version(node, host_names):
    """
    Find the closest host version to the current Houdini version.
    """
    find_closest_version = rops.get_parameter_value(node, "find_closest_version")
    if find_closest_version == 1:

        try:

            # Debug: Output the full list of host names
            # logger.debug("host_names (raw):", host_names)

            # Get the current Houdini version
            current_version = hou.applicationVersionString()  # Example: "20.0.751"

            # Parse the version into components for comparison
            current_version_parts = list(map(int, current_version.split(".")))  # Example: [20, 0, 751]

            # Debug: logger.debug current version details
            # logger.debug(f"Current Houdini version: {current_version}")
            # logger.debug(f"Current version parts: {current_version_parts}")

            # Find the closest version in the host_names list
            matching_host = min(
                host_names,
                key=lambda host: version_distance(host, current_version_parts)
            )

            # Debug: Output the selected host
            # logger.debug("Selected host:", matching_host)

            # Set the node parameter with the selected host
            rops.set_parameter_value(node, "host_version", matching_host)
            #Set the find_closest_version to 0
            rops.set_parameter_value(node, "find_closest_version", 0)

        except Exception as e:
            logger.debug(f"Error selecting host version: {e}")


def populate_host_menu(node):
    """
    Populate Houdini version menu.

    This is called by the UI whenever the user clicks the Houdini Version button.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()

    find_closest_host_version(node, host_names)

    # Format the menu for UI
    return [el for host in host_names for el in (host, host.capitalize())]



def populate_driver_menu(node):
    """Populate renderer/driver type menu.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    return [el for i in _get_compatible_plugin_versions(node) for el in (i,i)]
    """
    plugin_versions = [el for i in _get_all_plugin_versions(node) for el in (i, i)]
    plugin_versions.append(("built-in: karma-houdini", "built-in: karma-houdini"))
    return plugin_versions
    """



def populate_extra_plugin_menu(node):
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    #_get_all_plugin_versions
    return [el for i in _get_all_plugin_versions(node) for el in (i,i)]


def set_plugin(node):
    """
    If connected, ensure the value of this parm is valid.
    """
    if not coredata.valid():
        return

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()

    if selected_host not in host_names:
        selected_host = host_names[-1]

        node.parm("host_version").set(selected_host)

    # update_driver_selection(node)
    # update_plugin_selections(node)

    driver_names = _get_compatible_plugin_versions(node)
    logger.debug("set_plugin: driver_names: {}".format(driver_names))

    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return

    selected_driver = node.parm('driver_version').eval()
    logger.debug("set_plugin: selected_driver: {}".format(selected_driver))

    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]
    logger.debug("set_plugin: selected_driver: {}".format(selected_driver))
    node.parm('driver_version').set(selected_driver)


def ensure_valid_selection(node):
    """
    If connected, ensure the value of this parm is valid.
    """
    if not coredata.valid():
        return

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()

    if not host_names:
        node.parm("host_version").set("no_houdini_packages")
        node.parm('driver_version').set("no_drivers")
        num_plugins = node.parm("extra_plugins").eval()
        for i in range(1, num_plugins+1):
            node.parm("extra_plugin_{}".format(i)).set("no_plugins")
        return

    if selected_host not in host_names:
        selected_host = host_names[-1]
    
    node.parm("host_version").set(selected_host)
    
    update_driver_selection(node)
    update_plugin_selections(node)


    driver_names = _get_compatible_plugin_versions(node)
    # logger.debug("ensure_valid_selection: driver_names: {}".format(driver_names))


    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return

    selected_driver = node.parm('driver_version').eval()
    # logger.debug("ensure_valid_selection: selected_driver: {}".format(selected_driver))

    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]
    # logger.debug("ensure_valid_selection: selected_driver: {}".format(selected_driver))
    node.parm('driver_version').set(selected_driver)


def _get_compatible_plugin_versions(node):
    
    driver_data = driver.get_driver_data(node)
    if not driver_data:
        return ["No drivers available"]
    conductor_product = driver_data.get("conductor_product", None)
    if not conductor_product:
        return ["No conductor products available"]

    if conductor_product.lower().startswith(("built-in", "unknown")):
        return [driver_data["conductor_product"]]

    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)
    plugin_names = [plugin["plugin"] for plugin in plugins]

    if driver_data["conductor_product"] not in plugin_names:
        return ["No plugins available for {}".format(driver_data["conductor_product"])]

    plugin_versions = []
    for plugin in plugins:
        if plugin["plugin"] == driver_data["conductor_product"]:
            for version in plugin["versions"]:
                plugin_versions.append("{} {}".format(
                    plugin["plugin"], version))
            break
    # logger.debug("plugin_versions: {}".format(plugin_versions))
    return plugin_versions



def _get_all_plugin_versions(node):
    
    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)

    plugin_versions = []
    for plugin in plugins:
        for version in plugin["versions"]:
            plugin_versions.append("{} {}".format(
                plugin["plugin"], version))

    return plugin_versions

def update_driver_selection(node, **kwargs):

    selected_plugin = node.parm('driver_version').eval()
    # logger.debug("selected_plugin: {}".format(selected_plugin))
    plugin_names = _get_compatible_plugin_versions(node)
    # logger.debug("1: plugin_names: {}".format(plugin_names))
    if not plugin_names:
         node.parm('driver_version').set("no_plugins_available")
         return

    if selected_plugin not in plugin_names:
        # logger.debug("Setting driver version to: {}".format(plugin_names[0]))
        node.parm('driver_version').set(plugin_names[0])

def update_plugin_selections(node, **kwargs):

    try:
        plugin_names = _get_all_plugin_versions(node)
        # logger.debug("2: plugin_names: {}".format(plugin_names))
        extra_plugins = node.parm("extra_plugins")
        if extra_plugins:
            num_plugins = node.parm("extra_plugins").eval()
            for i in range(1, num_plugins+1):
                parm = node.parm("extra_plugin_{}".format(i))
                selected_plugin = parm.eval()
                if not plugin_names:
                    parm.set("no_plugins_available")
                    continue
                if selected_plugin not in plugin_names:
                    logger.debug("setting plugin to: {}".format(plugin_names[0]))
                    parm.set(plugin_names[0])
        else:
            logger.debug("No extra plugins parm found.")
    except Exception as e:
        logger.error("Error updating extra plugins: {}".format(e))


def resolve_payload(node):
    """Resolve the package IDs section of the payload for the given node."""
    ids = set()
 
    for package in packages_in_use(node):
        ids.add(package["package_id"])

    return {"software_package_ids": list(ids)}

def packages_in_use(node):
    """Return a list of packages as specified by names in the software dropdowns.
    """
    if not coredata.valid():
        return []
    tree_data = coredata.data().get("software")
    if not tree_data:
        return []

    platform = list(coredata.platforms())[0]
    host = node.parm("host_version").eval()
    driver = "{}/{} {}".format(host, node.parm("driver_version").eval(), platform)
    paths = [host, driver]

    num_plugins_param = node.parm("extra_plugins")
    if num_plugins_param:
        num_plugins = num_plugins_param.eval()
        for i in range(1, num_plugins+1):
            parm = node.parm("extra_plugin_{}".format(i))
            if parm:
                paths.append("{}/{} {}".format(host, parm.eval(), platform))

    return list(filter(None, [tree_data.find_by_path(path) for path in paths if path]))


def add_plugin(node, **kwargs):
    """Add a new variable to the UI.
    
    This is called by the UI when the user clicks the Add Variable button.
    """
    num_exist = node.parm("extra_plugins").eval()
    node.parm("extra_plugins").set(num_exist+1)
    update_plugin_selections(node)


def remove_plugin(node, index ):
    """Remove a variable from the UI.
    
    Remove the entry at the given index and shift all subsequent entries down.
    """
    curr_count =  node.parm("extra_plugins").eval()
    for i in range(index+1, curr_count+1):

        from_parm = node.parm("extra_plugin_{}".format(i))
        to_parm = node.parm("extra_plugin_{}".format(i-1))
        to_parm.set(from_parm.rawValue())
    node.parm("extra_plugins").set(curr_count-1)
