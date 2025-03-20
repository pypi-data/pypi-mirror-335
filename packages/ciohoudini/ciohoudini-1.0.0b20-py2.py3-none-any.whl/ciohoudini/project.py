"""Manage project menu selection."""


from ciocore import data as coredata



def populate_menu(node):
    """Populate project menu.

    Get list of items from the shared data_block where they
    have been cached. The menu needs a flat array: [k, v, k,
    v ....]

    Since projects are simply a list of names, the k and v can be the same.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not Connected --"]
    ensure_valid_selection(node)
    return [el for p in coredata.data()["projects"] for el in [p, p]]


# def on_project_changed(node, **kwargs):
#     """When user chooses a new project, update button states."""
#     pass


def ensure_valid_selection(node):
    """
    If connected, ensure the value of this parm is valid.
    """

    if not coredata.valid():
        return

    selected = node.parm("project").eval()


    projects = coredata.data()["projects"]
    if not projects:
        node.parm("project").set("no_projects")
        return
    if selected in projects:
        node.parm("project").set(selected)
    else:
        # This can happen if the user has deleted a project.
        node.parm("project").set(coredata.data()["projects"][0])

def resolve_payload(node):
    return {"project": node.parm('project').eval()}
 