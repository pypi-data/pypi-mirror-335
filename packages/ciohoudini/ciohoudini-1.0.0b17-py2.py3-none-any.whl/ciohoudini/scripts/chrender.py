#!/usr/bin/env hython

"""Script to render a ROP.

# Task template should resolve to something like:
# hython "/Users/julian/Conductor/houdini/ciohoudini/scripts/chrender.py" -f 2 2 1 -d /out/mantra1 "/path/to/aaa_MantraOnly.hip"
"""
import subprocess
import sys
import os
import re
import argparse

from string import ascii_uppercase
import hou

SIM_TYPES = ("baketexture", "geometry", "output", "dop")

DRIVE_LETTER_RX = re.compile(r"^[a-zA-Z]:")




def error(msg):
    if msg:
        sys.stderr.write("\n")
        sys.stderr.write("Error: %s\n" % msg)
        sys.stderr.write("\n")
        sys.exit(1)


def usage(msg=""):
    sys.stderr.write(
        """Usage:

    hython /path/to/chrender.py -d driver -f start end step hipfile
    All flags/args are required

    -d driver:          Path to the output driver that will be rendered
    -f range:           The frame range specification (see below)
    hipfile             The hipfile containing the driver to render
    """
    )
    error(msg)


def prep_ifd(node):
    """Prepare the IFD (Mantra) ROP for rendering."""
    print("Preparing Mantra ROP node {}".format(node.name()))
    node.parm("vm_verbose").set(3)
    print("Set loglevel to 3")
    node.parm("vm_alfprogress").set(True)
    print("Turn on Alfred style progress")
    node.parm("soho_mkpath").set(True)
    print("Make intermediate directories if needed")


def prep_baketexture(node):
    """Prepare the BAKETEXTURE ROP for rendering."""
    pass


def prep_arnold(node):
    """Prepare the Arnold ROP for rendering."""

    print("Preparing Arnold ROP node {} ...".format(node.name()))

    try:
        if node is not None:
            print("Abort on license failure")
            node.parm("ar_abort_on_license_fail").set(True)
            print("Abort on error")
            node.parm("ar_abort_on_error").set(True)
            print("Log verbosity to debug")
            node.parm("ar_log_verbosity").set('debug')
            print("Enable log to console")
            node.parm("ar_log_console_enable").set(True)

            # Setting environment variable ARNOLD_ADP_DISABLE to True
            # Todo: This should have been implemented as a sidecar. Remove this once confirmed and tested.
            # print("Setting environment variable ARNOLD_ADP_DISABLE to True.")
            # os.environ['ARNOLD_ADP_DISABLE'] = '1'

            # Todo: should we allow this?
            # print("Setting environment variable ARNOLD_CER_ENABLED to False.")
            # os.environ['ARNOLD_CER_ENABLED'] = '0'

    except Exception as e:
        print("Error preparing Arnold ROP: {}".format(e))


def prep_redshift(node):
    """Prepare the redshift ROP for rendering."""
    print("Preparing Redshift ROP node {}".format(node.name()))

    print("Turning on abort on license fail")
    node.parm("AbortOnLicenseFail").set(True)

    print("Turning on abort on altus license fail")
    node.parm("AbortOnAltusLicenseFail").set(True)

    print("Turning on abort on Houdini cooking error")
    node.parm("AbortOnHoudiniCookingError").set(True)

    print("Turning on abort on missing resource")
    node.parm("AbortOnMissingResource").set(True)

    print("Turning on Redshift log")
    node.parm("RS_iprMuteLog").set(False)

