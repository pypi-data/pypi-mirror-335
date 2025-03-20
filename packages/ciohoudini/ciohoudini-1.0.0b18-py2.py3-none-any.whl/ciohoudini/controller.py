"""
All communication with the HDA and routing is done through this module.
"""

import hou
import os
import re

from ciohoudini import (
    driver,
    instances,
    project,
    software,
    frames,
    environment,
    errors,
    context,
    assets,
    payload,
    submit,
    miscellaneous,
    render_rops,
    rops,
    create_usd,
)

from ciocore import data as coredata
import ciocore.loggeria
import ciocore.config
import ciocore.api_client
import ciohoudini.const as k

logger = ciocore.loggeria.get_conductor_logger()

ciocore.loggeria.setup_conductor_logging(log_filename="houdini_submitter.log")
ciocore.api_client.ApiClient.register_client(client_name="ciohoudini", client_version=k.VERSION)

# Set the task context to its current frame when frame changes. This is so that the user can copy
# the task, set to render the current frame, to the clipboard and then to run it locally in a shell.
# def currrentFrameContext(event_type, frame):
#     if event_type == hou.playbarEvent.FrameChanged:
#         context.set_for_task(first=frame,last=frame,step=1)

# hou.playbar.addEventCallback(currrentFrameContext)
# TURNED OFF FOR NOW.


fixtures_dir = os.path.expanduser(os.path.join("~", "conductor_fixtures"))
coredata.init("houdini")
coredata.set_fixtures_dir("")

# Set the task context to its default (first:1, last:1, step:1)
context.set_for_task()

MULTI_PARM_RE = re.compile(r"^([a-zA-Z0-9_]+_)\d+$")

# A list of parms that affect the payload. Only needed to update the payload panel. On submission,
# the payload is always regenerated.
AFFECTS_PAYLOAD = (
    "connect",
    "title",
    "project",
    "instance_type_family",
    "instance_type",
    "preemptible",
    "retries",
    "host_version",
    "driver_version",
    "chunk_size",
    "frame_range",
    "use_custom_frames",
    "use_scout_frames",
    "scout_frames",
    "rop_checkbox_",
    "rop_path_",
    "rop_frame_range_",
    "rop_use_scout_frames_",
    "add_hdas",
    "display_tasks",
    "do_asset_scan",
    "environment_kv_pairs",
    "env_key_",
    "env_value_",
    "env_excl_",
    "do_email",
    "email_addresses",
    "clear_all_assets",
    "browse_files",
    "browse_folder",
    "location_tag",
    "use_daemon",
    "add_variable",
    "add_existing_variable",
    "add_plugin",
    "extra_plugins",
    "extra_plugin_",
    "copy_script",
    "reload_render_rops",
    "update_render_rops",
    "apply_to_all_render_rops",
    "select_all_render_rops",
    "deselect_all_render_rops",
    "usd_filepath",
    "browse_usd_files",
    "driver_path",
    "override_image_output",
    "use_usd_scrapping_only",
    "driver_version",
    # "render_scene"

)


#: A dictionary of menu callbacks.
MENUS = {
    "instance_type": instances.populate_menu,
    "project": project.populate_menu,
    "host_version": software.populate_host_menu,
    "driver_version": software.populate_driver_menu,
    "frame_range_source": frames.populate_frame_range_menu,
    "extra_plugin_": software.populate_extra_plugin_menu,
    #"render_rop_list": rops.populate_render_rop_menu,
}

LOCK_ON_CREATE = ["asset_regex", "asset_excludes"]

# List of parms with expressions that need an event callback. in order to update the payload preview
# See on_loaded.
NEEDS_PAYLOAD_CALLBACK = ["output_folder", "render_script", "frame_range", "title", "rop_checkbox_",
    "rop_path_", "rop_frame_range_", "rop_use_scout_frames_", "driver_path", "override_image_output"]

def connect(node, **kwargs):
    """
    Connect to Conductor data.

    Get projects, hardware, software.
    """
    force = kwargs.get("force", True)
    try:

        try:
            coredata.data(force=force)
        except Exception as e:
            connection_failed(node)
            return
        project.ensure_valid_selection(node)
        instances.ensure_valid_selection(node)
        software.ensure_valid_selection(node)
        # node.parm("output_excludes").set(0)
        # rops.import_image_output(node)
        # node.parm("frame_range_source").set("Houdini playbar")
        # frames.update_render_rop_frame_range(node)
    except Exception as e:
        logger.error("Error connecting to Conductor: {}".format(e))

    if coredata.valid():
        rops.set_parameter_value(node, "is_connected", 1)

        hardware = coredata.data().get("instance_types")
        # Show preemptible if provider is not coreweave.
        if hardware.provider in ["cw"]:
            rops.set_parameter_value(node, "cw_connection", 1)
        else:
            rops.set_parameter_value(node, "cw_connection", 0)

    else:
        connection_failed(node)


