import os
import re
import shutil

import hou

import ciocore.loggeria

# Simple loose email regex, matches 1 email address.
SIMPLE_EMAIL_RE = re.compile(r"^\S+@\S+$")

def resolve_payload(node, **kwargs):
    """
    Resolve the notifications field for the payload.
    """
    result = {}
    addresses = resolve_email_addresses(node)
    if addresses:
        result["notify"] = addresses
    location = resolve_location(node)
    if location:
        result["location"] = location

    result["local_upload"] = not node.parm("use_daemon").eval()
    return result
 

def resolve_email_addresses(node):
    """
    Resolve the notifications field for the payload.
    """
    if not node.parm("do_email").eval():
        return []

    addresses = node.parm("email_addresses").eval() or ""
    addresses = [a.strip() for a in re.split(', ', addresses) if a and SIMPLE_EMAIL_RE.match(a)]
    return addresses

def resolve_location(node):
    """
    Resolve the location field for the payload.
    """
    location = node.parm("location_tag").eval()

    return location

def copy_render_script(node, **kwargs):
    """
    Copy the render script to somewhere else.
    """
    script = node.parm("render_script").eval()
    if not script:
        print("Couldn't copy script. No script specified.")
        return


    destination = hou.ui.selectFile(
        title="Destination file",
        start_directory = os.path.join(hou.getenv("HIP"), "scripts"),
        file_type=hou.fileType.Any,
        multiple_select=False,
        default_value=os.path.basename(script),
        chooser_mode=hou.fileChooserMode.Write,
    )

    if not destination:
        print("Couldn't copy script. No destination specified.")
        return

    shutil.copyfile(script, destination)

    lockstate = node.parm("render_script").isLocked()
    node.parm("render_script").lock(False)
    node.parm("render_script").set(destination)
    node.parm("render_script").lock(lockstate)

def change_log_level(node, **kwargs):
    ciocore.loggeria.set_conductor_log_level(kwargs['script_value'])