def prep_karma(node):
    """Prepare the karma ROP for rendering."""
    print("Preparing Karma ROP node {}".format(node.name()))

    print("Turning on Abort for missing texture")
    node.parm("abortmissingtexture").set(True)

    print("Turning on make path")
    node.parm("mkpath").set(True)

    print("Turning on save to directory")
    node.parm("savetodirectory").set(True)

    print("Turning on Husk stdout")
    node.parm("husk_stdout").set(True)

    print("Turning on Husk stderr")
    node.parm("husk_stderr").set(True)

    print("Turning on Husk debug")
    node.parm("husk_debug").set(True)

    print("Turning on log")
    node.parm("log").set(True)

    print("Turning on verbosity")
    node.parm("verbosity").set(True)

    print("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)

    # Todo: should we allow this?
    # print("Turning on threads")
    # node.parm("threads").set(True)

def prep_usdrender(node):
    """Prepare the usdrender OUT for rendering."""
    print("Preparing usdrender OUT node {}".format(node.name()))

    print("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)

    print("Turning on Husk debug")
    node.parm("husk_debug").set(True)

    #print("Turning on verbosity")
    #node.parm("verbosity").set(True)

    print("Turning on husk_log")
    node.parm("husk_log").set(True)

    #print("Turning on Husk stdout")
    #node.parm("husk_stdout").set(True)

    #print("Turning on Husk stderr")
    #node.parm("husk_stderr").set(True)

    #print("Turning on Save Time Info")
    #node.parm("savetimeinfo").set(True)

    print("Turning on Make Path")
    node.parm("mkpath").set(True)



def prep_usdrender_rop(node):
    """Prepare the usdrender OUT for rendering."""
    print("Preparing usdrender rop node {}".format(node.name()))

    print("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)

    print("Turning on Husk debug")
    node.parm("husk_debug").set(True)


    print("Turning on husk_log")
    node.parm("husk_log").set(True)


    print("Turning on Make Path")
    node.parm("mkpath").set(True)


def prep_ris(node):
    """
    Prepares the Renderman ROP (RIS) for rendering by setting specific parameters.

    This function configures the Renderman ROP by adjusting its log level and enabling progress reporting. Additionally, it ensures that intermediate directories are created for each display defined in the ROP. This preparation is crucial for rendering tasks, ensuring that log verbosity is sufficient for debugging and that necessary directories are available for output files.

    Parameters:
    node (hou.Node): The Renderman ROP node to prepare.
    """
    print("Preparing Ris ROP node {}".format(node.name()))
    node.parm("loglevel").set(4)
    print("Set loglevel to 4")
    node.parm("progress").set(True)
    print("Turn progress on")
    num_displays = node.parm("ri_displays").eval()
    for i in range(num_displays):
        print("Set display {} to make intermediate directories if needed".format(i))
        node.parm("ri_makedir_{}".format(i)).set(True)


def prep_vray_renderer(node):
    """
    Prepares the V-Ray ROP for rendering.

    Currently, this function does not perform any preparation due to the lack of specific V-Ray parameters that need adjusting in this context. This placeholder indicates where V-Ray specific preparation steps would be implemented if needed.

    Parameters:
    node (hou.Node): The V-Ray ROP node to prepare.
    """

    print("Preparing V-Ray ROP node {}".format(node.name()))
    # I couldn't find a parameter to increase verbosity or set progress format.
    print("Nothing to do")



def prep_geometry(node):
    """
    Prepares the geometry ROP for rendering.

    This function is currently a placeholder and does not implement any preparation steps. It's intended to be a template for future implementations where specific preparation of the geometry ROP might be required.

    Parameters:
    node (hou.Node): The geometry ROP node to prepare.
    """
    pass


def prep_output(rop_node):
    """
    Prepares the output ROP for rendering.

    This function is currently a placeholder and does not implement any preparation steps. It serves as a template for future implementations where specific preparation of the output ROP might be necessary.

    Parameters:
    rop_node (hou.Node): The output ROP node to prepare.
    """
    pass


def prep_dop(node):
    """
    Prepares the DOP ROP for rendering by setting specific parameters.

    This function adjusts the DOP ROP to enable the creation of necessary directories, to render over a time range, and to report progress. These adjustments are crucial for dynamic simulations where output management and progress tracking are essential.

    Parameters:
    node (hou.Node): The DOP ROP node to prepare.
    """
    node.parm("trange").set(1)
    node.parm("mkpath").set(True)
    node.parm("alfprogress").set(True)


def prep_opengl(node):
    """
    Prepares the OpenGL ROP for rendering.

    This function is currently a placeholder and does not implement any preparation steps. It's intended to be a template for future implementations where specific preparation of the OpenGL ROP might be required.

    Parameters:
    node (hou.Node): The OpenGL ROP node to prepare.
    """
    pass


def run_driver_prep(rop_node):
    """
    Executes the appropriate preparation function for a given ROP based on its type.

    This function dynamically identifies and runs a preparation function specific to the type of the provided ROP node. It's designed to automate the setup process for different ROP types, enhancing rendering workflows. If no specific preparation function exists for the ROP type, the function silently completes without action.

    Parameters:
    rop_node (hou.Node): The ROP node for which to run preparation.
    """

    rop_type = rop_node.type().name().split(":")[0]
    try:
        fn = globals()["prep_{}".format(rop_type)]
        print("Running prep function for ROP type: {}".format(rop_type))
        print("Function: {}".format(fn))
    except KeyError:
        return
    try:
        fn(rop_node)

    except:
        sys.stderr.write(
            "Failed to run prep function for ROP type: {}. Skipping.\n".format(rop_type)
        )
        return



def is_sim(rop):
    """
   Determines if the given ROP is of a simulation type.

   This function checks the type of the provided ROP node against a predefined list of simulation types. It returns True if the ROP is identified as a simulation type, indicating that it may require specific handling during rendering processes.

   Parameters:
   rop (hou.Node): The ROP node to check.

   Returns:
   bool: True if the ROP is a simulation type, False otherwise.
   """
    return rop.type().name().startswith(SIM_TYPES)


def parse_args():
    """
    Parses command-line arguments for the script, ensuring required arguments are provided.

    This function sets up argument parsing for the script, specifying that the driver and hipfile are required arguments, while frames is an optional argument that expects three integer values. It uses the argparse library to define these requirements and handle parsing.

    Arguments:
    -d (str): The driver argument, required for operation.
    -f (int int int): A series of three integers representing the frame range, optional.
    hipfile (str): The path to the hip file, required.

    If any unknown arguments are provided, the script prints an error message indicating the unrecognized arguments and halts execution. This ensures that only the expected arguments are passed to the script.

    Returns:
    argparse.Namespace: An object containing the parsed arguments. This object will have attributes for 'driver', 'frames' (if provided), and 'hipfile'.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", dest="driver", required=True)
    parser.add_argument("-f", dest="frames", nargs=3, type=int)
    # parser.add_argument("-o", dest="override_image_output")
    parser.add_argument("hipfile", nargs=1)

    args, unknown = parser.parse_known_args()

    if unknown:
        usage("Unknown argument(s): %s" % (" ".join(unknown)))

    return args


def ensure_posix_paths():
    """
    Converts file paths in Houdini file references to POSIX format.

    This function iterates over all file references in the current Houdini session. For each reference, it checks if the path contains a Windows-style drive letter. If so, it strips the drive letter and converts backslashes to forward slashes, thereby converting the path to POSIX format. This conversion is essential for ensuring compatibility across different operating systems, particularly when moving projects from Windows to Unix-like systems.

    The function skips over references that do not contain a Windows-style drive letter or are part of nodes with a type that starts with "conductor::job", assuming these references do not require conversion. For each conversion, it prints both the original path and the converted path for verification purposes. If setting the new path fails, it catches the exception, prints an error message, and continues with the next file reference.
    """

    refs = hou.fileReferences()

    for parm, value in refs:
        if not parm:
            continue

        try:
            node_name = parm.node().name()
            parm_name = parm.name()
            node_type = parm.node().type().name()
        except:
            print("Failed to get parm info")
            continue
        ident = "[{}]{}.{}".format(node_type, node_name, parm_name)
        if node_type.startswith("conductor::job"):
            continue

        # Flag to track if "Not a drive letter" has been printed
        printed_not_a_drive_letter = False

        if not DRIVE_LETTER_RX.match(value):
            if not printed_not_a_drive_letter:
                # print("Not a drive letter. Skipping")
                printed_not_a_drive_letter = True
            continue

        print("{} Found a drive letter in path: {}. Stripping".format(ident, value))
        value = DRIVE_LETTER_RX.sub("", value).replace("\\", "/")
        print("{} Setting value to {}".format(ident, value))
        try:
            parm.set(value)
        except hou.OperationFailed as ex:
            print("{} Failed to set value for parm {}. Skipping".format(ident, value))
            print(ex)
            continue
        print("{} Successfully set value {}".format(ident, value))


def evaluate_custom_output_path(rop):
    """
    Evaluates and prints potential custom output paths for Arnold and USD render nodes in Houdini.
    This function handles various scenarios where the output path might be set dynamically using
    Houdini expressions, Python expressions, custom logic, and other mechanisms. The function
    checks for multiple cases and prints each potential output path it finds.

    Parameters:
    rop (hou.Node): The ROP (Render Output Operator) node to evaluate custom output paths for.
                    This node could be an Arnold ROP, USD ROP, or any node where the output path
                    might be influenced by custom settings or logic.

    The function considers the following cases:
    1. Direct Parameters and Expressions:
       - Evaluates direct Houdini expressions set in parameters like 'ar_picture'.

    2. Python Expressions in USD Context:
       - Evaluates Python expressions stored in parameters like 'outputimage' within a USD context.

    3. Dynamically Generated Paths:
       - Generates dynamic paths based on scene properties, such as the current frame number.

    4. Custom Attributes:
       - Checks for custom attributes that might define the output path.

    5. Naming Conventions and Patterns:
       - Handles custom naming patterns and replaces common tokens (e.g., $HIPNAME, $OS, $AOV).

    6. Scene Level Overrides:
       - Checks for scene-level overrides that might influence the output path.

    7. Camera-Specific Paths:
       - Evaluates output paths that are specific to certain cameras used in the scene.

    8. Render Product Primitives in USD:
       - Traverses the USD stage to find RenderProduct primitives that define output paths.

    9. Dependencies and External Files:
       - Checks for output paths that are influenced by linked dependencies or external files.

    10. AOV and Render Layer Specific Paths:
        - Evaluates paths for AOVs (Arbitrary Output Variables) and different render layers.

    11. Per-Frame or Per-Sequence Paths:
        - Handles paths that vary based on the frame or sequence being rendered.

    12. Configuration File Paths:
        - Evaluates paths that are defined or overridden by external configuration files.

    13. HDA-Specific Output Paths:
        - Handles output paths set by Houdini Digital Assets (HDAs) and their parameters.

    14. Render Manager or Farm-Specific Paths:
        - Checks for paths that might be set or influenced by render farm settings or render managers.

    15. Pre/Post-Render Script Paths:
        - Evaluates paths that are modified or set by scripts run before or after rendering.

    16. User-Defined Paths and Templates:
        - Handles user-defined templates or project settings that influence output paths.

    17. Multipass Rendering Paths:
        - Evaluates paths for multipass renders, where different passes might be saved separately.

    18. Node-Specific Output Paths:
        - Checks for paths that are set by specific attributes or settings on the node itself.

    Exceptions:
    - The function includes error handling for evaluating expressions and other dynamic content. If an error occurs,
      it prints a message indicating the issue but continues to evaluate other cases.

    Returns:
    None: The function does not return a value. Instead, it prints each detected output path.
    """
    try:
        # Example 1: Evaluating a Houdini expression in a parameter
        if rop.parm("ar_picture"):
            output_path = rop.parm("ar_picture").eval()
            if output_path:
                print(f"Custom evaluated output path from ar_picture: {output_path}")

        # Example 2: Evaluating a Python expression within a USD context
        if rop.parm("outputimage"):
            python_expression = rop.parm("outputimage").unexpandedString()
            if "eval" in python_expression:
                try:
                    evaluated_path = eval(python_expression)
                    if evaluated_path:
                        print(f"Custom evaluated output path from Python expression: {evaluated_path}")
                except Exception as eval_error:
                    print(f"Error evaluating Python expression: {str(eval_error)}")

        # Example 3: Dynamically generating the path based on scene properties
        current_frame = hou.frame()
        if rop.parm("arnold_rendersettings:productName"):
            base_path = rop.parm("arnold_rendersettings:productName").eval()
            dynamic_path = f"{base_path}_frame_{current_frame}"
            print(f"Custom dynamically generated output path: {dynamic_path}")

        # Example 4: Handling any other custom attributes
        if rop.hasParm("custom_output_path"):
            custom_path = rop.parm("custom_output_path").eval()
            if custom_path:
                print(f"Custom output path from custom attribute: {custom_path}")

        # Example 5: Custom naming conventions or patterns
        if rop.parm("output_template"):
            output_template = rop.parm("output_template").evalAsString()
            if output_template:
                # Replace common tokens
                output_path = output_template.replace("$HIPNAME", hou.hipFile.basename())
                output_path = output_path.replace("$OS", rop.name())
                output_path = output_path.replace("$AOV", "beauty")
                print(f"Custom output path from naming pattern: {output_path}")

        # Example 6: Scene level overrides
        if rop.hasParm("scene_override"):
            override_path = rop.parm("scene_override").eval()
            if override_path:
                print(f"Custom output path from scene level override: {override_path}")

        # Example 7: Camera-specific output paths
        if rop.hasParm("camera_output_path"):
            camera_path = rop.parm("camera_output_path").eval()
            if camera_path:
                print(f"Custom output path based on camera: {camera_path}")

        # Example 8: Render Product Primitives in USD
        usd_stage = rop.stage()
        if usd_stage:
            for prim in usd_stage.Traverse():
                if prim.GetTypeName() == "RenderProduct":
                    output_path = prim.GetAttribute("productName").Get()
                    if output_path:
                        print(f"Custom output path from RenderProduct primitive: {output_path}")

        # Example 9: Handling dependencies and external files
        if rop.parm("dependency_output_path"):
            dependency_path = rop.parm("dependency_output_path").eval()
            if dependency_path:
                print(f"Custom output path from linked dependencies: {dependency_path}")

        # Example 10: AOV and Render Layer specific paths
        if rop.parm("aov_output_path"):
            aov_path = rop.parm("aov_output_path").eval()
            if aov_path:
                print(f"Custom output path for AOVs: {aov_path}")

        # Example 11: Per-frame or Per-sequence paths
        if rop.parm("frame_output_path"):
            frame_output_path = rop.parm("frame_output_path").eval()
            if frame_output_path:
                print(f"Custom output path for frames: {frame_output_path}")

        # Example 12: Configuration file paths
        if rop.parm("config_output_path"):
            config_output_path = rop.parm("config_output_path").eval()
            if config_output_path:
                print(f"Custom output path from configuration file: {config_output_path}")

        # Example 13: HDA-specific output paths
        if rop.parm("hda_output_path"):
            hda_output_path = rop.parm("hda_output_path").eval()
            if hda_output_path:
                print(f"Custom output path from HDA: {hda_output_path}")

        # Example 14: Render manager or farm-specific paths
        if rop.parm("farm_output_path"):
            farm_output_path = rop.parm("farm_output_path").eval()
            if farm_output_path:
                print(f"Custom output path from render farm settings: {farm_output_path}")

        # Example 15: Pre/Post-render script paths
        if rop.parm("script_output_path"):
            script_output_path = rop.parm("script_output_path").eval()
            if script_output_path:
                print(f"Custom output path from pre/post-render script: {script_output_path}")

        # Example 16: User-defined paths and templates
        if rop.parm("user_template_path"):
            user_template_path = rop.parm("user_template_path").eval()
            if user_template_path:
                print(f"Custom output path from user-defined template: {user_template_path}")

        # Example 17: Multipass rendering paths
        if rop.parm("multipass_output_path"):
            multipass_path = rop.parm("multipass_output_path").eval()
            if multipass_path:
                print(f"Custom output path for multipass rendering: {multipass_path}")

        # Example 18: Node-specific output paths
        if rop.parm("node_specific_output"):
            node_specific_path = rop.parm("node_specific_output").eval()
            if node_specific_path:
                print(f"Custom output path from node-specific settings: {node_specific_path}")

    except Exception as e:
        print(f"Error evaluating custom output path: {str(e)}")


def get_usd_output_path(rop):
    """
    Prints the output path from the USD Render ROP by resolving the USD stage and traversing it
    to find relevant render settings. It also checks for external references, sublayers, environment
    variables, and other scenarios where the output path may be set.

    Parameters:
    rop (hou.Node): The USD Render ROP node to extract the output path from.

    Returns:
    None
    """
    try:
        usd_stage = rop.stage()
        if not usd_stage:
            print("No USD stage found.")
            return

        print("Checking direct parameters on the ROP node...")
        output_parm = rop.parm("outputimage")
        if output_parm and output_parm.eval():
            print(f"Direct parameter output path: {output_parm.eval()}")
        else:
            print("No output path found in direct parameters.")

        print("Traversing the USD stage for render settings...")
        found_path = False
        for prim in usd_stage.Traverse():
            for attr_name in [
                'arnold_rendersettings:productName',
                'arnold_rendersettings.productName',
                'outputs:ri:displays:beauty:filePath',  # Renderman
                'outputs:karma:productName',  # Karma
                'outputs:image:file'  # Generic output path
            ]:
                if prim.HasAttribute(attr_name):
                    output_path = prim.GetAttribute(attr_name).Get()
                    if output_path:
                        print(f"Found output path in USD stage for {attr_name}: {output_path}")
                        found_path = True
                        break
        if not found_path:
            print("No output path found in USD stage.")

        print("Checking external references and sublayers for render settings...")
        found_path = False
        for layer in usd_stage.GetLayerStack():
            for prim in layer.Traverse():
                for attr_name in [
                    'arnold_rendersettings:productName',
                    'arnold_rendersettings.productName',
                    'outputs:ri:displays:beauty:filePath',
                    'outputs:karma:productName',
                    'outputs:image:file'
                ]:
                    if prim.HasAttribute(attr_name):
                        output_path = prim.GetAttribute(attr_name).Get()
                        if output_path:
                            print(f"Found output path in referenced layer for {attr_name}: {output_path}")
                            found_path = True
                            break
        if not found_path:
            print("No output path found in external references or sublayers.")

        print("Checking environmental variables...")
        if 'ARNOLD_OUTPUT_PATH' in os.environ:
            print(f"Output path from environment variable 'ARNOLD_OUTPUT_PATH': {os.environ['ARNOLD_OUTPUT_PATH']}")
        else:
            print("No output path found in environment variables.")

        print("Evaluating custom output path logic...")
        custom_output_path = evaluate_custom_output_path(rop)
        if custom_output_path:
            print(custom_output_path)
        else:
            print("No output path found in custom logic.")

    except Exception as e:
        print(f"Error resolving USD output path: {str(e)}")


def print_output_path(rop):
    """
    Prints the output path where the specified ROP node is saving rendered images or data files.

    This function checks for common output parameters used by various rendering engines or output
    drivers within Houdini. If it's a USD Render ROP, it resolves the USD stage to find the output path,
    including searching through referenced USD files, environment variables, custom logic, and more.

    Parameters:
    rop (hou.Node): The ROP node whose output path is to be printed.

    Returns:
    None
    """
    try:
        output_parm = None
        # Check common output parameters used by different ROPs
        for parm in [
            "vm_picture",  # Mantra ROP
            "RS_outputFileNamePrefix",  # Redshift ROP
            "ar_picture",  # Arnold ROP
            "ri_display_0_name",  # Renderman ROP
            "SettingsOutput_img_file_path",  # V-Ray ROP
            "vm_uvoutputpicture1",  # Bake Texture ROP
            "picture",  # Karma ROP, OpenGL ROP
            "outputimage",  # USD Render ROP
            "lopoutput",  # USD Render LOP
            "sopoutput",  # Geometry ROP
            "dopoutput"  # Output ROP, DOP ROP (Simulation)
        ]:
            if rop.parm(parm):
                output_parm = rop.parm(parm)
                break

        if output_parm:
            # Evaluate the output path and print it
            output_path = output_parm.eval()
            print("ROP '{}' will write to: {}".format(rop.name(), output_path))
        elif rop.type().name() in ["usdrender", "usdrender_rop"]:
            # If it's a USD Render ROP, resolve the USD stage and find the output path
            get_usd_output_path(rop)
        else:
            # If no recognized parameter is found
            print("ROP '{}' does not have a recognized output parameter.".format(rop.name()))

    except Exception as e:
        # Catch and print any errors that occur
        print("Error occurred while retrieving the output path for ROP '{}': {}".format(rop.name(), str(e)))




def render(args):
    """
    Render the specified Render Operator (ROP) within a Houdini scene based on the arguments provided.

    This function takes command line arguments to specify the Houdini project file (.hip file),
    the driver node (ROP) to render, and the frame range for rendering. It attempts to load the
    specified .hip file and, if successful, proceeds to render the specified ROP. If the .hip file
    loads with only warnings, it prints these warnings and continues with the rendering process.
    If the specified ROP does not exist, it lists the available ROPs in the scene.

    Parameters:
        args: A namespace object containing the following attributes:
            - hipfile (str): The path to the .hip file to be loaded.
            - driver (str): The path to the ROP node that will be rendered.
            - frames (tuple): A tuple specifying the start frame, end frame, and frame step.

    Note:
        If the .hip file contains unknown assets or nodes that only produce warnings upon loading,
        these warnings are printed out.

    Raises:
        hou.LoadWarning: If there are any issues loading the .hip file, a warning is printed,

    """

    # Unpack the arguments
    hipfile = args.hipfile[0]
    driver = args.driver
    frames = args.frames
    # override_image_output = args.override_image_output

    # Print out the arguments
    print("hipfile: '{}'".format(hipfile))
    print("driver: '{}'".format(driver))
    print("frames: 'From: {} to: {}'by: {}".format(*frames))
    # print("override_image_output: '{}'".format(override_image_output))

    # Load the hip file
    try:
        hou.hipFile.load(hipfile)
    except Exception as e:
        sys.stderr.write("Error: %s\n" % e)


    rop = hou.node(driver)
    if rop:
        print_output_path(rop)
        # render_rop(rop, frames)
        render_rop(rop, frames)
    # If the specified ROP does not exist, print the available ROPs in the scene.
    else:
        print_available_rops()
        return


def print_available_rops():
    """
    Prints the list of available Render Operators (ROPs) in the current Houdini session to stderr.

    This function attempts to retrieve and list all ROP nodes available within the scene. If any
    error occurs during the retrieval process, it prints an error message indicating the failure
    to list the available ROPs.

    Note:
        This function is typically called when a specified ROP does not exist or cannot be found,
        to assist the user in identifying the correct ROP to use.

    Raises:
        Exception: If an error occurs while attempting to retrieve the list of available ROPs,
                    an error message is printed to stderr.
    """
    try:
        msg = "ROP does not exist: '{}' \n".format(driver)
        sys.stderr.write(msg)
        # Print out the available ROPs
        all_rops = hou.nodeType(hou.sopNodeTypeCategory(), "ropnet").instances()
        sys.stderr.write("Available ROPs:\n")
        for r in all_rops:
            sys.stderr.write("  {}\n".format(r.path()))
        return
    except Exception as e:
        sys.stderr.write("Failed to get available ROPs\n")

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

def run_usd_image_output_prep(rop):

    # Get rop type
    image_output = default_image_output = "$HIP/render/$HIPNAME.$OS.$F4.exr"
    try:
        rop_type = rop.type().name()
        if rop_type in ["usdrender_rop"]:
            print("Preparing image output for USD ROP node {}".format(rop.name()))
            parm = rop.parm("outputimage")
            if parm:
                image_output = parm.unexpandedString()
                if image_output:
                    print(f"Image output from USD ROP: {image_output}")
                else:
                    parm.set(default_image_output)
                    print(f"default image output: {default_image_output}")
                    render_product_node = find_ancestor_render_product(rop)
                    if render_product_node:
                        image_output_parm  = render_product_node.parm("productName")
                        if image_output_parm:
                            image_output = image_output_parm.unexpandedString()
                            print(f"Image output from Render Product node: {image_output}")
                            if image_output:
                                parm.set(image_output)
    except Exception as e:
        print(f"Error running USD image output prep: {str(e)}")
    return  image_output





def render_rop(rop, frames):
    """
    Executes the rendering process for a specified Render Operator (ROP) based on a provided frame range.

    This function is responsible for rendering a specific ROP node within a Houdini scene. It ensures that all
    file paths are POSIX-compliant, runs any driver-specific preparation tasks, and then initiates the rendering
    process. The function handles different types of ROPs as follows:

    - If the ROP node is of type 'topnet', it uses the cook() method to process the TOP network.
    - If the ROP node is a simulation type, identified by the is_sim() function, it uses the render() method
      without a frame range.
    - For all other ROP types, it uses the render() method with the specified frame range.

    Parameters:
        rop (hou.Node): The ROP node to be rendered.
        frames (tuple): A tuple specifying the start frame, end frame, and frame step for the render.

    Note:
        This function assumes that all necessary preparations for rendering (such as path normalization
        and driver-specific preparations) are completed within it.

    Raises:
        hou.OperationFailed: If the rendering process encounters an error, an exception is caught and
                             an error message is printed to stderr. The function then exits without
                             completing the render process.

    Example:
        render_rop(rop_node, (1, 100, 1))
        This would render the specified ROP node from frame 1 to frame 100 with a step of 1.
    """
    try:
        print("Ensure POSIX paths")
        ensure_posix_paths()
        run_driver_prep(rop)

        run_usd_image_output_prep(rop)

        # Save the hip file after setting the image output
        hou.hipFile.save()

        # Prepare the ROP for rendering based on its type
        # If the ROP is a TOP network, use cookWorkItems() instead of render
        if rop.type().name() == "topnet":
            rop.displayNode().cookWorkItems(block=True)
        # If the ROP is a simulation type, render without a frame range
        elif is_sim(rop):
            rop.render(verbose=True, output_progress=True)
        # Otherwise, render with the specified frame range
        else:
            rop.render(
                frame_range=tuple(frames),
                verbose=True,
                output_progress=True,
                method=hou.renderMethod.FrameByFrame,
            )
    except hou.OperationFailed as e:
        sys.stderr.write("Error rendering the rop: %s\n" % e)
        return


render(parse_args())
