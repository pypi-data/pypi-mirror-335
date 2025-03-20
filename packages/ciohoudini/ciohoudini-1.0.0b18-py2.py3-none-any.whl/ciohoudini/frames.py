import hou
import re
import math

XPY = hou.exprLanguage.Python
from ciohoudini import errors, rops
from cioseq.sequence import Sequence
from ciocore import data as coredata

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

AUTO_RX = re.compile(r"^auto[, :]+(\d+)$")
FML_RX = re.compile(r"^fml[, :]+(\d+)$")

MAX_TASKS = 800

EXPR = """
import hou
from cioseq.sequence import Sequence

rop = hou.node(hou.pwd().parm('driver_path').evalAsString())
if not rop:
    first, last = hou.playbar.timelineRange()
    inc = hou.playbar.frameIncrement()
    return str(Sequence.create( first, last, inc))

use_range = rop.parm("trange").eval()
if not use_range:
    return int(hou.frame())

progression = rop.parmTuple("f").eval()
return str(Sequence.create(*progression))
"""

rendersettings_types = [
        "rendersettings",         # Solaris RenderSettings
        "karmarenderproperties",       # Karma RenderSettings (Radeon ProRender)
        "arnold_rendersettings",     # Arnold RenderSettings
    ]

"""
frame_range_source_dict = {"Houdini playbar": get_playbar_frame_range,
                        "Render rop node": get_rop_frame_range,
                        "Nearest render settings node":get_nearest_render_settings_frame_range,
                        "Custom frame range":get_custom_frame_range
                        }
"""

def on_use_custom(node, **kwargs):
    """
    Whether to override the frames specified in the input ROP.
    """
    node.parm("frame_range").deleteAllKeyframes()
    if not node.parm("use_custom_frames").eval():
        node.parm("frame_range").setExpression(EXPR, XPY, True)


def populate_frame_range_menu(node):
    """ Populate the frame range menu.
    This is called by the UI whenever the user clicks the Frame Range button.
    """

    # frame_override_methods = ["Houdini playbar", "Render rop node", "Nearest render settings node"]
    frame_override_methods = ["Houdini playbar", "Render rop node"]
    # logger.debug("populate_frame_range_menu")

    # menu_value = node.parm("frame_range_source").eval()
    # logger.debug("populate_frame_range_menu: menu_value: {}".format(menu_value))
    # update_render_rop_frame_range(node)
    return [el for i in frame_override_methods for el in (i, i)]

def update_render_rop_frame_range(node, **kwargs):
    """Update the frame range for all render rops in the UI."""
    try:
        # Get the current count of render rops
        render_rops_parm = node.parm("render_rops")
        if render_rops_parm:
            curr_count = render_rops_parm.eval()
            for i in range(1, curr_count + 1):
                rop_path_parm = node.parm("rop_path_{}".format(i))
                if rop_path_parm:
                    rop_path = rop_path_parm.evalAsString()
                    frame_range = get_all_rop_frame_range(node, rop_path)
                    if frame_range:
                        rop_frame_range_parm = node.parm("rop_frame_range_{}".format(i))
                        if rop_frame_range_parm:
                            rop_frame_range_parm.set(frame_range)
                        # logger.debug("update_render_rop_frame_range: rop_path: {}".format(rop_path))
                        # logger.debug("update_render_rop_frame_range: frame_range: {}".format(frame_range))
    except Exception as e:
        logger.debug("update_render_rop_frame_range: Error updating render rop frame range: {}".format(e))

def set_default_frame_range(node, **kwargs):
    frame_range = get_playbar_frame_range(node, None)
    rops.set_parameter_value(node, "frame_range", frame_range)

def update_frame_range(node, **kwargs):
    # Get the node type:
    node_type = rops.get_node_type(node)
    #if node_type in ["solaris"]:
    #    rop_path = node.parm("driver_path").evalAsString()
    #    frame_range = get_all_rop_frame_range(node, rop_path)
    #   rops.set_parameter_value(node, "frame_range", frame_range)
    if node_type in ["job"]:
        update_render_rop_frame_range(node, **kwargs)

def get_playbar_frame_range(node, rop):
    """ Get the frame range from the Houdini playbar."""
    start_time, end_time = hou.playbar.playbackRange()
    frame_range = "{}-{}".format(int(start_time), int(end_time))
    return frame_range


def get_nearest_render_settings_frame_range(node, rop):
    """ Get the frame range from the nearest render settings node."""
    frame_range = "1"
    rop_node = hou.node(rop)
    if rop_node:
        if rop_node.type().name() == 'usdrender_rop':
            render_rop_ancestors = rop_node.inputAncestors()

            # Find the first ancestor node is a render settings node of any type
            if render_rop_ancestors:
                for ancestor_node in render_rop_ancestors:
                    if is_render_settings_node(ancestor_node):
                        # Get the frame range from the render settings node
                        frame_range = get_frame_range(ancestor_node)
                        return frame_range
        else:
            frame_range = get_rop_frame_range(node, rop)
            return frame_range

    # If no render settings node was found, return "1"
    return frame_range
def get_custom_frame_range(node, rop):
    """ Get the frame range from the custom frame range field."""
    return node.parm("frame_range").eval()

def is_render_settings_node(node):
    # Check if the node is a render settings node of any type
    for type_name in rendersettings_types:
        if node.type().name() == type_name:
            return True
    return False

def get_frame_range(render_settings_node):
    # Get the frame range of the render settings node
    frame_range = "1"
    try:
        if render_settings_node:
            frame_range = "{}-{}".format(int(render_settings_node.parm("sample_f1").eval()), int(render_settings_node.parm("sample_f2").eval()))
        return frame_range
    except:
        pass
    return frame_range

