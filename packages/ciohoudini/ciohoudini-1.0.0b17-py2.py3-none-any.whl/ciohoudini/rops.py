import hou
import os
from ciohoudini import driver, frames, render_rops, software

from pxr import Usd, UsdRender

# render_rop_options = {}

nodes_dict = {
        "job": {
            "name": "job",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": True,
            "render_delegate": False,
            "image_output_source": False,
            "hython_command": True,
            "task_template_source": False,
        },
        "legacy": {
            "name": "legacy",
            "title": "Conductor Legacy Submitter",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": True,
            "render_delegate": False,
            "image_output_source": False,
            "hython_command": True,
            "task_template_source": False,
        },
        "rop": {
            "name": "rop",
            "title": "Conductor Rop Submitter",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": False,
            "render_delegate": True,
            "image_output_source": False,
            "import_image_output": True,
            "hython_command": True,
            "task_template_source": False,
        },
        "solaris": {
            "name": "solaris",
            "title": "Conductor Solaris Submitter",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": False,
            "render_delegate": True,
            "image_output_source": False,
            "import_image_output": True,
            "hython_command": True,
            "task_template_source": False,
        },
       "husk": {
            "name": "husk",
            "title": "Conductor Husk Submitter",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": False,
            "render_delegate": True,
            "image_output_source": False,
            "import_image_output": True,
            "hython_command": False,
            "husk_command": True,
            "usd_filepath": True,
            "task_template_source": False,
        },

        "generator": {
            "name": "generator",
            "title": "Conductor Generator",
            "render_rop_paths": True,
            "render_rop_list": True,
            "multi_rop": False,
            "render_delegate": True,
            "image_output_source": True,
            "chunk_size": True,
            "hython_command": True,
            "generation": True,
            "task_template_source": False,
        },
}
"""
Set the task template for the render job.
{first}: The starting frame of the render.
{count}: The total number of frames to render.
{step}: The frame increment (e.g., 1 for every frame, 2 for every second frame).
{image_output}: Path to the rendered output file(s), typically with frame variables like $F4.
{render_delegate}: The Hydra render delegate (e.g., HdKarma, HdStorm, etc.).
{usd_filepath}: Path to the USD file to render.

"""
task_templates_dict = {
  "hython": "{hserver}hython {render_script} -f {first} {last} {step} -d {render_rop} -o {image_output} {render_scene}", #Hython Command
    "arnold_renderer_kick": "kick -i {usd_filepath} -frames {first}-{last} -step {step} -o {image_output} --renderer {render_delegate}", #Arnold Renderer Kick
    "husk": "husk --verbose 9 -f {first} -n {count} -i {step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Husk
    "pixar_usd_record": "usdrecord --verbose 9 --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Pixar USD Record
    "pixar_renderman": "prman --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Pixar RenderMan
    "redshift_commandline_renderer": "redshiftCmdLine -l {usd_filepath} -f {first} -e {last} -s {step} -o {image_output} --renderer {render_delegate}", #Redshift Command Line Renderer
    "nvidia_omniverse_kit": "kit-cli-render {usd_filepath} --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate}", #NVIDIA Omniverse Kit
    "hydra_viewe_usdview": "usdview {usd_filepath} --renderer {render_delegate} --frames {first}:{last}:{step} --output {image_output}", #Hydra Viewer (usdview)

}

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

def get_node_type(node):
    if not node:
        return None
    try:
        for key in nodes_dict:
            # logger.debug("node name : ", node.name())
            # logger.debug("node type: ", node.type().name())
            if key in node.type().name():
                return key
    except Exception as e:
        logger.error(f"Error getting node type: {e}")


def get_node_list(parm):
    node_list = []
    try:
        for key in nodes_dict:
            target = nodes_dict[key]
            if parm in target and target.get(parm, False):
                node_list.append(key)
        return node_list
    except Exception as e:
        logger.error(f"Error getting node list: {e}")


def get_parameter_value(node, parm_name, string_value=False, unexpand=False):
    """
    Retrieves the value of a parameter on a given Houdini node.

    Args:
        node (hou.Node): The Houdini node containing the parameter.
        parm_name (str): The name of the parameter to retrieve.

    Returns:
        str: The value of the parameter if found, otherwise an empty string.
    """
    try:
        parm = node.parm(parm_name)
        #print("Node name: ", node.name())
        #print("Parameter name: ", parm_name)
        if parm:
            if unexpand:
                return parm.unexpandedString()
            #print("Getting parameter value: ", parm.evalAsString())
            if string_value:
                return parm.evalAsString()
            else:
                return parm.eval()

        #else:
        #   logger.debug(f"Parameter not found: {parm_name}")
    except Exception as e:
        logger.error(f"Error getting parameter value: {e}")

    return None


def set_parameter_value(node, parm_name, value):
    """
    Sets the value of a parameter on a given Houdini node.

    Args:
        node (hou.Node): The Houdini node containing the parameter.
        parm_name (str): The name of the parameter to set.
        value (str): The value to set on the parameter.
    """
    try:
        if node:
            parm = node.parm(parm_name)
            if parm:
                parm.set(value)
        else:
            logger.debug(f"Node not found.")
    except Exception as e:
        logger.error(f"Error setting parameter value: {e}")

