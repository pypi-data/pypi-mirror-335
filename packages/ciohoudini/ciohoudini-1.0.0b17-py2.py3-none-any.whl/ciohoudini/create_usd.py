
import hou
import os

from ciohoudini import (
    render_rops,
    rops,
)


def browse_usd_file(node, **kwargs):
    # File extensions to allow
    valid_extensions = (".usd", ".usda", ".usdc", ".usdz")

    # Browse for a single file
    file_path = hou.ui.selectFile(
        title="Browse for a USD file to upload",
        file_type=hou.fileType.Any,
        chooser_mode=hou.fileChooserMode.Read,
        multiple_select=False,  # Allow only one file
    )

    if not file_path:
        # User canceled the file selection
        return

    file_path = file_path.strip()

    # Validate file extension
    if not file_path.lower().endswith(valid_extensions):
        hou.ui.displayMessage(
            f"Invalid file type selected.\nPlease select a file with one of the following extensions: {', '.join(valid_extensions)}",
            title="Invalid File Type",
        )
        return

    # Add the valid file path to the node or return it
    rops.set_parameter_value(node, "usd_filepath", file_path)
    print("Selected USD file: ", file_path)

    return file_path



def prepare_usd_submission(node):
    try:
        node_type = rops.get_node_type(node)
        node_list = rops.get_node_list("task_template_source")

        if node_type in node_list:
            if node_type in ["husk"]:
                render_rop_path = node.parm("driver_path").eval()
                if render_rop_path:
                    husk_command = create_usd_file(node, render_rop_path)
            elif node_type in ["generator"]:
                render_rop_list = node.parm("render_rop_list").eval()
                if render_rop_list:
                    for render_rop_path in render_rop_list:
                        husk_command = create_usd_file(node, render_rop_path)
    except Exception as e:
        print(f"Error preparing USD submissions: {e}")


def create_usd_file(node, render_rop_path, save_usd=False):
    """
    Export the USD from the Houdini node. Then the shot will be ready
    to render with Husk.
    """
    usd_export_filepath = None
    try:
        render_rop_hnode = hou.node(render_rop_path)
        target_type = hou.nodeType(hou.lopNodeTypeCategory(), "usdrender_rop")
        if render_rop_hnode.type() != target_type:
            print(f"{render_rop_path} is not a USD Render ROP.")
            return

        # We need a USD ROP node that is equivalent to the USD Render ROP node that
        # was provided. Create it as another output from the node that connects to
        # the render ROP (normally this will be a RenderSettings node).
        inputs = render_rop_hnode.inputs()

        if len(inputs) != 1:
            print("Expected USD Render ROP to have only 1 input")
            return
        usd_rop_hnode = inputs[0].createOutputNode("usd_rop")

        # setup the USD rop ...
        usd_render_rop_name = extract_name(render_rop_path)
        usd_export_filepath = usd_rop_setup(node, usd_rop_hnode, usd_render_rop_name)

        # Export the USD file...
        if save_usd:
            print(f"Now exporting USD for ROP {usd_render_rop_name} to {usd_export_filepath}")
            usd_rop_hnode.parm('execute').pressButton()

        # Delete the USD ROP node
        # print(f"Deleting USD ROP node {usd_rop_hnode}")
        # usd_rop_hnode.destroy()

        husk_command = create_husk_command(node, render_rop_path, usd_export_filepath)

    except Exception as e:
        print(f"Error creating USD file: {e}")

    return husk_command


def usd_rop_setup(node, usd_rop_hnode, usd_render_rop_name):
    """ Set up the USD rop """

    usd_export_filepath = None
    try:
        usd_export_filepath = set_usd_rop_filepath(node, usd_rop_hnode, usd_render_rop_name)
        set_usd_rop_parameters(usd_rop_hnode)
        set_usd_rop_frame_range(node, usd_rop_hnode)
    except Exception as e:
        print(f"Error setting up USD ROP: {e}")

    return usd_export_filepath


def set_usd_rop_filepath(node, usd_rop_hnode, usd_render_rop_name):
    """ Set up the USD rop filepath"""
    usd_export_filepath = None

    try:
        # Set the 'lopoutput' parameter of the USD ROP
        output_folder = node.parm("output_folder").eval()
        if not output_folder:
            # Set the output folder to the hip folder
            output_folder = os.path.dirname(hou.hipFile.path())
        # set the usd_export_filepath in a "geo" folder in the output folder
        usd_export_name = f"{usd_render_rop_name}_export.usda"
        usd_export_filepath = os.path.join(output_folder, "geo", usd_export_name)
        usd_export_filepath = usd_export_filepath.replace("\\", "/")
        usd_rop_hnode.parm('lopoutput').set(usd_export_filepath)
        create_folder(usd_export_filepath)
    except Exception as e:
        print(f"Error setting USD ROP filepath: {e}")

    return usd_export_filepath