def get_rop_frame_range(node, rop):
    """ Get the frame range from the render rop node."""
    frame_range = "1"
    rop_node = hou.node(rop)
    if rop_node:
        frame_range = "{}-{}".format(int(rop_node.parm("f1").eval()), int(rop_node.parm("f2").eval()))
    return frame_range
def get_all_rop_frame_range(node, rop_path):

    # Get the selected menu value
    menu_value = node.parm("frame_range_source").eval()

    if menu_value == "Houdini playbar":
        frame_range = get_playbar_frame_range(node, rop_path)
    elif menu_value == "Render rop node":
        frame_range = get_rop_frame_range(node, rop_path)
    elif menu_value == "Render settings node":
        frame_range = get_nearest_render_settings_frame_range(node, rop_path)
    elif menu_value == "Custom frame range":
        frame_range = get_custom_frame_range(node, rop_path)
    else:
        frame_range = "1"

    return frame_range
def set_stats_panel(node, **kwargs):
    """
    Update fields in the stats panel that are driven by frames related setttings.
    """

    if node.parm("is_sim").eval():
        node.parm("scout_frame_spec").set("0")
        node.parmTuple("frame_task_count").set((1, 1))
        node.parmTuple("scout_frame_task_count").set((0, 0))
        return

    main_seq = main_frame_sequence(node)
    frame_count = len(main_seq)
    task_count = main_seq.chunk_count()
    chunk_size = node.parm("chunk_size").eval()
    node.parm("resolved_chunk_size").set(str(chunk_size))
    resolved_chunk_size = cap_chunk_count(task_count, frame_count, chunk_size)
    if resolved_chunk_size >= chunk_size:
        node.parm("resolved_chunk_size").set(str(resolved_chunk_size))
        main_seq = main_frame_sequence(node, resolved_chunk_size=resolved_chunk_size)
        task_count = main_seq.chunk_count()
        frame_count = len(main_seq)

    scout_seq = scout_frame_sequence(node, main_seq)

    scout_frame_count = frame_count
    scout_task_count = task_count
    scout_frame_spec = "No scout frames. All frames will be started."

    if scout_seq:
        scout_chunks = main_seq.intersecting_chunks(scout_seq)
        # if there are no intersecting chunks, there are no scout frames, which means all frames will start.
        if scout_chunks:
            scout_tasks_sequence = Sequence.create(",".join(str(chunk) for chunk in scout_chunks))
            scout_frame_count = len(scout_tasks_sequence)
            scout_task_count = len(scout_chunks)
            scout_frame_spec = str(scout_seq)

    node.parm("scout_frame_spec").set(scout_frame_spec)
    node.parmTuple("frame_task_count").set((frame_count, task_count))
    node.parmTuple("scout_frame_task_count").set((scout_frame_count, scout_task_count))


def get_resolved_chunk_size(node, frame_range=None):
    """
    Get the resolved chunk size for the current node.
    """
    main_seq = main_frame_sequence(node, frame_range=frame_range)
    frame_count = len(main_seq)
    task_count = main_seq.chunk_count()
    chunk_size = node.parm("chunk_size").eval()
    node.parm("resolved_chunk_size").set(str(chunk_size))
    resolved_chunk_size = cap_chunk_count(task_count, frame_count, chunk_size)
    if resolved_chunk_size >= chunk_size:
        node.parm("resolved_chunk_size").set(str(resolved_chunk_size))
        return resolved_chunk_size

    return chunk_size

def cap_chunk_count(task_count, frame_count, chunk_size):
    """Cap the number of chunks to a max value.

    This is useful for limiting the number of chunks to a reasonable
    number, e.g. for a render farm.
    """
    if task_count > MAX_TASKS:
        return math.ceil(frame_count / MAX_TASKS)

    return chunk_size

def main_frame_sequence(node, frame_range=None, resolved_chunk_size=None):
    """
    Generate Sequence containing current chosen frames.
    """
    if not resolved_chunk_size:
        chunk_size = node.parm("chunk_size").eval()
    else:
        chunk_size = resolved_chunk_size
    if frame_range:
        spec = frame_range
    else:
        spec = node.parm("frame_range").eval()

    with errors.show():
        return Sequence.create(spec, chunk_size=chunk_size, chunk_strategy="progressions")


def scout_frame_sequence(node, main_sequence):
    """
    Generate Sequence containing scout frames.

    Scout frames may be generated from a spec, such as 1-2, 5-20x3 OR by subsampling the main
    sequence. Example: auto:5 would generate a scout sequence of 5 evenly spaced frames in the main
    sequence.
    """

    if not node.parm("use_scout_frames").eval():
        return

    scout_spec = node.parm("scout_frames").eval()

    match = AUTO_RX.match(scout_spec)
    if match:
        samples = int(match.group(1))
        return main_sequence.subsample(samples)
    else:
        match = FML_RX.match(scout_spec)
        if match:
            samples = int(match.group(1))
            return main_sequence.calc_fml(samples)

    try:
        return Sequence.create(scout_spec).intersection(main_sequence)

        #  Sequence.create(scout_spec)
    except:
        pass


def resolve_payload(node, frame_range=None):
    """If we are in sim mode, don't add scout frames."""

    if node.parm("is_sim").eval():
        return {}
    if not node.parm("use_scout_frames").eval():
        return {}

    main_seq = main_frame_sequence(node, frame_range=frame_range)
    scout_sequence = scout_frame_sequence(node, main_seq)
    if scout_sequence:
        return {"scout_frames": ",".join([str(f) for f in scout_sequence])}
    return {}

