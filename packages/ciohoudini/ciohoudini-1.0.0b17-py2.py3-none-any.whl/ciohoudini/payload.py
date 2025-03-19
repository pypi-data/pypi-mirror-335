import json
import hou

from ciohoudini import (
    job_title,
    project,
    instances,
    software,
    environment,
    driver,
    frames,
    task,
    assets,
    miscellaneous,
    render_rops,
    rops,
)

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def set_stats_panel(node, **kwargs):
    """Update the stats panel.

    Currently, only gets frames info, but will probably get other (non-payload) info like cost
    estimate. Example, when chunk size of frames change value.
    """
    frames.set_stats_panel(node, **kwargs)


def set_preview_panel(node, **kwargs):
    """Update the payload preview panel.

    Payload preview displays the JSON object that is submitted to Conductor. For optimization
    reasons, we don't always do a dependency scan or generate all tasks.

    User can set task_limit to -1 to see all tasks
    if user hits the display_assets button the assets list will include the result of a scan.
    """
    kwargs["task_limit"] = node.parm("display_tasks").eval()
    do_asset_scan = False
    if kwargs.get("parm_name") == "do_asset_scan":
        do_asset_scan = True
    kwargs["do_asset_scan"] = do_asset_scan
    try:
        payload = resolve_payload(node, **kwargs)
        if payload and len(payload) > 0:
            node.parm("payload").set(json.dumps(payload, indent=2))
        else:
            node.parm("payload").set("Unable to generate payload.")
    except Exception as e:
        node.parm("payload").set("Error generating payload: {}".format(e))



def refresh_lop_network():
    # Get the LOP Network object
    lop_network = hou.node("/stage")

    # Force a cook to refresh the LOP network
    lop_network.cook(force=True)


def resolve_payload(node, **kwargs):
    # set_stats_panel(node, **kwargs)
    # Get the payload for the current node.
    payload_list = []
    if not node:
        return payload_list
    try:
        node_type = rops.get_node_type(node)
        node_list = rops.get_node_list("multi_rop")
        # Multi rop nodes
        if node_type in node_list:
            render_rop_data = render_rops.get_render_rop_data(node)
            do_asset_scan = kwargs.get("do_asset_scan", False)
            if not render_rop_data:
                return None
            # Refresh the LOP network
            refresh_lop_network()

            # Get the payload for each rop.
            for render_rop in render_rop_data:
                frame_range = render_rop.get("frame_range", None)
                kwargs["frame_range"] = frame_range
                rop_path = render_rop.get("path", None)
                kwargs["rop_path"] = rop_path
                payload = get_payload(node, **kwargs)
                if payload:
                    payload_list.append(payload)
        # Single rop nodes
        else:
            if node_type not in ["generator"]:
                # logger.debug("Getting payload for node of type: ", node_type)
                rop_path = None
                if node_type not in ["husk"]:
                    rop_path = node.parm("driver_path").evalAsString()
                kwargs["rop_path"] = rop_path

                payload = get_payload(node, **kwargs)
                if payload:
                    payload_list.append(payload)

            # Generator nodes
            else:
                # logger.debug("Getting payload for generator node.")
                payload_list = get_generator_payload(node, **kwargs)
    except Exception as e:
        logger.error("Error resolving payload: {}".format(e))

    return payload_list


def get_generator_payload(node, **kwargs):
    """
    Generates payloads for the render ROPs attached to the generator node.

    Args:
        node (hou.Node): The Houdini node containing render ROPs.
        **kwargs: Additional parameters for payload generation.

    Returns:
        list: A list of payload dictionaries.
    """
    try:
        render_rops_data = render_rops.get_render_rop_data(node)
        # logger.debug(f"Render ROP data: {render_rops_data}")
        if not render_rops_data:
            # logger.debug("No render ROP data found.")
            return None

        # Refresh the LOP network
        refresh_lop_network()

        # Find the subnet attached to the node
        connected_subnet = None
        try:
            for input_node in node.outputs():
                if input_node and input_node.type().name() == "subnet":
                    connected_subnet = input_node
                    # logger.debug(f"Found subnet: {connected_subnet.name()}")
                    break
        except Exception as e:
            logger.debug(f"Error while checking for connected subnets: {e}")
            return None

        if not connected_subnet:
            # logger.debug("No subnet is attached to the node. Please attach a subnet before proceeding.")
            return None

        # logger.debug(f"Using attached subnet: {connected_subnet.name()}")

        # Get the payload for each ROP
        payload_list = []

        for render_rop in render_rops_data:
            try:
                rop_path = render_rop.get("path", None)
                # logger.debug(f"Processing render ROP: {rop_path}")
                frame_range = render_rop.get("frame_range", None)
                if not rop_path:
                    # logger.debug("Skipping render ROP with no path.")
                    continue

                # Extract the ROP name from the path (e.g., "/stage/usdrender_rop1" -> "usdrender_rop1")
                rop_name = rop_path.split("/")[-1]

                # Look for the conductor node inside the attached subnet
                conductor_node_name = f"conductor_{rop_name}"
                conductor_node = connected_subnet.node(conductor_node_name)

                if conductor_node:
                    # logger.debug(f"Found conductor node: {conductor_node_name} in subnet: {connected_subnet.name()}")

                    # Prepare kwargs and call get_payload
                    kwargs["frame_range"] = frame_range
                    kwargs["rop_path"] = rop_path


                    try:
                        payload = get_payload(conductor_node, **kwargs)
                        if payload:
                            payload_list.append(payload)
                    except Exception as e:
                        logger.debug(f"Error while generating payload for conductor node {conductor_node_name}: {e}")
                else:
                    logger.debug(f"Conductor node {conductor_node_name} not found in subnet {connected_subnet.name()}.")

            except Exception as e:
                logger.debug(f"Error while processing render ROP: {e}")

        return payload_list

    except Exception as e:
        logger.debug(f"Error in get_generator_payload: {e}")
        return None


def get_payload(node, **kwargs):
    payload = {}

    if not node:
        return None

    #kwargs["do_asset_scan"] = True
    #do_asset_scan = rops.get_parameter_value(node, "do_asset_scan")
    # kwargs["do_asset_scan"] = do_asset_scan
    rop_path = kwargs.get("rop_path", None)
    frame_range = kwargs.get("frame_range", None)
    if not frame_range:
        frame_range = node.parm("frame_range").evalAsString()
        kwargs["frame_range"] = frame_range
    #logger.debug("Getting payload for node: {} and rop: {}".format(node.path(), rop_path))
    payload.update(job_title.resolve_payload(node, rop_path=rop_path))
    payload.update(project.resolve_payload(node))
    payload.update(instances.resolve_payload(node))
    payload.update(software.resolve_payload(node))
    payload.update(environment.resolve_payload(node))
    # Get the payload for the driver using the rop path.
    payload.update(render_rops.resolve_payload(node, rop_path))
    payload.update(miscellaneous.resolve_payload(node))
    payload.update(frames.resolve_payload(node, frame_range=frame_range))
    # Get the payload for the assets using the rop path and frame range.
    payload.update(task.resolve_payload(node, **kwargs))
    payload.update(assets.resolve_payload(node, **kwargs))


    return payload




