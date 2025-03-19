from PySide2 import QtWidgets, QtCore
from ciohoudini.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini import rops, validation, payload
import json


import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()
class SelectionTab(ButtonedScrollPanel):
    def __init__(self, dialog):
        super(SelectionTab, self).__init__(
            dialog,
            buttons=[("close", "Close"), ("continue", "Continue Submission")]
        )
        self.dialog = dialog
        self.node = self.dialog.node
        self.all_checkboxes = []  # Keep track of all node checkboxes
        self.node_map = {}  # Map checkboxes to their corresponding nodes
        self.subnet_checkboxes = []  # Keep track of all subnet checkboxes
        self.configure_signals()

        # Add "Select all nodes" and "Deselect all nodes" buttons at the top
        self.add_global_buttons()

    def configure_signals(self):
        """Connect button signals to their respective handlers."""
        self.buttons["close"].clicked.connect(self.dialog.on_close)
        self.buttons["continue"].clicked.connect(self.on_continue)

    def add_global_buttons(self):
        """Add global buttons for selecting and deselecting all nodes."""
        button_layout = QtWidgets.QHBoxLayout()
        select_all_button = QtWidgets.QPushButton("Select all nodes")
        deselect_all_button = QtWidgets.QPushButton("Deselect all nodes")

        # Connect the buttons to their respective slots
        select_all_button.clicked.connect(self.select_all_nodes)
        deselect_all_button.clicked.connect(self.deselect_all_nodes)

        # Add buttons to the layout
        button_layout.addWidget(select_all_button)
        button_layout.addWidget(deselect_all_button)
        self.layout.addLayout(button_layout)

    def list_subnet_nodes(self, node):
        """
        Lists the name of each subnet connected to the generator node and adds checkboxes for nodes in the subnets.
        """
        logger.debug("Selection tab: Listing subnet nodes...")

        if not node:
            logger.debug("Selection tab: No node provided.")
            return

        # Clear existing content in the layout to prepare for new content
        self.clear()
        self.all_checkboxes = []  # Reset the list of all node checkboxes
        self.node_map = {}  # Reset the node map
        self.subnet_checkboxes = []  # Reset the list of subnet checkboxes

        # Add the global buttons again at the top
        self.add_global_buttons()

        # Iterate over connected output nodes to find subnets
        for output_node in node.outputs():
            if output_node and output_node.type().name() == "subnet":
                logger.debug(f"Found subnet: {output_node.name()}")

                # Create a horizontal layout for the subnet title and checkbox
                subnet_row_layout = QtWidgets.QHBoxLayout()

                # Create a checkbox for the subnet
                subnet_checkbox = QtWidgets.QCheckBox()
                subnet_checkbox.setToolTip(f"Toggle all nodes in subnet: {output_node.name()}")
                subnet_row_layout.addWidget(subnet_checkbox)
                self.subnet_checkboxes.append(subnet_checkbox)  # Track subnet checkbox globally

                # Create a label for the subnet name and style it
                subnet_name_label = QtWidgets.QLabel(f"Subnet: {output_node.name()}")
                subnet_name_label.setStyleSheet("font-weight: bold;")  # Make the text bold
                subnet_row_layout.addWidget(subnet_name_label)

                # Align subnet name to the left
                subnet_row_layout.setAlignment(QtCore.Qt.AlignLeft)

                # Add the subnet row layout to the main layout
                self.layout.addLayout(subnet_row_layout)

                # Create a vertical layout to group checkboxes for nodes within the subnet
                node_container_layout = QtWidgets.QVBoxLayout()
                node_container_layout.setContentsMargins(40, 0, 0, 0)  # Indent for better grouping
                self.layout.addLayout(node_container_layout)

                # Add checkboxes for each node in the subnet
                node_checkboxes = []
                for child_node in output_node.children():
                    # logger.debug(f"Adding checkbox for node: {child_node.name()}")
                    checkbox = QtWidgets.QCheckBox(child_node.name())
                    node_payload = self.generate_payload(child_node)
                    tooltip_text = json.dumps(node_payload, indent=2) if node_payload else "No payload available"
                    checkbox.setToolTip(tooltip_text)  # Set tooltip with payload
                    node_container_layout.addWidget(checkbox)
                    node_checkboxes.append(checkbox)
                    self.all_checkboxes.append(checkbox)  # Track globally
                    self.node_map[checkbox] = child_node  # Map checkbox to its node

                # Connect the subnet checkbox to toggle all child node checkboxes
                subnet_checkbox.stateChanged.connect(
                    lambda state, checkboxes=node_checkboxes: self.toggle_subnet_nodes(state, checkboxes)
                )

        # Add a stretch to align content to the top
        self.layout.addStretch()

    def toggle_subnet_nodes(self, state, checkboxes):
        """
        Toggles the state of all node checkboxes under a subnet.

        Args:
            state (int): The state of the subnet checkbox (0: unchecked, 2: checked).
            checkboxes (list): List of node checkboxes under the subnet.
        """
        is_checked = state == QtCore.Qt.Checked
        for checkbox in checkboxes:
            checkbox.setChecked(is_checked)

    def generate_payload(self, node):
        """
        Generates a payload for a single node.

        Args:
            node: The Houdini node for which to generate the payload.

        Returns:
            dict: The generated payload or None if there was an error.
        """
        kwargs = {
            "frame_range": rops.get_parameter_value(node, "frame_range"),
            "task_limit": 1,
            "do_asset_scan": True,
        }
        rop_path = rops.get_parameter_value(node, "driver_path")

        try:
            node_payload = payload.get_payload(node, rop_path, **kwargs)
            return node_payload
        except Exception as e:
            logger.error(f"Error generating payload for node {node.name()}: {e}")
            return None

    def select_all_nodes(self):
        """Sets all node and subnet checkboxes to checked."""
        logger.debug("Selecting all nodes...")
        for checkbox in self.all_checkboxes:
            checkbox.setChecked(True)
        for subnet_checkbox in self.subnet_checkboxes:
            subnet_checkbox.setChecked(True)

    def deselect_all_nodes(self):
        """Sets all node and subnet checkboxes to unchecked."""
        logger.debug("Deselecting all nodes...")
        for checkbox in self.all_checkboxes:
            checkbox.setChecked(False)
        for subnet_checkbox in self.subnet_checkboxes:
            subnet_checkbox.setChecked(False)

    def on_continue(self):
        """Handles the 'Continue Submission' button click."""
        logger.debug("Validation tab: Continue Submission...")

        # Generate payloads for all checked nodes
        payloads = self.get_payloads()
        logger.debug(f"Generated {len(payloads)} payloads.")

        if self.node:
            # Show the validation tab in the dialog
            self.dialog.show_validation_tab()
            logger.debug("Validation tab: Running validation...")

            # Run validation and populate the validation tab with results
            errors, warnings, notices = validation.run(self.node)
            logger.debug("Validation tab: Populating validation results...")
            self.dialog.validation_tab.populate(errors, warnings, notices)
