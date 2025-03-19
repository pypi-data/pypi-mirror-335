import re
import os
from ciohoudini import frames, context, rops, util

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def create_task_template_husk(node, **kwargs):
    """Get the task template from the node and format it based on input_template."""

    rop_path = kwargs.get("rop_path", None)
    # rop_name = extract_name(rop_path)
    rop_name = "usd_rop1"
    output_folder = node.parm("output_folder").eval()
    first = kwargs.get("first", 1)
    last = kwargs.get("last", 1)
    step = kwargs.get("step", 1)
    count = last-first+1
    renderer = "Karma"
    usd_filepath = "/Users/alaaibrahim/Documents/Tasks/Houdini/Houdini-Demo/Houdini-demo/SimpleScene/geo/simple_scene_6_solaris.usd_rop1.usd"
    render_output_filespec = "{0}/{1}.1.exr".format(output_folder, rop_name)
    #Todo: fix this
    # input_template = rops.query_task_template(node, rop_path)
    input_template = f'husk -v 9 -f {first} -n {count} -i {step} -o {render_output_filespec} {usd_filepath}'

    logger.debug("Input template: {}".format(input_template))


    render_script = rops.query_render_script(node, rop_path)
    render_scene = node.parm("render_scene").eval()
    host_version = node.parm("host_version").eval()

    # Expand variables for rop_path and render_scene
    try:
        if rop_path:
            rop_path = os.path.expandvars(rop_path)
    except Exception as e:
        logger.error("Error expanding rop path {}: {}".format(rop_path, e))

    try:
        render_scene = os.path.expandvars(render_scene)
    except Exception as e:
        logger.error("Error expanding render scene {}: {}".format(render_scene, e))

    node_type = rops.get_node_type(node)
    hython_list = rops.get_node_list("hython_command")
    husk_list = rops.get_node_list("task_template_source")
    render_method = "hython"
    usd_path = rops.get_usd_path(node)
    if node_type in hython_list:
        render_method = "hython"
    elif node_type in husk_list:
        render_method = "husk"

    # Prepare data for formatting the input template
    data = {
        "hserver": "",
        "hython": "hython",
        "render_script": re.sub("^[a-zA-Z]:", "", render_script).replace("\\", "/"),
        "first": first,
        "last": last,
        "step": step,
        "render_rop": rop_path,
        "render_method": render_method,
        "render_scene": render_scene,
        "usd_path": usd_path,
    }
    logger.debug("Data: {}".format(data))
    # Determine the host version and set hserver if needed
    try:
        host_version = int(host_version.split()[1].split(".")[0])
    except:
        host_version = 19

    if host_version < 19:
        data["hserver"] = "/opt/sidefx/houdini/19/houdini-19.0.561/bin/hserver --logfile /tmp/hserver.log -C -D; "

    # Format the input template with the actual values
    task_command = ""
    try:
        task_command = 'husk -V 9 -f 1 -n 1 -i 1 \
            -o "/Users/alaaibrahim/Documents/Tasks/Houdini/Houdini-Demo/Houdini-demo/SimpleScene/render/usd_rop1.\\\$F4.exr" --renderer BRAY_HdKarma\
            "/Users/alaaibrahim/Documents/Tasks/Houdini/Houdini-Demo/Houdini-demo/SimpleScene/geo/simple_scene_6_solaris.usd_rop1.usd"'

        # logger.debug("Task command  : {}".format(task_command))
    except Exception as e:
        logger.debug(f"Missing key in data for template: {e}")

    return task_command

def extract_name(render_rop_path):
    """ Extract the name of the render rop from the path """
    return render_rop_path.split("/")[-1]


def get_task_template(node, **kwargs):
    task_template = ""
    try:
        """Get the task template from the node."""
        first = kwargs.get("first", 1)
        last = kwargs.get("last", 1)
        step = kwargs.get("step", 1)
        count = last - first + 1
        rop_path = kwargs.get("rop_path", None)
        render_script = node.parm("render_script").eval()
        render_delegate = get_render_delegate(node)
        image_output = get_image_output(node)
        usd_filepath = get_usd_path(node)
        render_scene = get_render_scene(node)
        # script_path = get_render_script(node)
        script_path = re.sub("^[a-zA-Z]:", "", render_script).replace("\\", "/")
        script_path = f'"{script_path}"'

        try:
            if rop_path:
                rop_path = os.path.expandvars(rop_path)
        except Exception as e:
            logger.error("Error expanding rop path {}: {}".format(rop_path, e))


        data = {
            "script": script_path,
            "render_script": script_path,
            "first": first,
            "last": last,
            "step": step,
            "count": count,
            "driver": rop_path, # Use the rop path instead of the driver path.
            "render_rop": rop_path,
            "image_output": image_output,
            "usd_filepath": usd_filepath,
            "render_delegate": render_delegate,
            "hipfile": render_scene,
            "render_scene": render_scene,
            "hserver": ""
        }

        cmd = rops.get_parameter_value(node, "task_template", string_value=True)
        # logger.debug("cmd: {}".format(cmd))
        if not cmd:
            cmd = rops.query_task_template(node, rop_path)
        task_template = cmd.format(**data)
        # logger.debug("Task template: {}".format(task_template))
    except Exception as e:
        logger.error("Error getting task template: {}".format(e))

    return task_template

