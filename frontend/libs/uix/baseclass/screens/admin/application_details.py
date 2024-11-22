from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (
    ApplicationsRoutes,
    StudentsubjectsRoutes,
)
from libs.uix.baseclass.components.subject_view_list import SubjectListItem


class ApplicationDetailsScreen(MDScreen):
    subjects = []

    def on_pre_enter(self):
        self.current_application = self.manager.get_shared_data("current_application")
        self.get_all_my_subjects()

    def on_enter(self):
        self.set_application_pending()

    def approve_application(self):
        if self.current_application.get("status") != "APPROVED":
            application_id = self.current_application.get("id")
            response = self._update_application_status(application_id, "approve")

            if response.status_code == 200:
                self.manager.push_replacement("applications")
            else:
                self._show_error_dialog("Failed to Approve Application", response)

    def reject_application(self):
        if self.current_application.get("status") != "REJECTED":
            application_id = self.current_application.get("id")
            response = self._update_application_status(application_id, "reject")

            if response.status_code == 200:
                self.manager.push_replacement("applications")
            else:
                self._show_error_dialog("Failed to Reject Application", response)

    def set_application_pending(self):
        if self.current_application.get("status") == "SENT":
            application_id = self.current_application.get("id")
            response = self._update_application_status(application_id, "pending")

            if response.status_code == 200:
                print(f"Application: {application_id} is now pending")
            else:
                self._show_error_dialog("Failed to Update Application Status", response)

    def _update_application_status(self, application_id, action):
        # Centralized function to update application status
        route = ApplicationsRoutes(client=self.manager.connection_client)
        if action == "approve":
            return route.patch_approve_application(application_id=application_id)
        elif action == "reject":
            return route.patch_reject_application(application_id=application_id)
        elif action == "pending":
            return route.patch_pending_application(application_id=application_id)

    def _show_error_dialog(self, title, response):
        """Show an error dialog with the response details."""
        MDDialog(
            title=title,
            text=f"Error: {response.status_code} - {response.content.decode()}",
            size_hint=(0.8, 1),
            buttons=[
                MDButton(
                    MDButtonText(text="Close"),
                    on_release=lambda x: self.dismiss_dialog(),
                )
            ],
        ).open()

    def dismiss_dialog(self):
        """Dismiss the error dialog."""
        self.dialog.dismiss()

    def get_all_my_subjects(self):
        try:
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).get_student_subjects()

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()
                # print(student_subjects)
                self.subjects = student_subjects  # Update the subjects list

                # Set the subjects to the shared data (optional)
                self.manager.set_shared_data("student_subjects", student_subjects)

                # Populate the UI after receiving subjects
                self.populate_subjects_ui()
            else:
                print(f"Error fetching subjects: {response.status_code}")

        except Exception as e:
            print(f"Error fetching subjects: {e}")

    def populate_subjects_ui(self):
        # Clear any existing subjects
        self.ids.subjects.clear_widgets()

        # Iterate through all subjects and display them in the UI
        for subject in self.subjects:
            self.ids.subjects.add_widget(
                SubjectListItem(
                    subject_name=subject.get(
                        "name", "N/A"
                    ),  # Assuming 'name' is a key in the response
                    grade=subject.get(
                        "grade", "N/A"
                    ),  # Assuming 'grade' is the symbol for the subject
                )
            )
