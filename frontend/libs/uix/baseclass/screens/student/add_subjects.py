from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (  # noqa: F401
    StudentsubjectsRoutes,
    SubjectsRoutes,
)
from libs.uix.baseclass.components.subject_create_list_item import SubjectCreateListItem


class AddSubjectsScreen(MDScreen):
    def on_pre_enter(self):
        # Fetch and populate subjects when the screen is about to be entered
        self.get_all_subjects()

    def get_all_subjects(self):
        try:
            response = SubjectsRoutes(
                client=self.manager.connection_client
            ).get_subjects()

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
                SubjectCreateListItem(
                    subject_name=subject.get(
                        "name", "N/A"
                    ),  # Assuming 'name' is a key in the response
                    subject_grade=subject.get(
                        "grade", "N/A"
                    ),  # Assuming 'grade' is the symbol for the subject
                )
            )

    def get_subjects_with_symbols(self):
        # Get all the children (widgets) in the subjects container
        all_subjects = self.ids.subjects.children
        valid_subjects = []

        # Iterate over the subjects and print their names
        for subject_widget in all_subjects:
            # Assuming SubjectCreateListItem has properties subject_name and subject_grade
            subject_name = subject_widget.subject_name
            subject_grade = subject_widget.ids.grade_text_field.text.upper()

            # If subject_grade is default X or is empty or len>1 (Skip that value is invalid, else create a list of student_subjects)
            if subject_grade == "X" or len(subject_grade) > 1:
                print("Error Value")
            else:
                user_subject = {"name": subject_name, "grade": subject_grade}
                valid_subjects.append(user_subject)

        # Send all the valid subjects to the backend and create new user subjects
        response = StudentsubjectsRoutes(
            client=self.manager.connection_client
        ).post_bulk_add_student_subject(
            json=valid_subjects
        )  # With a list of student subjects to add

        if response.status_code == 200:
            self.manager.push("my_subjects")
            # change to the
