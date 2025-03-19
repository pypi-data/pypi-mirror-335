import os
import sys
from ciocore.validator import Validator
import hou
import logging
import ciocore.loggeria
from ciohoudini import rops

logger = ciocore.loggeria.get_conductor_logger()


class ValidateDriverPath(Validator):
    def run(self, _):
        """
        Validate that the "driver_path" parameter is set for nodes of type "solaris" or "rop".
        """
        node = self._submitter
        node_type = rops.get_node_type(node)  # Determine node type

        if node_type in ["solaris", "rop"]:
            driver_path_param = node.parm("driver_path")

            if not driver_path_param or not driver_path_param.eval().strip():
                msg = (
                    "The 'driver_path' parameter is not set. "
                    "Please select a valid driver before submission."
                )
                self.add_error(msg)


class ValidateImageOutputPath(Validator):
    def run(self, _):
        """
        Validate the "override_image_output" parameter of the node.

        - Evaluate the parameter to get the file path.
        - Check if the folder of the file path exists.
        - If it doesn't exist:
          - Attempt to create the folder.
          - Add appropriate error or warning messages based on the result.
        """
        node = self._submitter

        image_output_param = node.parm("override_image_output")

        if not image_output_param:
            return  # If the parameter doesn't exist, skip validation.

        image_output_path = image_output_param.eval().strip()

        if not image_output_path:
            node_type = rops.get_node_type(node)
            if node_type in ["solaris"]:
                msg = (
                    "No output path detected in any RenderProducts or in a USD Render ROP."
                    " Please set before submitting."
                )
            else:
                msg = (
                    "The 'override_image_output' parameter is not set. "
                    "Please specify a valid file path for image output before submission."
                )
            self.add_error(msg)
            return

        # Resolve Houdini variables (e.g., $HIP) in the path
        try:
            resolved_path = hou.expandString(image_output_path)
        except Exception as e:
            resolved_path = image_output_path  # Fallback if expansion fails
            logger.debug(f"Failed to resolve path: {e}")

        # Get the folder of the file path
        folder_path = os.path.dirname(resolved_path)

        # If the folder path is not empty, check if it exists
        if folder_path:
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                    msg = (
                        f"The folder '{folder_path}' did not exist and was created successfully."
                    )
                    self.add_warning(msg)  # Adding as a warning since it was corrected automatically
                except Exception as e:
                    msg = (
                        f"The folder '{folder_path}' did not exist and could not be created. "
                        f"Error: {e}"
                    )
                    self.add_error(msg)  # Adding as an error since the issue could not be resolved
        else:
            # If the folder path is empty, it means the file path is relative to the current working directory
            # In this case, we don't need to create the folder since it will be created automatically by Houdini
            pass



class ValidateUSDFilePath(Validator):
    def run(self, _):
        """
        Validate the "usd_filepath" parameter of the node.

        - If "usd_filepath" is not set, prompt the user to set it.
        - If "usd_filepath" is set but the file does not exist on disk, warn the user to correct it.
        """
        node = self._submitter
        usd_filepath_param = node.parm("usd_filepath")

        if not usd_filepath_param:
            return  # If the parameter doesn't exist, skip validation.

        usd_filepath = usd_filepath_param.eval().strip()

        if not usd_filepath:
            msg = (
                "The 'usd_filepath' parameter is not set. "
                "Please specify a valid USD file path before submission."
            )
            self.add_error(msg)
            return

        # Resolve Houdini variables (e.g., $HIP) in the path
        try:
            resolved_filepath = hou.expandString(usd_filepath)
        except Exception as e:
            resolved_filepath = usd_filepath  # Fallback if expansion fails
            logger.debug(f"Failed to resolve path: {e}")

        # Check if the resolved path exists on disk
        if not os.path.exists(resolved_filepath):
            msg = (
                f"The specified USD file path '{usd_filepath}' resolves to '{resolved_filepath}', "
                "but it does not exist on disk. Please verify the path and ensure the file is accessible "
                "before submission."
            )
            self.add_error(msg)


class ValidateUploadDaemon(Validator):
    def run(self, _):
        node = self._submitter
        use_daemon = node.parm("use_daemon").eval()
        if not use_daemon:
            return
        location = node.parm("location_tag").eval().strip()
        if location:
            msg = "This submission expects an uploader daemon to be running and set to a specific location tag. "
            msg += "Please make sure that you have installed ciocore from the Conductor Companion app "
            msg += "and that you have started the daemon with the --location flag set to the same location tag."
            msg += 'After you press submit you can open a shell and type: conductor uploader --location "{}"\n'.format(
                location

            )
        else:
            msg = "This submission expects an uploader daemon to be running.\n"
            msg += "Please make sure that you have installed ciocore from the Conductor Companion app "
            msg += 'After you press submit you can open a shell and type: "conductor uploader"'


        self.add_notice(msg)

        self.add_warning(
            "Since you are using an uploader daemon, you'll want to make sure that all your assets are "+
            "accessible by the machine on which the daemon is running.\n You can check the list of upload assets in the Preview tab.\n"+
            "Just hit the Do Asset Scan button and scroll down to the bottom."
            )


