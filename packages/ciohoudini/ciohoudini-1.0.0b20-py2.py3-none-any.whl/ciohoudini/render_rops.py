import hou

import os

from ciohoudini import (
    driver,
    frames,
    rops,
)
import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def add_one_render_rop(rop, node, next_index, network, render_rops_dict=None):
    """Add a render rop to the ui."""
    if not rop:
        return None
    try:
        rop_checkbox = True
        rop_path = rop.path() or "/{}/{}".format(network, rop.name())
        # logger.debug("Adding rop: {} at index: {}".format(rop_path, next_index))

        if rop.type().name() == 'usdrender_rop':
            #rop_frame_range = "{}-{}".format(int(rop.parm("f1").eval()), int(rop.parm("f2").eval()))
            rop_frame_range = frames.get_all_rop_frame_range(node, rop_path)
        else:
            #rop_frame_range = node.parm("frame_range").eval()
            rop_frame_range = frames.get_all_rop_frame_range(node, rop_path)

        if rop_path and render_rops_dict:
            key = rop_path.replace("/", "")
            if key in render_rops_dict:
                rop_frame_range = render_rops_dict[key].get('frame_range', '1-1')
                rop_checkbox = render_rops_dict[key].get('rop_checkbox', True)
                # logger.debug("Stored frame range: {}".format(rop_frame_range))

        # logger.debug("Adding rop frame range: {}".format(rop_frame_range))

        render_rops_parm = node.parm("render_rops")
        if render_rops_parm:
            render_rops_parm.set(next_index)

        rop_checkbox_parm = node.parm("rop_checkbox_{}".format(next_index))
        if rop_checkbox_parm:
            rop_checkbox_parm.set(rop_checkbox)

        rop_path_parm = node.parm("rop_path_{}".format(next_index))
        if rop_path_parm:
            rop_path_parm.set(rop_path)

        rop_frame_range_parm = node.parm("rop_frame_range_{}".format(next_index))
        if rop_frame_range_parm:
            rop_frame_range_parm.set(rop_frame_range)
    except Exception as e:
        logger.error("Error adding rop: {}".format(e))


def get_render_rop_data(node):
    """Get the render rop data from the UI."""
    render_rops_data = []
    try:
        if node.parm("render_rops"):
            for i in range(1, node.parm("render_rops").eval() + 1):
                if node.parm("rop_checkbox_{}".format(i)).eval():
                    render_rops_data.append({
                        "path": node.parm("rop_path_{}".format(i)).evalAsString(),
                        "frame_range": node.parm("rop_frame_range_{}".format(i)).evalAsString(),
                        # "use_scout_frames": node.parm("rop_use_scout_frames_{}".format(i)).eval(),
                    })
    except Exception as e:
        logger.error("Error getting render rop data: {}".format(e))
    return render_rops_data

def store_current_render_rop_data(node):
    """Store the current render rop data in the UI."""
    render_rops_dict = {}
    for i in range(1, node.parm("render_rops").eval() + 1):
        path = node.parm("rop_path_{}".format(i)).evalAsString()
        if path:
            key = path.replace("/", "")
            if key not in render_rops_dict:
                render_rops_dict[key] = {}
                render_rops_dict[key]["rop_checkbox"] = node.parm("rop_checkbox_{}".format(i)).eval()
                render_rops_dict[key]["frame_range"] = node.parm("rop_frame_range_{}".format(i)).evalAsString()
                # render_rops_dict[key]["use_scout_frames"] = node.parm("rop_use_scout_frames_{}".format(i)).eval()

    return render_rops_dict