def evaluate_houdini_parameter(parm):
    """
    Evaluates a Houdini parameter, resolving any channel references (ch(), chs()),
    Houdini expressions (e.g., $HIP), or direct string values.
    If the parameter is 'output_folder' and the result is a file path, returns the directory of the path.

    Args:
        parm (hou.Parm): The Houdini parameter to evaluate.

    Returns:
        str: The resolved value of the parameter, or the folder if it's an 'output_folder' parameter with a file path.
    """

    try:
        if parm is not None:
            # Get the parameter name
            parm_name = parm.name()

            # Evaluate the parameter to get the resolved value or expression
            parm_value = parm.evalAsString()

            # Check if the value contains a channel reference (ch(), chs())
            if parm_value.startswith(('ch(', 'chs(', 'ch("', 'chs("')):
                # Extract the referenced parameter's path, remove 'ch()', 'chs()', fancy quotes, and spaces
                referenced_parm_path = parm_value[parm_value.index('(') + 1:-1].strip().replace('“', '"').replace('”', '"').strip('\"')

                # Separate the node path and parameter name
                node_path, ref_parm_name = referenced_parm_path.rsplit("/", 1)

                # Get the node that contains the referenced parameter
                referenced_node = hou.node(node_path)

                if referenced_node is not None:
                    # Get the parameter on the referenced node
                    referenced_parm = referenced_node.parm(ref_parm_name)

                    if referenced_parm is not None:
                        # Evaluate the referenced parameter's value
                        resolved_value = referenced_parm.eval()
                    else:
                        logger.debug(f"Could not find parameter: {ref_parm_name} on node {node_path}")
                        return None
                else:
                    logger.debug(f"Could not find node: {node_path}")
                    return None
            else:
                # If it's not a channel reference, evaluate and return the value
                resolved_value = parm.eval()

            # Special handling if the parameter is 'output_folder'
            if parm_name == "output_folder":
                # Check if the resolved value is a file path (i.e., contains a file extension)
                if os.path.isfile(resolved_value) or os.path.splitext(resolved_value)[1]:
                    # Return the folder of the file path
                    return os.path.dirname(resolved_value)

            # Return the evaluated value (or folder if applicable)
            return resolved_value
    except Exception as e:
        logger.error(f"Error evaluating Houdini parameter: {e}")

    return None



def evaluate_houdini_path(path_value):
    """
    Evaluates a Houdini path value, resolving any channel references (ch(), chs()),
    Houdini expressions (e.g., $HIP), or direct string values.
    If the result is a file path, returns the directory of the path.

    Args:
        path_value (str): The value of the path, which may be a channel reference, file path, folder path, or expression.

    Returns:
        str: The resolved path, or the folder if it's a file path.
    """
    if path_value is None:
        return None
    try:

        # Check if the value contains a channel reference (ch(), chs())
        if path_value.startswith(('ch(', 'chs(', 'ch("', 'chs("')):
            # Extract the referenced parameter's path, remove 'ch()', 'chs()', fancy quotes, and spaces
            referenced_parm_path = path_value[path_value.index('(') + 1:-1].strip().replace('“', '"').replace('”', '"').strip('\"')

            # Separate the node path and parameter name
            node_path, ref_parm_name = referenced_parm_path.rsplit("/", 1)

            # Get the node that contains the referenced parameter
            referenced_node = hou.node(node_path)

            if referenced_node is not None:
                # Get the parameter on the referenced node
                referenced_parm = referenced_node.parm(ref_parm_name)

                if referenced_parm is not None:
                    # Evaluate the referenced parameter's value
                    resolved_value = referenced_parm.eval()
                else:
                    logger.debug(f"Could not find parameter: {ref_parm_name} on node {node_path}")
                    return None
            else:
                logger.debug(f"Could not find node: {node_path}")
                return None
        else:
            # If it's not a channel reference, evaluate and return the value directly (handles $HIP, etc.)
            resolved_value = hou.expandString(path_value)

        # Special handling if the resolved value is a file path
        if os.path.isfile(resolved_value) or os.path.splitext(resolved_value)[1]:
            # Return the folder of the file path
            return os.path.dirname(resolved_value)

        # Return the evaluated value (which might already be a folder)
        return resolved_value

    except Exception as e:
        logger.error(f"Error evaluating Houdini path: {e}")
        return None


def list_current_render_rop_paths(node):
    """
    Collects all the render ROP paths from the provided node.

    Args:
        node (hou.Node): The Houdini node from which to retrieve the ROP paths.

    Returns:
        list: A list of strings representing the render ROP paths.
    """
    render_rops_list = []
    if not node:
        return render_rops_list
    node_type = get_node_type(node)
    node_list = get_node_list("render_rop_paths")
    if node_type in node_list:
        for i in range(1, node.parm("render_rops").eval() + 1):
            path = node.parm("rop_path_{}".format(i)).eval()
            if path:
                render_rops_list.append(path)
    else:
        driver_type = node.parm("driver_type").eval()
        if "usdrender_rop" in driver_type:
            driver_path = node.parm("driver_path").eval()
            if driver_path:
                render_rops_list.append(driver_path)

    return render_rops_list

def prepare_usd_submissions(node):
    try:
        node_type = get_node_type(node)
        node_list = get_node_list("task_template_source")

        if node_type in node_list:
            if node_type in ["husk"]:
                driver_path = node.parm("driver_path").eval()
                if driver_path:
                    save_usd(node, driver_path)
            # Todo: do this for the generator node as well
            elif node_type in ["generator"]:
                render_rop_list = node.parm("render_rop_list").eval()
                if render_rop_list:
                    pass
    except Exception as e:
        logger.error(f"Error preparing USD submissions: {e}")