"""
class ValidateTaskCount(Validator):
    def run(self, _):
        pass
        #Todo: do we need this?
        
        node = self._submitter
        tasks = node.parm("frame_task_county").eval()
        if tasks > 2000:
            self.add_error(
                "This submission contains over 1000 tasks ({}). You'll need to either increase chunk_size or send several job?".format(
                    tasks
                )
            )
 """

 
class ValidateScoutFrames(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        node = self._submitter
        use_scout_frames = node.parm("use_scout_frames").eval()


        scout_count = node.parm("scout_frame_task_countx").eval()
        frame_count = node.parm("frame_task_countx").eval()
        chunk_size = node.parm("chunk_size").eval()
        instance_type_name = node.parm("instance_type").eval()

        if scout_count == 0 and instance_type_name in ["best-fit-cpu", "best-fit-gpu"]:
            msg = (
            "We strongly recommend using Scout Frames with best fit instance types," +
            " as Conductor is not responsible for insufficient render nodes when using Best" +
            " Fit instance types."
            )
            self.add_warning(msg)
            
        """
        if frame_count < 5:
            return

        if scout_count < 5 and scout_count > 0:
            return

        if scout_count == 0 or scout_count == frame_count:
            msg = "All tasks will start rendering."
            msg += " To avoid unexpected costs, we strongly advise you to configure scout frames so that most tasks are initially put on hold. This allows you to check a subset of frames and estimate costs before you commit a whole sequence."
            self.add_warning(msg)
        """

        if chunk_size > 1 and use_scout_frames:
            msg = "You have chunking set higher than 1."
            msg += " This can cause more scout frames to be rendered than you might expect."
            self.add_warning(msg)

class ValidateResolvedChunkSize(Validator):
    def run(self, _):
        """
        Add a validation warning for a large number of tasks.
        """
        try:
            node = self._submitter
            chunk_size = node.parm("chunk_size").eval()
            resolved_chunk_size = node.parm("resolved_chunk_size").eval()

            if chunk_size and resolved_chunk_size:
                chunk_size = int(chunk_size)
                resolved_chunk_size = int(resolved_chunk_size)

                if resolved_chunk_size > chunk_size:
                    msg = "In one or more render rops, the number of frames per task has been automatically increased to maintain " \
                          "a total task count below 800. If you have a time-sensitive deadline and require each frame to be " \
                          "processed on a dedicated instance, you might want to consider dividing the frame range into smaller " \
                          "portions. " \
                          "Alternatively, feel free to reach out to Conductor Customer Support for assistance."
                    self.add_warning(msg)

        except Exception as e:
            logger.debug("ValidateResolvedChunkSize: {}".format(e))


class ValidateGPURendering(Validator):
    def run(self, _):
        """
        Add a validation warning for CPU rendering when using the Redshift plugin.
        """
        node = self._submitter
        instance_type_family = node.parm("instance_type_family").eval().lower()
        driver_software = node.parm("driver_version").eval().lower()

        if "redshift" in driver_software and instance_type_family == "cpu":
            msg = "CPU rendering is selected."
            msg += " We strongly recommend selecting GPU rendering when using the Redshift plugin for Houdini.."
            self.add_warning(msg)

class ValidateUploadedFilesWithinOutputFolder(Validator):
    def run(self, _):
        """
        Add a validation warning for Uploaded Files Within Output Folder.
        """
        node = self._submitter
        output_excludes = node.parm("output_excludes").eval()
        print("output_excludes: {}".format(output_excludes))
        output_folder = node.parm("output_folder").eval()
        if output_excludes and output_excludes == 1:
            msg = "One or more assets in the output folder: {} ".format(output_folder)
            msg += "have been identified as already uploaded. "
            msg += "To ensure smooth processing on the render farm and avoid potential conflicts, "
            msg += "these files have been excluded from the list of assets to be uploaded."
            msg += "For successful job submission, please relocate these files to "
            msg += "a different folder and then resubmit your job."

            self.add_warning(msg)
        node.parm("output_excludes").set(0)

class ValidatePaths(Validator):
    def run(self, _):
        """
        Add a validation warning for using the $HOME path in "loadlayer" USD node.
        """
        stage_node_list = hou.node('/stage').allSubChildren()
        disallowed_list = ["$HOME"]
        for stage_node in stage_node_list:
            if stage_node:
                if stage_node.type().name() == 'loadlayer':
                    filepath_param = stage_node.parm("filepath")
                    if filepath_param:
                        filepath_value = filepath_param.rawValue()
                        for item_sr in disallowed_list:
                            if item_sr in filepath_value:
                                msg = (
                                    "We strongly recommend using an explicit path over using '$HOME' in the filepath of any loadlayer node within the stage as '$HOME' might not be correctly evaluated on the renderfarm."
                                )
                                self.add_warning(msg)

# Implement more validators here
####################################
####################################


def run(*nodes):
    errors, warnings, notices = [], [], []
    for node  in nodes:
        er, wn, nt = _run_validators(node)
        
        errors.extend(er)
        warnings.extend(wn)
        notices.extend(nt)

    return errors, warnings, notices

def _run_validators(node):

    takename =  node.name()
    validators = [plugin(node) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run(takename)

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices


