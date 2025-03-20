import hou
import re
import os
from ciopath.gpath_list import PathList, GLOBBABLE_REGEX
from ciopath.gpath import Path
from ciohoudini import common, rops, util

import ciocore.loggeria

import pxr.UsdUtils

logger = ciocore.loggeria.get_conductor_logger()

# Parms that don't have a string type of 'File' won't be returned by hou.fileReferences()
# Additional parms can be added to this dict in the format:
# {node_type: (parm1, parm2, etc...)}
ADDITIONAL_PATH_PARMS = {
    'Lop/reference::2.0': ('filepath1',)
}



def resolve_payload(node, **kwargs):
    """
    Resolve the upload_paths field for the payload.
    """
    # print("Assets resolve_payload ... ")
    rop_path = kwargs.get("rop_path", None)
    # print("Assets: rop_path: {}".format(rop_path))
    path_list = PathList()
    path_list.add(*auxiliary_paths(node, rop_path))

    path_list.add(*add_usd_file(node))

    path_list.add(*extra_paths(node))

    do_asset_scan = kwargs.get("do_asset_scan", False)
    # do_asset_scan = True
    # do_asset_scan = rops.get_parameter_value(node, "do_asset_scan")
    if do_asset_scan:
        path_list.add(*scan_paths(node, path_list))

    # Get the output folder
    expanded_path = get_output_folder(node)
    output_folder = Path(expanded_path)

    # Convert paths to strings
    current_assets = []
    for path in path_list:
        path = str(path)
        path = path.replace("\\", "/")
        if path not in current_assets:
            current_assets.append(path)
    # print("current_assets: {}".format(current_assets))

    # Filter out paths that are within the output folder
    # Todo: add this to validation as a warning
    filtered_paths = [path for path in current_assets if not is_within_output_folder(path, output_folder)]

    if len(current_assets) > len(filtered_paths):
        node.parm("output_excludes").set(0)

    # print("filtered assets: {}".format(filtered_paths))

    return {"upload_paths": filtered_paths}


def is_within_output_folder(path, output_folder):
    # Normalize the paths to handle different platforms and spaces
    normalized_path = os.path.normpath(str(path))  # Convert path to string
    normalized_output_folder = os.path.normpath(str(output_folder))  # Convert path to string

    # Check if the normalized path is within the normalized output folder
    result = normalized_path.startswith(normalized_output_folder)
    return result


def auxiliary_paths(node, rop_path):
    """
    Add the hip file, the OCIO file, and the render script to the list of assets.
    """

    path_list = PathList()

    # print("Assets: node_type: {}".format(node_type))
    # If the node is a husk, we don't need to add the hip file, OCIO file, or render script

    node_type = rops.get_node_type(node)
    if node_type in ["husk"]:
        usd_only = rops.get_parameter_value(node, "use_usd_scrapping_only")
        if usd_only:
            logger.debug("Scrapping USD only")
            return path_list

    try:
        path_list.add(hou.hipFile.path())

        ocio_file = os.environ.get("OCIO")
        if ocio_file:
            path_list.add(os.path.dirname(ocio_file))

        render_script = node.parm("render_script").eval()
        # render_script = rops.query_render_script(node, rop_path)
        # print("Assets: render_script: {}".format(render_script))

        if render_script:
            # Make the render script optional, by putting the last char in sq brackets
            render_script = "{}[{}]".format(render_script[:-1], render_script[-1])
            path_list.add(render_script)

        if path_list:
            path_list = _resolve_absolute_existing_paths(path_list)

        exclude_pattern = node.parm("asset_excludes").unexpandedString()
        if exclude_pattern:
            path_list.remove_pattern(exclude_pattern)
    except Exception as e:
        logger.error("Error while getting auxiliary paths: %s", e)

    return path_list

def add_usd_file(node):
    """
    Add the USD file to the list of assets.
    """

    path_list = PathList()
    try:
        node_type = rops.get_node_type(node)
        node_list = rops.get_node_list("usd_filepath")
        # print("node_type: {}".format(node_type))
        if node_type in node_list:
            # print("Adding USD file asset ... ")
            # usd_file = rops.get_parameter_value(node, "usd_filepath", string_value=True)
            usd_file = rops.get_parameter_value(node, "usd_filepath")
            # print("usd_file: {}".format(usd_file))
            if usd_file:
                path_list.add(usd_file)
                # print("USD file added to path_list: {}".format(path_list))
                if path_list:
                    path_list = _resolve_absolute_existing_paths(path_list)
                    # print("USD file path_list resolved: {}".format(path_list))
    except Exception as e:
        logger.error("Error while adding USD file: %s", e)

    return path_list
def scan_usd_files_with_hip_name(node):
    """
    Scan for USD files that contain the HIP file name in the same folder as the HIP file.
    """
    result = PathList()
    try:
        # Get the current HIP file path and its name
        hip_file_path = hou.hipFile.path()
        hip_dir = os.path.dirname(hip_file_path)
        hip_name = os.path.splitext(os.path.basename(hip_file_path))[0]

        # Check for USD files in the HIP folder that match the pattern
        for file in os.listdir(hip_dir):
            if file.endswith('.usd') and hip_name in file:
                usd_file_path = os.path.join(hip_dir, file)
                logger.debug(f"Found USD file: {usd_file_path}")
                result.add(usd_file_path)

        result = _resolve_absolute_existing_paths(result)
    except Exception as e:
        logger.error("Error while scanning for USD files with HIP name: %s", e)

    return result