def set_usd_rop_parameters(usd_rop_hnode):
    """ Set up the USD rop filepath"""

    # Set the 'savestyle' parameter of the USD ROP
    usd_rop_hnode.parm('savestyle').set('separate')

    # Set up outputprocessors, which is necessary for the USD files referenced
    # by the stage to end up in the right place relative to usd_export_filepath.
    output_processor_values_dict = {
        'matchoutputextension': {
            'enable': 1,
        },
        'savepathsrelativetooutput': {
            'enable': 0,
            'rootdir': '',
        },
        'simplerelativepaths': {
            'enable': 0,
        },
        'usesearchpaths': {
            'enable': 0,
            'searchpath': '',
        },
    }

    # Set the 'errorsavingimplicitpaths' parameter of the USD ROP
    set_usd_rop_output_processors(usd_rop_hnode, output_processor_values_dict)

    # This next parm suppresses errors from Houdini like:
    #     Error:       Layer saved to a location generated from a node path: ...
    #
    # ...which is good, because the implicit paths are correct in our case. As a
    # side effect, this also suppresses potential warnings coming from the
    # resolver related to referencing files outside of the root path. This is
    # also harmless, but a bit unexpected.
    usd_rop_hnode.parm('errorsavingimplicitpaths').set(0)


def set_usd_rop_frame_range(node, usd_rop_hnode):
    """ Set up the USD rop frame range"""

    # Set "Valid Frame Range" (trange) to index 1 (which is for "Render Specific Frame Range")
    usd_rop_hnode.parm('trange').set(1)

    frame_range = node.parm("frame_range").eval()
    (start_frame, end_frame) = parse_range(frame_range)

    # When creating a USD Rop as an output to the selected Render Rop's input, there are animation keys
    # set on the USD Rop's "f1" and "f2" params (which are start frame and end frame) ... these need
    # to be deleted before we can set those param values
    #
    usd_rop_hnode.parm('f1').deleteAllKeyframes()
    usd_rop_hnode.parm('f2').deleteAllKeyframes()
    usd_rop_hnode.parm('f3').deleteAllKeyframes()

    # Now set the USD Rop's export frame range to what the render job submission specified
    usd_rop_hnode.parm('f1').set(start_frame)
    usd_rop_hnode.parm('f2').set(end_frame)
    usd_rop_hnode.parm('f3').set(1)  # step frame


def create_folder(filepath):
    """ Create the folder for the filepath """
    folder = os.path.dirname(filepath)
    if not os.path.exists(folder):
        os.makedirs(folder)
def extract_name(render_rop_path):
    """ Extract the name of the render rop from the path """
    return render_rop_path.split("/")[-1]

def parse_range( range_str ):
    """
    Given a range as a string like "1001-1100", return the values the range
    represents as a tuple of ints ( start, end ).
    """
    start = end = 0
    if '-' in range_str:
        (start, end) = (int(f) for f in range_str.split( "-" ))
    else:
        start = end = int(range_str)

    return (start, end)

def set_usd_rop_output_processors( usd_rop_hnode, output_processor_values_dict ):
    """
    Set the output processors for the USD ROP
    """
    try:
        import loputils
        output_processor_name_list = sorted(output_processor_values_dict.keys())
        spare_p_list = [str(sp).split()[1] for sp in usd_rop_hnode.spareParms()]
        for output_processor_name in output_processor_name_list:
            enable_p_name \
                = 'enableoutputprocessor_{}'.format( output_processor_name )
            if enable_p_name not in spare_p_list:
                # if not found as a spare parm then we need to add it
                loputils.handleOutputProcessorAdd( {
                    'node': usd_rop_hnode,
                    'parm': usd_rop_hnode.parm('outputprocessors'),
                    'script_value': output_processor_name
                } )
            # end-if
            values_d = output_processor_values_dict[output_processor_name]
            for key in values_d.keys():
                if key == 'enable':
                    usd_rop_hnode.parm( enable_p_name ).set( values_d['enable'] )
                else:
                    p_name = '{0}_{1}'.format( output_processor_name, key )
                    usd_rop_hnode.parm( p_name ).set( values_d[key] )
    except Exception as e:
        print("Unable to set USD rop output processors")


def create_husk_command(node, render_rop_path, usd_export_filepath):
    """
    Create a husk command to submit to the render farm
    """
    try:
        rop_name = extract_name(render_rop_path)
        output = node.parm("output_folder").eval()
        override_image_output = node.parm("override_image_output").evalAsString()

        houdini_render_args = [
            "--renderer", "Redshift",
            "--frame", "1",
            "--frame-count", "1",
            "--output", output
        ]
        cmd = f"husk -o {override_image_output} usd_export_filepath"


    except Exception as e:
        print(f"Error creating husk command: {e}")