def get_usd_path_original(node):

    usd_export_path = ""
    try:
        driver_path = get_parameter_value(node, "driver_path")
        if not driver_path:
            return usd_export_path
        usd_node = hou.node(driver_path)

        if usd_node:
            # Ensure the output path is set correctly
            hip_file = hou.hipFile.path()

            hip_folder = os.path.dirname(hip_file)
            hip_name = os.path.basename(hip_file)

            driver_name = driver_path.split('/')[-1]
            # usd_export_path is hip folder / hip file name + driver name without stage .usd
            usd_export_path = f"{hip_folder}/{hip_name.replace('.hip', '')}_{driver_name}.usd"
    except Exception as e:
        logger.error(f"Error getting USD path: {e}")

    return usd_export_path

def save_usd(node, driver_path):
    """
    Prepares the USD submission for the given node.

    Args:
        node (hou.Node): The Houdini node to prepare the submission for.
    """
    usd_export_path = ""
    try:
        usd_node = hou.node(driver_path)
        usd_export_path = get_usd_path_original(node)
        if usd_node:
            usd_node.parm("lopoutput").set(usd_export_path)

            # Render the node to create the USD file
            usd_node.render(verbose=True, output_progress=True)
            logger.debug(f"USD file exported to: {usd_export_path}")
            if usd_export_path:
                # Set the usd_file parameter of the node to be the exported USD file
                set_parameter_value(node, "usd_file", usd_export_path)

    except Exception as e:
        logger.error(f"Error preparing USD node: {e}")

    return usd_export_path
def populate_render_rop_menu(node):
    """
    Populates a list of render ROPs in the current stage and sets the default ROPs for the node.

    Args:
        node (hou.Node): The Houdini node for which the render ROP menu is being populated.

    Returns:
        list: A list of strings representing the paths of the ROPs found in the stage.
    """
    stage_render_ropes = []
    render_ropes_list = []
    try:
        node_type = get_node_type(node)
        node_list = get_node_list("render_rop_list")
        if node_type in node_list:

            # Add the driver ROP if it exists
            driver_rop = driver.get_driver_node(node)
            if driver_rop:
                key = driver_rop.path()
                stage_render_ropes.extend([key, key])
                render_ropes_list.append(key)

            # Add all render ROPs in the stage
            stage_node_list = hou.node('/stage').allSubChildren()

            if stage_node_list:
                for rop in stage_node_list:
                    if rop and rop.type().name() == 'usdrender_rop' and not rop.isBypassed():
                        key = rop.path()
                        stage_render_ropes.extend([key, key])
                        render_ropes_list.append(key)

            # Set the first render rop in the list as the node's render_rop_list parameter
            key = node.parm("render_rop_list").eval()
            if key and render_ropes_list and "Connection" in key or "connection" in key:
                key = render_ropes_list[0]
                node.parm("render_rop_list").set(key)

            # Set default render ROPs for the node
            # set_default_render_rops(node, render_ropes_list)
    except Exception as e:
        logger.error(f"Error populating render rop menu: {e}")

    return stage_render_ropes

def get_default_output_folder():
    """
    Retrieves the default output folder path for the current Houdini session.

    Returns:
        str: The default output folder path.
    """
    output_folder = ""
    try:
        output_folder = driver.calculate_output_path(hou.pwd()).replace("\\", "/")
        if not output_folder:
            hip_path = os.path.expandvars("$HIP")
            output_folder = f'{hip_path}/render'
    except Exception as e:
        logger.error(f"Error getting default output folder: {e}")

    return output_folder

def get_default_render_script():
    """
    Retrieves the default render script path based on environment variables.

    Returns:
        str: The default render script path.
    """
    render_script = ""
    try:
        ciodir = os.environ.get("CIODIR")
        render_script = f"{ciodir}/ciohoudini/scripts/chrender.py"
    except Exception as e:
        logger.error(f"Error getting default render script: {e}")

    return render_script


def set_default_task_template(node, **kwargs):
    """
    Retrieves the default task template for rendering.

    Returns:
        str: The default task template for render jobs.
    """
    # logger.debug("MARK: 1")
    node_type = get_node_type(node)
    node_list = get_node_list("task_template_source")
    if node_type in node_list:
        get_default_task_template(node)


def get_default_task_template(node):
    """
    Retrieves the default task template for rendering.

    Returns:
        str: The default task template for render jobs.
    """
    task_template = ""
    if not node:
        return task_template
    try:
        node_type = get_node_type(node)
        hython_list = get_node_list("hython_command")
        husk_list = get_node_list("husk_command")
        # Generator node temporarily doesn't have a task template source, so it's not included in the list
        generator_list = get_node_list("task_template_source")
        if node_type in hython_list:
            task_template = get_hython_task_template(node)
        if node_type in husk_list:
            task_template = get_husk_task_template(node)
        if node_type in generator_list:
            task_template = get_generator_task_template(node)
        set_parameter_value(node, "task_template", task_template)

    except Exception as e:
        logger.error(f"Error getting default task template: {e}")

    return task_template

def get_husk_task_template(node):
    """
    Retrieves the husk task template for rendering.

    Returns:
        str: The husk task template for render jobs.
    """
    task_template = ""
    try:
        task_template = task_templates_dict.get("husk", "")
        # logger.debug("Husk task_template", task_template)

    except Exception as e:
        logger.error(f"Error getting husk task template: {e}")

    return task_template