def extra_paths(node, **kwargs):
    path_list = PathList()
    try:
        num = node.parm("extra_assets_list").eval()
        for i in range(1, num + 1):
            asset = node.parm("extra_asset_{:d}".format(i)).eval()
            asset = os.path.expandvars(asset)
            if asset:
                path_list.add(asset)

        if path_list:
            path_list = _resolve_absolute_existing_paths(path_list)
    except Exception as e:
        logger.error("Error while getting extra paths: %s", e)

    return path_list


def scan_paths(node, result):
    """
    Scans and collects file paths referenced by the given node, including USD dependencies.

    This function gathers file references from parameters, applies a regex pattern to
    standardize paths, resolves nested USD dependencies, filters paths based on exclude
    patterns, and converts the resulting paths to absolute and existing ones.

    Args:
        node: A Houdini node object containing parameters that reference file paths.

    Returns:
        PathList: A list of resolved file paths, including nested USD dependencies,
                  with excluded paths removed.

    Workflow:
        - Retrieves file reference parameters and additional file reference parameters.
        - Applies a regex pattern defined in the node to identify variable parts in the paths.
        - Resolves and adds file paths to a result set.
        - Identifies and resolves nested USD dependencies for USD-based file references.
        - Resolves paths to absolute existing file paths.
        - Excludes paths that match the exclude pattern specified in the node.

    Error Handling:
        - Logs errors encountered during different stages of the path scanning process,
          including file reference evaluation, USD dependency resolution, and path exclusion.

    Notes:
        - The function is designed to handle potentially expensive dependency scanning,
          making it suitable for tasks where performance is not critical.
        - The `asset_regex` parameter defines the regex pattern for file path evaluation.
        - The `asset_excludes` parameter specifies patterns to exclude paths.

    Exceptions:
        - Errors encountered during parameter evaluation, USD dependency resolution, or
          exclude pattern application are logged, but the function continues processing
          unaffected components.

    Example:
        result = scan_paths(hou.node("/obj/geo1"))
    """

    #result = PathList()
    scan_files = True

    node_type = rops.get_node_type(node)
    if node_type in ["husk"]:
        parm = node.parm("use_usd_scrapping_only")
        if parm:
            if parm.eval():
                logger.debug("Scrapping USD only")
                scan_files = False

    try:
        #if node_type not in ["solaris", "rop", "husk"] and scan_files:
        if node_type not in ["generator"] and scan_files:
        #if node_type not in ["generator"]:
            parms = _get_file_ref_parms()
            parms.extend(_get_additional_file_ref_parms())

            # regex to find all patterns in an evaluated filename that could represent a varying parameter.
            regex = node.parm("asset_regex").unexpandedString()
            REGEX = re.compile(regex, re.IGNORECASE)

            for parm in parms:
                logger.debug("Evaluating %s", parm)
                evaluated = parm.eval()
                logger.debug("Scraping '%s'. Found path '%s'", parm, evaluated)
                if evaluated:
                    pth = REGEX.sub(r"*", evaluated)
                    if is_path_ok(pth):
                        result.add(pth)
                    else:
                        pass
                        # print("Skipping path: {}".format(pth))
    except Exception as e:
        logger.error("Error while scanning assets: %s", e)


    try:
        # Find all nested USD references
        if node_type in ["husk"]:
            usd_dependencies = set()
            # Find all nested USD references
            for file_path in result:
                file_path = str(file_path)

                logger.debug("Is %s (%s) a USD file?", file_path, type(file_path))

                if os.path.splitext(file_path)[-1] in (".usd", ".usda", ".usdc", ".usdz"):
                    logger.debug("Computing dependencies for %s", file_path)
                    layers, assets, unresolved_paths = pxr.UsdUtils.ComputeAllDependencies(file_path)

                    for l in layers:
                        usd_dependencies.add(l.realPath)

                    usd_dependencies.update(set(assets))

            for p in usd_dependencies:
                logger.debug("Adding USD nest asset: %s", p)
                result.add(p)
    except Exception as e:
        logger.error("Error while scanning USD assets: %s", e)

    result = _resolve_absolute_existing_paths(result)

    try:
        exclude_pattern = node.parm("asset_excludes").unexpandedString()
        if exclude_pattern:
            result.remove_pattern(exclude_pattern)
    except Exception as e:
        logger.error("Error while excluding  paths: %s", e)

    return result


def _get_file_ref_parms():
    parms = []
    refs = hou.fileReferences()
    for parm, _ in refs:
        if not parm:
            continue
        # if parm.node().type().name().startswith("conductor::job"):
        if parm.node().type().name().startswith("conductor"):
            continue
        parms.append(parm)
    return parms