def add_render_ropes(node, render_rops_dict=None):
    """
    Add all render rops to the UI.
    Currently only supports driver rop (out network)
    and usdrender_rop nodes (Stage network).
    """
    try:
        next_index = 1
        # Add the driver rop if it exists
        driver_rop = driver.get_driver_node(node)
        if driver_rop:
            # logger.debug("driver_rop: {}".format(driver_rop.name()))
            # Add the driver rop to the UI
            add_one_render_rop(driver_rop, node, next_index, "out", render_rops_dict=render_rops_dict)
        # Add all the render rops in the stage
        render_ropes = get_stage_render_rops()
        if render_ropes:
            for rop in render_ropes:
                render_ropes_param = node.parm("render_rops")
                if render_ropes_param:
                    next_index = render_ropes_param.eval() + 1

                # logger.debug("Adding rop: {}".format(rop.name()))
                # Add the rop to the UI
                add_one_render_rop(rop, node, next_index, "stage", render_rops_dict=render_rops_dict)
    except Exception as e:
        logger.error("Error adding render rops: {}".format(e))


def get_stage_render_rops():
    """ Create a list all usdrender_rop nodes in the stage """
    stage_render_ropes = []
    stage_node_list = hou.node('/stage').allSubChildren()

    # logger.debug("Stage nodes:")
    for rop in stage_node_list:
        if rop:
            if rop.type().name() == 'usdrender_rop':
                if rop.isBypassed() is False:
                    stage_render_ropes.append(rop)
                    # logger.debug(rop.name())
    return stage_render_ropes


def remove_rop_row(node):
    """Remove a variable from the UI.

    Remove the entry at the given index and shift all subsequent entries down.
    """
    curr_count = node.parm("render_rops").eval()
    node.parm("rop_checkbox_{}".format(curr_count)).set(False)
    node.parm("rop_path_{}".format(curr_count)).set("")
    node.parm("rop_frame_range_{}".format(curr_count)).set("")
    # node.parm("rop_use_scout_frames_{}".format(curr_count)).set(False)
    node.parm("render_rops").set(curr_count - 1)

def remove_all_rop_rows(node):
    """Remove all the render rop rows from the UI."""
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm("rop_checkbox_{}".format(i)).set(False)
        node.parm("rop_path_{}".format(i)).set("")
        node.parm("rop_frame_range_{}".format(i)).set("")
        # node.parm("rop_use_scout_frames_{}".format(i)).set(False)
    node.parm("render_rops").set(0)


def select_all_render_rops(node, **kwargs):
    """Select all the render rops in the UI."""
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm("rop_checkbox_{}".format(i)).set(True)


def deselect_all_render_rops(node, **kwargs):
    """Deselect all the render rops in the UI."""
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm("rop_checkbox_{}".format(i)).set(False)


def reload_render_rops(node, **kwargs):
    """Reload the render rop data from the UI."""

    # Remove all the render rops rows from the UI
    remove_all_rop_rows(node)
    # Add all the render rops to the UI
    add_render_ropes(node, render_rops_dict=None)

def update_render_rops(node, **kwargs):
    """Update the render rop data from the UI."""

    render_rops_dict = store_current_render_rop_data(node)
    # Remove all the render rops rows from the UI
    remove_all_rop_rows(node)
    # Add all the render rops to the UI
    add_render_ropes(node, render_rops_dict=render_rops_dict)


def apply_script_to_all_render_rops(node, **kwargs):
    """Apply the given script to all render rops."""
    script = node.parm("override_image_output").evalAsString()
    # logger.debug("script: {}".format(script))

    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        rop_path = node.parm("rop_path_{}".format(i)).evalAsString()
        driver.apply_image_output_script(rop_path, script)


def resolve_payload(node, rop_path=None):
    """Resolve the output path for the given node."""

    output_path = ""
    try:
        # output_path = node.parm('output_folder').eval()
        output_path = rops.query_output_folder(node, rop_path=rop_path)
        output_path = os.path.expandvars(output_path)
        if output_path and not os.path.exists(output_path):
            os.makedirs(output_path)
        # logger.debug("Output path: {}".format(output_path))
    except Exception as e:
        logger.debug("Unable to set output dir. ", e)


    return {"output_path": output_path}