def get_generator_task_template(node):
    """
    Retrieves the default task template for rendering using Solaris.

    Returns:
        str: The default task template for render jobs using Solaris.
    """
    task_template = ""
    task_template_source = ""
    try:
        task_template_source = get_parameter_value(node, "task_template_source")
        task_template = task_templates_dict.get(task_template_source, "")

    except Exception as e:
        logger.error(f"Error getting task template from {task_template_source}: {e}")

    return task_template

def get_hython_task_template(node):
    """
    Retrieves the default task template for rendering using Hython.

    Returns:
        str: The default task template for render jobs using Hython.
    """
    task_template = ""
    try:
        task_template = task_templates_dict.get("hython", "")

    except Exception as e:
        logger.error(f"Error getting Hython task template: {e}")

    return task_template

def set_driver_version(node):
    """
    Imports the render delegate from the render ROP node to the current node and set the driver version

    Args:
        node (hou.Node): The Houdini node to import the image output for.
    """
    try:
        node_type = get_node_type(node)
        if node_type in ["solaris"]:
            driver_path = get_parameter_value(node, "driver_path")
            driver_version = "built-in: karma-houdini"
            if driver_path:
                driver_node = hou.node(driver_path)
                if driver_node:
                    # software.set_plugin(node)
                    software.ensure_valid_selection(node)
                else:
                    set_parameter_value(node, "driver_version", driver_version)
            else:
                set_parameter_value(node, "driver_version", driver_version)

    except Exception as e:
        logger.error(f"Error importing image output: {e}")

def set_driver_path(node, **kwargs):
    """
    Imports the driver path from the current node.

    Args:
        node (hou.Node): The Houdini node to import the image output for.
    """
    try:
        node_type = get_node_type(node)
        if node_type in ["solaris", "rop"]:
            driver_path = get_parameter_value(node, "driver_path")
            if driver_path:
                set_parameter_value(node, "driver_path", driver_path)

    except Exception as e:
        logger.error(f"Error importing driver path: {e}")

def import_image_output(node, **kwargs):
    """
    Imports the image output from the render ROP node to the current node.

    Args:
        node (hou.Node): The Houdini node to import the image output for.
    """
    try:
        node_type = get_node_type(node)
        if node_type in ["husk"]:
            return
        set_driver_path(node, **kwargs)

        node_list = get_node_list("import_image_output")

        # logger.debug("node_type", node_type)
        if node_type in node_list:
            """
            force_image_path = kwargs.get("force_image_path", False)
            if not force_image_path:
                # Check if the user manually set a value
                user_override = node.parm("override_image_output").eval().strip()

                # If the parameter is already set, do not override
                if user_override and user_override != "":
                   logger.debug(f"User-set override_image_output retained: {user_override}")
                   return
            """

            image_output = ""
            driver_path = get_parameter_value(node, "driver_path")
            # print("driver_path 0: ", driver_path)
            if driver_path:
                if node_type in ["rop"]:
                    image_output = get_rop_image_output(node)

                elif node_type in ["solaris"]:
                    image_output = get_solaris_image_output(driver_path)
                    # print("image_output 1", image_output)
                # logger.debug("import_image_output: image_output:", image_output)
                if image_output:
                    # print("image_output 2", image_output)
                    set_parameter_value(node, "override_image_output", image_output)

                else:
                    logger.debug("No image output found")
                # print("override_image_output 3", image_output)

    except Exception as e:
        logger.error(f"Error importing image output: {e}")

def get_rop_image_output(node):
    """
    Retrieves the image output for the render ROP node.

    Returns:
        str: The image output for the render ROP node.
    """
    driver_path = get_parameter_value(node, "driver_path")
    if driver_path:
        return driver.get_rop_image_output(driver_path)


def get_solaris_image_output_original(driver_path):
    """
    Retrieves the image output for the Solaris render ROP node.

    Args:
        driver_path (str): The path to the Solaris render ROP node.

    Returns:
        str: The image output path for the Solaris render ROP node.
    """
    # image_output = "$HIP/render/$HIPNAME.$OS.$F4.exr"  # Default output path
    image_output = ""
    try:
        driver_node = hou.node(driver_path)
        if driver_node:
            # image_output = get_parameter_value(driver_node, "outputimage", string_value=True)
            image_output = get_parameter_value(driver_node, "outputimage")
            # print("Image output from USD render rop:", image_output)
            if not image_output:
                # print("No image output found in the USD render rop")
                # Find the first upstream Render Product node
                render_product_node = find_ancestor_render_product(driver_node)
                if render_product_node:
                    # print("Found Render Product node", render_product_node.path())
                    image_output = get_parameter_value(render_product_node, "productName", string_value=True)
                    # print("Image output from Render Product node:", image_output)

    except Exception as e:
        logger.error(f"Error getting Solaris image output: {e}")

    return image_output


