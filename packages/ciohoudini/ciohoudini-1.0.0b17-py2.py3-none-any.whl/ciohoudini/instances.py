"""Manage instance_type menu."""

from ciocore import data as coredata
from ciohoudini import rops


import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def _get_instance_types(node):
    family = node.parm("instance_type_family").eval()
    instances = coredata.data()["instance_types"]
    if instances:
        instances = instances.instance_types.values()
        # logger.debug("instances", instances)
        return [item for item in instances if _is_family(item, family)]
    else:
        return []


def _is_family(item, family):
    return ((family == "gpu") and item.get("gpu")) or ((family == "cpu") and not item.get("gpu"))



def populate_menu(node):
    """Populate instance type menu.

    Get list of items from the shared coredata.
    The menu expects a flat array: [k, v, k,
    v ....]
    """

    if not coredata.valid():
        return ["not_connected", "-- Not Connected --"]
    ensure_valid_selection(node)
    return [el for item in _get_instance_types(node) for el in (item["name"], item["description"])]


def ensure_valid_selection(node, **kwargs):
    """
    If connected, ensure the value of this parm is valid.
    """
    if not coredata.valid():
        return

    selected = node.parm("instance_type").eval()  # key

    names = [i["name"] for i in _get_instance_types(node)]

    if not names:
        node.parm("instance_type").set("no_instance_types")
        return
    if selected in names:
        node.parm("instance_type").set(selected)
    else:
        node.parm("instance_type").set(names[0])


def resolve_payload(node):
    preemptible = False
    preemptible_check = rops.get_parameter_value(node, "preemptible")
    cw_connection = rops.get_parameter_value(node, "cw_connection")
    if preemptible_check and cw_connection == 1:
        preemptible = True

    result = {
        "instance_type": node.parm("instance_type").eval(),
        "preemptible": preemptible
    }

    retries = rops.get_parameter_value(node, "retries")
    if (preemptible and retries > 0):
        result["autoretry_policy"] = {  "preempted": {"max_retries": retries}}
    
    return result