def _get_additional_file_ref_parms():
    parms = []
    try:
        for node_type_name, node_parms in ADDITIONAL_PATH_PARMS.items():

            logger.debug("Looking for parameter '%s' in nodes of type '%s'", node_parms, node_type_name)

            node_type = hou.nodeType(node_type_name)

            if node_type is None:
                logger.warning("Uknown node type: '{}'".format(node_type_name))
                continue

            for node in node_type.instances():
                logger.debug("Scraping node %s", node)
                for parm_name in node_parms:
                    additional_parm = node.parm(parm_name)
                    logger.debug("Adding additional parm for scraping: '%s'", additional_parm)
                    parms.append(additional_parm)
    except Exception as e:
        logger.error("Error while getting additional file ref parms: %s", e)

    return parms

def clear_all_assets(node, **kwargs):
    node.parm("extra_assets_list").set(0)


def browse_files(node, **kwargs):
    files = hou.ui.selectFile(
        title="Browse for files to upload",
        collapse_sequences=True,
        file_type=hou.fileType.Any,
        multiple_select=True,
        chooser_mode=hou.fileChooserMode.Read,
    )
    if not files:
        return
    files = [f.strip() for f in files.split(";") if f.strip()]
    add_entries(node, *files)


def browse_folder(node, **kwargs):
    files = hou.ui.selectFile(title="Browse for folder to upload", file_type=hou.fileType.Directory)
    if not files:
        return
    files = [f.strip() for f in files.split(";") if f.strip()]
    add_entries(node, *files)


def add_entries(node, *entries):
    """
    Add entries to the asset list.

    These new entries and the existing entries are deduplicated. PathList object automatically
    deduplicates on access.
    """

    path_list = PathList()
    try:
        num = node.parm("extra_assets_list").eval()
        for i in range(1, num + 1):
            asset = node.parm("extra_asset_{:d}".format(i)).eval()
            asset = os.path.expandvars(asset)
            if asset:
                path_list.add(asset)

        for entry in entries:
            path_list.add(entry)

        paths = [p.fslash() for p in path_list]

        node.parm("extra_assets_list").set(len(paths))
        for i, arg in enumerate(paths):
            index = i + 1
            node.parm("extra_asset_{:d}".format(index)).set(arg)
    except Exception as e:
        logger.error("Error while adding entries: %s", e)


def remove_asset(node, index):
    try:
        curr_count = node.parm("extra_assets_list").eval()
        for i in range(index + 1, curr_count + 1):
            from_parm = node.parm("extra_asset_{}".format(i))
            to_parm = node.parm("extra_asset_{}".format(i - 1))
            to_parm.set(from_parm.unexpandedString())
        node.parm("extra_assets_list").set(curr_count - 1)
    except Exception as e:
        logger.error("Error while removing asset: %s", e)


def add_hdas(node, **kwargs):
    """
    Add all hda folders to the asset list.

    Called from a button in the UI. It's just a convenience. User could also browse for HDAs by
    hand.
    """

    hda_paths = [hda.libraryFilePath() for hda in common.get_plugin_definitions()]
    if not hda_paths:
        return

    add_entries(node, *hda_paths)


def _resolve_absolute_existing_paths(path_list):
    """
    Resolve all absolute paths in the list to their canonical form.

    This is necessary because Houdini stores absolute paths in the file references, but the
    canonical form is what we want to upload.

    Prefix any relative paths with HIP. It's the best we can do for now.
    However, some relative paths may be internal stuff like op:blah or temp:blah,
    we'll ignore them for now.
    """
    hip = hou.getenv("HIP")
    job = hou.getenv("JOB")
    internals = ("op:", "temp:")

    resolved = PathList()
    try:
        for path in path_list:
            if path.relative:
                if not path.fslash().startswith(internals):
                    resolved.add(
                        os.path.join(hip, path.fslash()),
                        os.path.join(job, path.fslash()),
                    )
            else:
                resolved.add(path)

        resolved.remove_missing()
        resolved.glob()
    except Exception as e:
        logger.error("Error while resolving absolute existing paths: %s", e)
    return resolved


def expand_env_vars(path):
    """
    Expand environment variables in the given path string.
    """
    return os.path.expandvars(path)

def get_output_folder(node):
    """
    Get the output folder from the node.
    """
    # default output folder
    output_folder = "$HIP/render"
    image_output = rops.get_parameter_value(node, "override_image_output")
    if image_output:
        # get the directory of the image output
        output_folder = os.path.dirname(image_output)
    output_folder = os.path.expandvars(output_folder)
    return output_folder


def is_path_ok(file_path):
    """
    Scans for asset dependencies and filters out unwanted paths.
    """

    file_path = file_path.replace("\\", "/")  # Normalize slashes

    if "*" in file_path:  # Skip wildcard paths
        # logger.debug(f"Skipping wildcard path: {file_path}")
        return False

    if file_path.startswith("/tmp/"):  # Skip temporary files
        # logger.debug(f"Skipping temporary file: {file_path}")
        return False

    if "houdini_temp" in file_path:  # Skip Houdini temp folder
        # logger.debug(f"Skipping Houdini temp file: {file_path}")
        return False


    return True