def get_solaris_image_output(driver_path):
    """
    Retrieves the image output path for a given Solaris render ROP node in Houdini.
    This function attempts to determine the image output by checking the USD stage,
    referenced USD files, and the render node's parameters.

    Args:
        driver_path (str): The Houdini node path to the Solaris render ROP.

    Returns:
        str: The resolved image output path. Returns an empty string if the output
        path cannot be determined.

    Raises:
        Exception: Logs an error message if an unexpected issue occurs while retrieving
        the image output.

    Process:
        1. Attempts to retrieve the image output from the USD stage associated with
           the given render node.
        2. If the USD stage is not found, checks if the node references an external
           USD file and attempts to extract the render product from it.
        3. If the image output is still not found, it searches for an ancestor
           RenderProduct Houdini node and retrieves the `productName` parameter.
        4. Finally, as a fallback, it extracts the `outputimage` parameter from
           the driver node itself.

    Notes:
        - Uses `get_usd_stage(driver_node)` to retrieve the USD stage.
        - Uses `find_render_product_in_usd(stage)` to extract the render product path
          from the USD stage.
        - Uses `find_ancestor_render_product(driver_node)` to search for a RenderProduct node.
        - Uses `get_parameter_value(node, param, string_value=True)` to extract string
          parameter values from Houdini nodes.
    """
    image_output = ""
    try:
        driver_node = hou.node(driver_path)
        if driver_node:
            # Try to get image output from the USD stage first
            if not image_output:
                # Attempt to get image output from USD stage first
                stage = get_usd_stage(driver_node)
                if stage:
                    image_output = find_render_product_in_usd(stage)
                else:
                    # print("No USD stage found. Checking for loaded references.")
                    refs = driver_node.parm("lopoutput").eval()
                    if refs:
                        refs = os.path.abspath(refs)  # Ensure full path is used
                        # print(f"Possible referenced USD: {refs}")
                        if os.path.exists(refs):
                            try:
                                stage = Usd.Stage.Open(refs)
                                if stage:
                                    # print("Loaded USD reference stage successfully.")
                                    image_output = find_render_product_in_usd(stage)
                                    # print(f"Image output from referenced USD: {image_output}")
                                else:
                                    logger.debug("Failed to load referenced USD stage.")
                            except Exception as e:
                                logger.debug(f"Error loading referenced USD: {e}")
                        else:
                            logger.debug(f"Referenced USD file does not exist: {refs}")
            # If still not found, check the driver node
            if not image_output:
                image_output = get_parameter_value(driver_node, "outputimage", unexpand=True)
                # print(f"Image output from driver node: {image_output}")
            # If not found, fallback to RenderProduct Houdini node
            if not image_output:
                render_product_node = find_ancestor_render_product(driver_node)
                if render_product_node:
                    image_output = get_parameter_value(render_product_node, "productName", unexpand=True)
                    # print(f"Image output from Render Product node: {image_output}")


    except Exception as e:
        logger.error(f"Error getting Solaris image output: {e}")
    # If all attempts fail, return default image output
    if not image_output:
        image_output = "$HIP/render/$HIPNAME.$OS.$F4.exr"
    return image_output


def get_usd_stage(driver_node):
    """
    Retrieves the USD stage from a Solaris LOP node.

    Args:
        driver_node (hou.Node): The render ROP node.

    Returns:
        Usd.Stage: The USD stage if available, otherwise None.
    """
    try:
        if hasattr(driver_node, "editableStage"):
            return driver_node.editableStage()
    except Exception as e:
        logger.error(f"Error retrieving USD stage: {e}")
    return None


def find_render_product_in_usd(stage):
    """
    Searches for a UsdRenderProduct prim in the USD stage and returns its productName.

    Args:
        stage (Usd.Stage): The USD stage to search.

    Returns:
        str: The image output path from UsdRenderProduct, or "" if not found.
    """
    try:
        for prim in stage.Traverse():
            if prim.IsA(UsdRender.Product):
                render_product = UsdRender.Product(prim)
                image_output = render_product.GetProductNameAttr().Get()
                if image_output:
                    return image_output
    except Exception as e:
        logger.error(f"Error finding RenderProduct in USD: {e}")
    return ""



def find_ancestor_render_product(node):
    """
    Finds the first ancestor Render Product node by traversing upstream through inputs.

    Args:
        node (hou.Node): The starting node to search from.

    Returns:
        hou.Node: The first found Render Product node, or None if not found.
    """
    visited_nodes = set()
    queue = [node]

    while queue:
        current_node = queue.pop(0)

        if current_node in visited_nodes:
            continue
        visited_nodes.add(current_node)

        # Print the name of the current visited node
        # print(f"Visiting node: {current_node.path()} ({current_node.type().name()})")

        # Check if the current node is a Render Product node
        if current_node.type().name() == "renderproduct":
            # print(f"Found Render Product node: {current_node.path()}")
            return current_node

        # Add all input nodes to the queue to continue the search
        queue.extend(filter(None, current_node.inputs()))

    # print("No Render Product node found.")
    return None  # No Render Product node found


def set_image_output_override(node, **kwargs):
    """
    Sets the image output override for the render ROP node.

    Args:
        node (hou.Node): The Houdini node to set the image output override for.
    """
    try:
        node_type = get_node_type(node)
        node_list = get_node_list("image_output_source")
        logger.debug("node_type", node_type)
        if node_type in node_list:
            image_output_source = get_parameter_value(node, "image_output_source")

            logger.debug("image_output_source", image_output_source)
            if image_output_source in ["render_rop", "Render Rop"]:
                render_rop_info = get_render_rop_info(node)
                if render_rop_info:
                    image_output_override = render_rop_info.get("outputimage", None)
                    logger.debug("image_output_override", image_output_override)
                    node.parm("override_image_output").set(image_output_override)
            elif image_output_source in ["Default", "default"]:
                image_output_override = "$HIP/render/$HIPNAME.$OS.$F4.exr"
                logger.debug("image_output_override", image_output_override)
                node.parm("override_image_output").set(image_output_override)

    except Exception as e:
        logger.error(f"Error setting image output override: {e}")


