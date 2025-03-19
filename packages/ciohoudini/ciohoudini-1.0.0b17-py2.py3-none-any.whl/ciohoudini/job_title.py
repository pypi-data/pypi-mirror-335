"""frame range section in the UI."""

import hou

def resolve_payload(node, rop_path=None):
    title = node.parm("title").eval().strip()
    if rop_path:
        title = "{}  {}".format(title, rop_path)
    return {"job_title": title}