def connection_failed(node):
    """
    Show a message window that the connection to Conductor failed.
    """
    hou.ui.displayMessage("Connection to Conductor failed. Please check your network connection and verify your credentials and try again.", severity=hou.severityType.Error)

def on_created(node, **kwargs):
    """Initialize state when a node is created.

    See on_loaded()
    """
    for parm in LOCK_ON_CREATE:
        node.parm(parm).lock(True)

    # Some default values don't seem to get set on creation. This is a hack to set them.
    node.parm("scout_frames").set("fml:3")
    preemptible_parm = node.parm("preemptible")
    if preemptible_parm:
        preemptible_parm.set(True)

    frame_range_source_parm = node.parm("frame_range_source")
    if frame_range_source_parm:
        frame_range_source_parm.set("Houdini playbar")

    frames.populate_frame_range_menu(node)
    frames.update_render_rop_frame_range(node, **kwargs)
    # rops.reset_render_rop_options(node)

    on_loaded(node, **kwargs)



def on_loaded(node, **kwargs):
    """Initialize state when a node is loaded.

    Steps:
        1. Parms with expressions do not trigger callbacks that are set up in the HDA parameter
           interface. Therefore we have to add them using addParmCallback in order to keep the stats
           panel and payload preview up to date.
        2. If coredata is valid (another node previously connected to Conductor), then we must
           ensure the values the projects, inst-types, and software string parms are valid according
           to the options in coredata before updating the preview node. Otherwise the menus
           might look valid, but the value could be "notset", and that would show up in
           the preview.
        3. Refresh the preview and stats panels.
    """
    kwargs["force"] = False
    node.addParmCallback(payload.set_preview_panel, NEEDS_PAYLOAD_CALLBACK)
    project.ensure_valid_selection(node)
    instances.ensure_valid_selection(node)
    software.ensure_valid_selection(node)
    # rops.import_image_output(node)

    node_type = rops.get_node_type(node)
    if node_type not in ["generator"]:
        payload.set_preview_panel(node, **kwargs)

    node.parm('log_label').set(ciocore.loggeria.LOG_PATH)


def check_connection(node, **kwargs):
    is_connected = rops.get_parameter_value(node, "is_connected")
    if is_connected == 0:
        if coredata.valid():
            rops.set_parameter_value(node, "is_connected", 1)


def populate_menu(node, parm, **kwargs):
    """Call method to populate any menu dynamically.

    Menu populate methods are defined in MENUS dict.
    We handle single and multi parms. 
    In the case of multi parms, the handler key has no index. It just ends in an underscore.
    """

    # print("populate_menu: parm: ", parm)
    check_connection(node, **kwargs)
    # rops.import_image_output(node)

    with errors.show():
        
        menu_key = parm.name()
        match = MULTI_PARM_RE.match(menu_key)
        if match:
            menu_key = match.group(1)
        # print("Populate menu: {}".format(menu_key))
        return MENUS.get(menu_key, noop )(node)


def populate_menu_extended(node, parm, **kwargs):
    """Call method to populate any menu dynamically.

    Menu populate methods are defined in MENUS dict.
    We handle single and multi parms.
    In the case of multi parms, the handler key has no index. It just ends in an underscore.
    """
    populated_parm = {}
    print("populate_menu: parm: ", parm)
    check_connection(node, **kwargs)
    # rops.import_image_output(node)

    with errors.show():

        menu_key = parm.name()
        if menu_key not in populated_parm:
            print("Populate menu: {}".format(menu_key))
            populated_parm[menu_key] = True
            match = MULTI_PARM_RE.match(menu_key)
            if match:
                menu_key = match.group(1)
            # print("Populate menu: {}".format(menu_key))
            return MENUS.get(menu_key, noop)(node)
        else:
            print("Populate menu: {} already populated".format(menu_key))



def set_instance_type(node):
    """ Set instance type to GPU if Redshift renderer is selected """
    driver_software = node.parm("driver_version").eval().lower()
    if "redshift" in driver_software:
        logger.debug("Instance type is set to GPU to accommodate the selected RedShift renderer.")
        node.parm("instance_type_family").set("GPU")