def default_render_software(node, **kwargs):
    """
    Sets the render software for the render ROP node.

    Args:
        node (hou.Node): The Houdini node to set the render software for.
    """
    get_render_delegate(node)


def get_render_delegate(node):
    """
    Retrieves the render delegate for the render ROP node.

   """
    render_delegate = "BRAY_HdKarma"
    try:
        driver_path = get_parameter_value(node, "driver_path")
        # logger.debug("driver_path", driver_path)
        if driver_path:
            # get the "renderer" parameter from the driver path
            render_rop_node = hou.node(driver_path)
            if render_rop_node:
                render_delegate = get_parameter_value(render_rop_node, "renderer", string_value=True)
                # logger.debug("renderer", renderer)
                if render_delegate:
                    set_parameter_value(node, "render_delegate", render_delegate)

    except Exception as e:
        logger.error(f"Error setting render software: {e}")
    return render_delegate


def set_usd_path(node, **kwargs):
    """
    Sets the USD file path for the render ROP node.

    Args:
        node (hou.Node): The Houdini node to set the USD file path for.
    """
    try:
        usd_path = get_parameter_value(node, "usd_filepath")
        if usd_path:
            set_parameter_value(node, "usd_filepath", usd_path)
    except Exception as e:
        logger.error(f"Error setting USD path: {e}")
def set_render_software(node, **kwargs):
    """
    Sets the render software for the render ROP node.

    Args:
        node (hou.Node): The Houdini node to set the render software for.
    """
    logger.debug("Setting render software")
    software.ensure_valid_selection(node)

def get_render_rop_info(node):
    """
    Retrieves the render ROP options for the current render rop.

    Returns:
        dict: A dictionary containing the render ROP options for each node.
    """
    render_rop_info = {
        "renderer": None,
        "rendercommand": None,
        "outputimage": None,
        "firstframe": 1,
        "endframe": 1,
    }
    driver_type = None
    try:

        driver_path = get_parameter_value(node, "driver_path")
        if driver_path:
            render_rop_node = hou.node(driver_path)
            for key in render_rop_info:
                render_rop_info[key] = get_parameter_value(render_rop_node, key, string_value=True)
        # logger.debug("render_rop_info: ", render_rop_info)

    except Exception as e:
        logger.error(f"Error getting render rop info: {e}")

    return render_rop_info

"""
def set_default_render_rops(node, render_ropes_list):
    
    #Sets the default ROP options (output folder, render script, task template) for a given node.

    #Args:
    #    node (hou.Node): The Houdini node to set default ROP options for.
    #    render_ropes_list (list): A list of ROP paths associated with the node.
    
    try:
        output_folder = get_default_output_folder()
        render_script = get_default_render_script()
        # logger.debug("MARK: 2")
        task_template = get_default_task_template(node)

        node_name = node.name()

        if node_name not in render_rop_options:
            render_rop_options[node_name] = {}

        for key in render_ropes_list:
            if key not in render_rop_options[node_name]:
                render_rop_options[node_name][key] = {
                    "output_folder": output_folder,
                    "render_script": render_script,
                    "task_template": task_template,
                }
                node.parm("render_script").set(render_script)
                node.parm("task_template").set(task_template)
    except Exception as e:
        logger.error(f"Error setting default render rops: {e}")
"""

"""
def reset_render_rop_options(node):
    
    #Resets the render ROP options for the given node, clearing only the values associated
    #with the provided node's name in the render_rop_options dictionary.

    #Args:
    #    node (hou.Node): The Houdini node whose render ROP options are to be reset.
    
    try:
        node_name = node.name()
        if node_name in render_rop_options:
            render_rop_options[node_name] = {}
            logger.debug(f"Render ROP options for node '{node_name}' have been reset.")
    except Exception as e:
        logger.error(f"Error resetting render rop options for node '{node.name()}': {e}")
"""

"""
def update_render_rop_options(node, **kwargs):
    
    #Updates the render ROP options for a given node based on the current parameter values.
    #Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    #Args:
    #    node (hou.Node): The Houdini node whose render ROP options are to be updated.
    #    **kwargs: Additional keyword arguments for flexibility in the future.
    
    try:
        if not node:
            return
        node_name = node.name()

        output_folder = node.parm("output_folder").eval()
        render_script = node.parm("render_script").eval()
        task_template = node.parm("task_template").eval()

        node_type = get_node_type(node)
        node_list = get_node_list("render_rop_list")
        if node_type not in node_list:
            key = node.parm("render_rop_list").eval()

            # Check if the key exists before updating
            if key not in render_rop_options.get(node_name, {}):
                # Reinitialize if the key is missing
                set_default_render_rops(node, [key])

            render_rop_options[node_name][key]["output_folder"] = output_folder
            render_rop_options[node_name][key]["render_script"] = render_script
            render_rop_options[node_name][key]["task_template"] = task_template

    except Exception as e:
        logger.error(f"Error updating render rop options: {e}")
"""

"""
def get_render_rop_options(node, **kwargs):
    
    #Retrieves the render ROP options for a given node and applies them to the node's parameters.
    #Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    #Args:
    #    node (hou.Node): The Houdini node whose render ROP options are to be retrieved.
    #    **kwargs: Additional keyword arguments for flexibility in the future.
   
    try:
        node_name = node.name()
        key = node.parm("render_rop_list").eval()

        if key not in render_rop_options.get(node_name, {}):
            output_folder = get_default_output_folder()
            render_script = get_default_render_script()
            # logger.debug("MARK: 3")
            task_template = get_default_task_template(node)

            render_rop_options.setdefault(node_name, {})[key] = {
                "output_folder": output_folder,
                "render_script": render_script,
                "task_template": task_template,
            }

        options = render_rop_options[node_name][key]

        # Set evaluated parameters back to the node
        node.parm("output_folder").set(options["output_folder"])
        node.parm("render_script").set(options["render_script"])
        node.parm("task_template").set(options["task_template"])

    except Exception as e:
        logger.error(f"Error getting render rop options: {e}")
 """