def get_render_scene(node):
    """Get the render scene from the node."""

    # Default houdini scene
    render_scene = "$HIP/$HIPNAME.hip"

    try:
        render_scene = rops.get_parameter_value(node, "render_scene", string_value=True)
        render_scene = util.prepare_path(render_scene)

    except Exception as e:
        logger.error("Error getting render scene: {}".format(e))

    return render_scene



def get_image_output(node):
    """Get the image output from the node."""
    # Default image output
    image_output = "$HIP/render/$HIPNAME.$OS.$F4.exr"
    try:
        node_type = rops.get_node_type(node)
        node_list = rops.get_node_list("import_image_output")
        if node_type in node_list:
            image_output = rops.get_parameter_value(node, "override_image_output",  string_value=True)
            image_output = util.prepare_path(image_output)
    except Exception as e:
        logger.error("Error getting image output: {}".format(e))

    image_output = os.path.expandvars(image_output)
    return image_output


def get_render_script_stripped(node):
    """Get the render script from the node."""
    render_script = rops.get_default_render_script()
    try:
        render_script = rops.get_parameter_value(node, "render_script", string_value=True)
        render_script = os.path.expandvars(render_script)
        render_script = util.clean_and_strip_path(render_script)
        render_script = f'"{render_script}"'


    except Exception as e:
        logger.error("Error getting render script: {}".format(e))
    return render_script



def get_render_script(node):
    """Get the render script from the node."""
    render_script = rops.get_default_render_script()
    try:
        render_script = rops.get_parameter_value(node, "render_script", string_value=True)
        render_script = util.prepare_path(render_script)

    except Exception as e:
        logger.error("Error getting render script: {}".format(e))
    return render_script


def get_render_delegate(node):
    """Get the render delegate from the node."""

    render_delegate = rops.get_render_delegate(node)

    return render_delegate

def get_usd_path(node):
    """Get the USD file path from the node."""
    usd_path = ""
    try:
        node_type = rops.get_node_type(node)
        node_list = rops.get_node_list("usd_filepath")
        if node_type in node_list:
            usd_path = rops.get_parameter_value(node, "usd_filepath", string_value=True)
            usd_path = util.prepare_path(usd_path)
    except Exception as e:
        logger.error("Error getting USD path: {}".format(e))
    return usd_path

def get_host_version(node):
    """Get the host version from the node."""
    host_version = node.parm("host_version").eval()
    try:
        host_version = int(host_version.split()[1].split(".")[0])
    except:
        host_version = 19
    return host_version

def resolve_payload(node, **kwargs):
    """
    Resolve the task_data field for the payload.

    If we are in sim mode, we emit one task.
    """
    tasks = []
    if not node:
        return {"tasks_data": tasks}
    try:
        task_limit = kwargs.get("task_limit", -1)
        frame_range = kwargs.get("frame_range", None)
        if node.parm("is_sim").eval():
            cmd = node.parm("task_template").eval()
            tasks = [{"command": cmd, "frames": "0"}]
            return {"tasks_data": tasks}

        resolved_chunk_size = frames.get_resolved_chunk_size(node, frame_range=frame_range)
        sequence = frames.main_frame_sequence(node, frame_range=frame_range, resolved_chunk_size=resolved_chunk_size)
        chunks = sequence.chunks()
        # Get the scout sequence, if any.
        for i, chunk in enumerate(chunks):
            if task_limit > -1 and i >= task_limit:
                break
            # Get the frame range for this chunk.
            #
            kwargs["first"] = chunk.start
            kwargs["last"] = chunk.end
            kwargs["step"] = chunk.step
            # logger.debug("resolve_payload: kwargs: {}".format(kwargs))
            # Get the task template.

            cmd = get_task_template(node, **kwargs)
            # Set the context for this chunk.
            context.set_for_task(first=chunk.start, last=chunk.end, step=chunk.step)


            tasks.append({"command": cmd, "frames": str(chunk)})
    except Exception as e:
        logger.error("Error resolving payload: {}".format(e))


    return {"tasks_data": tasks}
