
#from ciohoudini.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini.notice_grp import NoticeGrp

from ciohoudini import rops

import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()
class ValidationTab(ButtonedScrollPanel):

    def __init__(self, dialog):
        super(ValidationTab, self).__init__(
            dialog,
            buttons=[("close", "Close"), ("continue", "Continue Submission")])
        self.dialog = dialog
        self.configure_signals()

    def configure_signals(self):
        self.buttons["close"].clicked.connect(self.dialog.on_close)
        self.buttons["continue"].clicked.connect(self.on_continue)

    def populate(self, errors, warnings, infos):
        
        obj = {
            "error": errors,
            "warning": warnings,
            "info": infos
        }
        has_issues = False
        for severity in ["error", "warning", "info"]:
            for entry in obj[severity]:
                has_issues = True
                widget = NoticeGrp(entry, severity)
                self.layout.addWidget(widget)

        if not has_issues:
            widget = NoticeGrp("No issues found", "success")
            self.layout.addWidget(widget)

        self.layout.addStretch()

        if errors:
            self.buttons["continue"].setEnabled(False)
        else:
            self.buttons["continue"].setEnabled(True)


    def on_continue(self):
        """ When someone clicks on Continue Submission """
        logger.debug("Continue Submission...")
        node = self.dialog.node

        use_daemon = node.parm("use_daemon").eval()

        # rops.prepare_usd_submissions(node)

        if node:
            # Show the progress tab
            self.dialog.show_progress_tab()

            logger.debug("Submitting jobs...")
            self.dialog.progress_tab.submit(node)
        """
        if node:
            if not use_daemon:
                # Show the progress tab
                self.dialog.show_progress_tab()

                logger.debug("Submitting jobs...")
                self.dialog.progress_tab.submit(node)

            else:
                results = submit.run(node)
                self.dialog.response_tab.hydrate(results)
                self.dialog.tab_widget.setCurrentWidget(self.dialog.response_tab)

                # Enable responses and disable validation, and progress
                self.dialog.tab_widget.setTabEnabled(2, True)
                self.dialog.tab_widget.setTabEnabled(1, False)
                self.dialog.tab_widget.setTabEnabled(0, False)
        """

        
 