def query_output_folder_original(node, rop_path=None):
    """
    Queries the output folder path for a given node and ROP path.
    Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    Args:
        node (hou.Node): The Houdini node to query.
        rop_path (str): The specific ROP path rop_path to look up.

    Returns:
        str: The output folder path if available, otherwise an empty string.
    """
    output_folder = ""
    try:
        #output_folder = get_parameter_value(node, "output_folder", string_value=True)

        image_path = get_parameter_value(node, "override_image_output", string_value=True)
        if image_path:
                output_folder = os.path.dirname(image_path)
                # Consider relative path
                if not os.path.isabs(output_folder):
                    hip_path = os.path.expandvars("$HIP")
                    output_folder = os.path.join(hip_path, output_folder)

        #if not output_folder:
        #    output_folder = get_default_output_folder()
    except Exception as e:
        logger.error(f"Error querying output folder: {e}")

    return output_folder



def query_output_folder(node, rop_path=None):
    """
    Queries the output folder path for a given node and ROP path.
    Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    Args:
        node (hou.Node): The Houdini node to query.
        rop_path (str): The specific ROP path rop_path to look up.

    Returns:
        str: The output folder path if available, otherwise an empty string.
    """
    output_folder = ""
    try:
        image_path = get_parameter_value(node, "override_image_output", string_value=True)

        if image_path:
            # Convert Houdini-style path to OS-compatible path
            image_path = os.path.normpath(image_path)
            # print("image_path:", image_path)

            # Extract the directory portion
            output_folder = os.path.dirname(image_path)
            # print("output_folder 1:", output_folder)

            # Handle relative paths correctly
            if not output_folder:
                hip_path = os.path.normpath(os.path.expandvars("$HIP"))
                output_folder = os.path.join(hip_path, output_folder)
                # print("output_folder 2:", output_folder)

            # Ensure consistent forward slashes for cross-platform compatibility
            output_folder = output_folder.replace("\\", "/")

    except Exception as e:
        logger.error(f"Error querying output folder: {e}")

    return output_folder



def query_render_script(node, key):
    """
    Queries the render script path for a given node and ROP path.
    Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    Args:
        node (hou.Node): The Houdini node to query.
        key (str): The specific ROP path key to look up.

    Returns:
        str: The render script path if available, otherwise the default render script.
    """
    render_script = ""
    try:
        render_script = get_default_render_script()
    except Exception as e:
        logger.error(f"Error querying render script: {e}")

    return render_script

def query_task_template(node, key):
    """
    Queries the task template for a given node and ROP path.
    Ensures that all Houdini parameters are evaluated to their resolved values (e.g., $HIP).

    Args:
        node (hou.Node): The Houdini node to query.
        key (str): The specific ROP path key to look up.

    Returns:
        str: The task template if available, otherwise the default task template.
    """
    task_template = ""
    try:
        task_template = get_default_task_template(node)
    except Exception as e:
        logger.debug(f"Error querying task template: {e}")

    return task_template


def copy_parameters(src_node, dest_node):
    """
    Copies parameter values from the source node to the destination node if the parameter exists in both nodes,
    skipping specific parameters such as 'asset_regex' and 'asset_excludes'.

    Args:
        src_node (hou.Node): The source node from which parameter values will be copied.
        dest_node (hou.Node): The destination node to which parameter values will be copied.
    """
    try:
        skip_params = {'asset_regex', 'asset_excludes'}

        for parm in src_node.parms():
            parm_name = parm.name()

            # Skip specific parameters
            if parm_name in skip_params:
                continue

            dest_parm = dest_node.parm(parm_name)
            if dest_parm:
                try:
                    dest_parm.set(parm.eval())
                except Exception as e:
                    logger.error(f"Error copying parameter '{parm_name}' from {src_node.path()} to {dest_node.path()}: {e}")
    except Exception as e:
        logger.error(f"Error copying parameters: {e}")