def on_updated(node, **kwargs):
    """
    Make changes based on input connecion make/break.

    Input means driver: arnold, mantra, sim dop simulation etc.
    """
    # print("on_updated: kwargs: ", kwargs)
    pass
def on_input_changed(node, **kwargs):
    """
    Make changes based on input connecion make/break.

    Input means driver: arnold, mantra, sim dop simulation etc.
    """
    # print("on_input_changed: kwargs: ", kwargs)
    with errors.show():
        driver.update_input_node(node)
        software.ensure_valid_selection(node)
        # rops.import_image_output(node, **kwargs)

    node_type = rops.get_node_type(node)
    if node_type not in ["generator"]:
        payload.set_preview_panel(node, **kwargs)

PARM_HANDLERS = {
    "connect": connect,
    "instance_type_family": instances.ensure_valid_selection,
    "use_custom_frames": frames.on_use_custom,
    "clear_all_assets": assets.clear_all_assets ,
    "browse_files": assets.browse_files ,
    "browse_folder": assets.browse_folder,
    "add_hdas":  assets.add_hdas,
    "submit": submit.invoke_submission_dialog,
    "export_script": submit.export_script,
    "add_variable": environment.add_variable,
    "add_existing_variable": environment.add_existing_variables,
    "add_plugin": software.add_plugin,
    "frame_range_source": frames.update_frame_range,
    "reload_render_rops": render_rops.reload_render_rops,
    "update_render_rops": render_rops.update_render_rops,
    "apply_to_all_render_rops": render_rops.apply_script_to_all_render_rops,
    "select_all_render_rops": render_rops.select_all_render_rops,
    "deselect_all_render_rops": render_rops.deselect_all_render_rops,
    "copy_script": miscellaneous.copy_render_script,
    "log_level": miscellaneous.change_log_level,
    "output_folder": rops.query_output_folder,
    # "render_script": rops.update_render_rop_options,
    #"task_template": rops.update_render_rop_options,
    #"render_rop_list": rops.get_render_rop_options,
    #"render_delegate": rops.default_render_software,
    "render_delegate": rops.set_render_software,
    "usd_filepath": rops.set_usd_path,
    #"image_output_source": rops.set_image_output_override,
    "task_template_source": rops.set_default_task_template,
    # "override_image_output": rops.import_image_output,
    #"driver_path": rops.set_driver_path,
    # "driver_path": rops.import_image_output,
    "browse_usd_files": create_usd.browse_usd_file,
    "generate": rops.generate_solaris_nodes,
    # "do_asset_scan": assets.do_asset_scan,
}

def noop(node, **kwargs):
    pass

def on_change(node, **kwargs):
    """Routing for all HDA parameter callbacks.
    
    handler can be a callback or a list of callbacks
    """
    parm_name = kwargs["parm_name"]
    # print("on_change: parm_name: ", parm_name)
    # logger.debug("parm_name: {}".format(parm_name))
    # logger.debug("value: ", node.parm(parm_name).eval())
    with errors.show():
        # All parms invoke one or more handler functions from the PARM_HANDLERS dict.
        funcs = PARM_HANDLERS.get(parm_name, noop)
        # logger.debug("funcs: {}".format(funcs))
        if not isinstance(funcs, list):
            funcs = [funcs]
        for func in funcs:
            func(node, **kwargs)

        if parm_name.startswith(AFFECTS_PAYLOAD):
            node_type = rops.get_node_type(node)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)

        # Only update image output if a render-related parameter changed
        # print("on_change: parm_name: ", parm_name)
        """
        if parm_name in ["driver_path"]:
            kwargs["force_image_path"] = True
            rops.import_image_output(node, **kwargs)
        """


def on_action_button(node, **kwargs):
    """
    Callback for any action button.

    Action buttons are the little buttons ion the right hand side that can be associated with any
    parm.

    """
    with errors.show():
        node_type = rops.get_node_type(node)

        parmtuple = kwargs["parmtuple"]
        if parmtuple.name().startswith("extra_asset_"):
            index = kwargs["script_multiparm_index"]
            assets.remove_asset(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node,  **kwargs)
                return

        if parmtuple.name().startswith("env_excl_"):
            index = kwargs["script_multiparm_index"]
            environment.remove_variable(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node,  **kwargs)
            return

        if parmtuple.name().startswith("extra_plugin_"):
            index = kwargs["script_multiparm_index"]
            software.remove_plugin(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)
            return