def generate_solaris_nodes_original(node, **kwargs):
    """
    Creates a subnet connected to the current node and adds conductor nodes inside
    the subnet for each ROP path, connecting them sequentially.

    Args:
        node (hou.Node): The Houdini node to which the subnet will be connected.
        **kwargs: Additional keyword arguments for future extensions.
    """
    try:
        # Create the subnet node
        parent = node.parent()
        subnet = parent.createNode("subnet", "solaris_subnet")
        subnet.moveToGoodPosition()

        # Remove default input nodes that may be created inside the subnet
        for child in subnet.children():
            if "input" in child.name():
                child.destroy()

        # Get the render ROP data from the node
        render_rops_data = render_rops.get_render_rop_data(node)
        # logger.debug("render_rops_data", render_rops_data)

        if not render_rops_data:
            logger.debug("No render ROP data found.")
            return None

        # Keep track of the last created node for connecting purposes
        previous_node = None

        # Iterate through each render ROP path and create a conductor node inside the subnet
        for index, render_rop in enumerate(render_rops_data):
            # logger.debug("-----------------------------------------")
            # logger.debug("Creating new Solaris node ...")
            rop_path = render_rop.get("path", None)
            # logger.debug("rop_path", rop_path)
            if not rop_path:
                continue

            # Get node name, for exammple if rop_path "/stage/usdrender_rop1" then node_name = "solaris_usdrender_rop1"
            node_name = f"conductor_{rop_path.split('/')[-1]}"
            # Create a new conductor node inside the subnet
            solaris_node = subnet.createNode("conductor::conductor_solaris_submitter::0.1", node_name, run_init_scripts=False)
            solaris_node.moveToGoodPosition()

            # Copy parameters from the original node to the newly created node
            copy_parameters(node, solaris_node)

            # Set the parameter after the node is created but before connections
            try:
                solaris_node.parm("driver_path").set(rop_path)
                # logger.debug("Setting driver_path to:", rop_path)
            except Exception as e:
                logger.error(f"Error setting driver_path for node {solaris_node.name()}: {e}")

            # Connect the nodes sequentially inside the subnet
            if previous_node:
                try:
                    solaris_node.setInput(0, previous_node)
                    # logger.debug(f"Connected {solaris_node.name()} to {previous_node.name()}")
                except Exception as e:
                    logger.error(f"Error connecting {solaris_node.name()} to {previous_node.name()}: {e}")

            # Re-set the parameter explicitly after connections
            try:
                solaris_node.parm("driver_path").set(rop_path)
                driver_path = solaris_node.parm("driver_path").eval()
                # logger.debug("Confirming: driver_path", driver_path)
            except Exception as e:
                logger.error(f"Error re-confirming driver_path for node {solaris_node.name()}: {e}")

            # Update the previous node for the next iteration
            previous_node = solaris_node

            # logger.debug("Successfully created the Solaris node.")

        # Layout the nodes for better visibility inside the subnet
        subnet.layoutChildren()

        # Connect the input of the subnet to the output of the current node
        try:
            subnet.setInput(0, node)
            # logger.debug(f"Connected subnet {subnet.name()} to {node.name()}")
        except Exception as e:
            logger.error(f"Error connecting subnet {subnet.name()} to {node.name()}: {e}")

        logger.debug("Successfully created the conductor subnet and connected the nodes.")

    except Exception as e:
        logger.error(f"Error generating Solaris nodes: {e}")

def generate_solaris_nodes(node, **kwargs):
    """
    Creates a subnet connected to the current node and adds conductor nodes inside
    the subnet for each ROP path, connecting them sequentially.

    Args:
        node (hou.Node): The Houdini node to which the subnet will be connected.
        **kwargs: Additional keyword arguments for future extensions.
    """
    try:
        # Check for existing subnets connected to the node
        existing_subnet_count = 0
        for output_node in node.outputs():
            if output_node.type().name() == "subnet":
                existing_subnet_count += 1

        # Determine the new subnet name based on the count of existing subnets
        subnet_rank = existing_subnet_count + 1
        subnet_name = f"solaris_subnet_{subnet_rank}"

        # Create the subnet node
        parent = node.parent()
        subnet = parent.createNode("subnet", subnet_name)
        subnet.moveToGoodPosition()

        # Remove default input nodes that may be created inside the subnet
        for child in subnet.children():
            if "input" in child.name():
                child.destroy()

        # Get the render ROP data from the node
        render_rops_data = render_rops.get_render_rop_data(node)

        if not render_rops_data:
            logger.debug("No render ROP data found.")
            return None

        # Keep track of the last created node for connecting purposes
        previous_node = None

        # Iterate through each render ROP path and create a conductor node inside the subnet
        for index, render_rop in enumerate(render_rops_data):
            rop_path = render_rop.get("path", None)
            if not rop_path:
                continue

            # Generate a unique name for each Solaris node, including the subnet rank
            base_node_name = f"conductor_{rop_path.split('/')[-1]}"
            node_name = f"{base_node_name}_{subnet_rank}"

            # Create a new conductor node inside the subnet
            solaris_node = subnet.createNode("conductor::conductor_solaris_submitter::0.1", node_name, run_init_scripts=False)
            solaris_node.moveToGoodPosition()

            # Copy parameters from the original node to the newly created node
            copy_parameters(node, solaris_node)

            # Set the parameter after the node is created but before connections
            try:
                solaris_node.parm("driver_path").set(rop_path)
            except Exception as e:
                logger.error(f"Error setting driver_path for node {solaris_node.name()}: {e}")

            # Connect the nodes sequentially inside the subnet
            if previous_node:
                try:
                    solaris_node.setInput(0, previous_node)
                except Exception as e:
                    logger.error(f"Error connecting {solaris_node.name()} to {previous_node.name()}: {e}")

            # Re-confirm the driver_path parameter
            try:
                solaris_node.parm("driver_path").set(rop_path)
            except Exception as e:
                logger.error(f"Error re-confirming driver_path for node {solaris_node.name()}: {e}")

            # Update the previous node for the next iteration
            previous_node = solaris_node

        # Layout the nodes for better visibility inside the subnet
        subnet.layoutChildren()

        # Connect the input of the subnet to the output of the current node
        try:
            subnet.setInput(0, node)
        except Exception as e:
            logger.error(f"Error connecting subnet {subnet.name()} to {node.name()}: {e}")

        logger.debug(f"Successfully created the subnet '{subnet_name}' and connected the nodes.")

    except Exception as e:
        logger.error(f"Error generating Solaris nodes: {e}")
