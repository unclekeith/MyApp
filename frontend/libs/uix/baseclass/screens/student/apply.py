from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import (
    ApplicationsRoutes,
    StudentsubjectsRoutes,
)
from libs.uix.baseclass.components.subject_apply_list import SubjectApplyListItem


class ApplyScreen(MDScreen):
    subjects = []
    PROGRESS_INDICATOR_SIZE = ("120dp", "120dp")
    BUTTON_RADIUS = 42  # Half of the button's width/height
    BUTTON_COLOR = "green"
    ICON_COLOR = "white"
    ICON_SIZE = "28sp"
    PROGRESS_DURATION = 10  # Duration of the progress in seconds
    STATUS_CHECK_INTERVAL = 2  # Interval in seconds to check for updates

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application_status_displayed = (
            False  # Track if application status is displayed
        )
        self.application_check_event = (
            None  # Store the scheduled Clock event for checking status
        )

    def on_pre_enter(self):
        # Clear any previously added widgets
        self.ids.check.clear_widgets()
        # Fetch and populate subjects when the screen is about to be entered
        self.get_user_application()

    def on_enter(self):
        # Clear any previously added widgets
        self.ids.check.clear_widgets()

        # Start checking for updates to the application status every 2 seconds
        self.application_check_event = Clock.schedule_interval(
            self.check_for_application_updates, self.STATUS_CHECK_INTERVAL
        )

    def on_leave(self):
        # Unschedule the periodic status check when leaving the screen
        if self.application_check_event:
            Clock.unschedule(self.application_check_event)

    def check_for_application_updates(self, dt):
        # Call the method to get and update user application
        self.get_user_application()

    def get_user_application(self):
        user_application = self.manager.get_shared_data("user").get("application")

        if len(user_application) > 0:
            user_application = user_application[0]
            application_status = user_application.get("status")
            color = ""

            # Clear previous status if already displayed
            if self.application_status_displayed:
                self.ids.check.clear_widgets()
                self.application_status_displayed = False

            # Check and update status based on application status
            if application_status == "SENT":
                color = "orange"
                self.sent()
                self.application_status_displayed = True

            elif application_status == "PENDING":
                color = (0.8, 0.3, 0.8, 5)
                self.pending()
                self.application_status_displayed = True

            elif application_status == "APPROVED":
                color = "green"
                self.show_check_icon()
                self.application_status_displayed = True
                Clock.schedule_once(self.switch_to_next_screen, 5)

            elif application_status == "REJECTED":
                color = "red"
                Clock.schedule_once(self.switch_to_rejected_screen, 10)
                self.application_status_displayed = True

            # Add card to show the current status
            self.add_widget(
                MDCard(
                    MDLabel(text="Application Status"),
                    MDLabel(text=f"{application_status}"),
                    orientation="horizontal",
                    pos_hint={"center_x": 0.5, "center_y": 0.4},
                    size_hint=(None, None),
                    theme_bg_color="Custom",
                    md_bg_color=color,
                    size_hint_x=0.7,
                    size_hint_y=0.08,
                    padding=(dp(20), 0, 0, 0),
                )
            )
        else:
            self.populate_subjects_ui()

    # Other methods remain unchanged (populate_subjects_ui, apply, show_check_icon, etc.)

    def get_user_subjects(self):
        try:
            response = StudentsubjectsRoutes(
                client=self.manager.connection_client
            ).get_student_subjects()

            # Check if the request was successful
            if response.status_code == 200:
                student_subjects = response.json()
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
                SubjectApplyListItem(
                    subject_name=subject.get(
                        "name", "N/A"
                    ),  # Assuming 'name' is a key in the response
                    subject_grade=subject.get(
                        "grade", "N/A"
                    ),  # Assuming 'grade' is the symbol for the subject
                )
            )
        self.add_widget(
            MDButton(
                MDButtonText(text="Apply"),
                MDButtonIcon(icon="check-decagram"),
                on_release=self.apply,
                pos_hint={"center_x": 0.5, "center_y": 0.1},
                radius=dp(0),
            )
        )

    def get_subjects_with_symbols(self):
        # Get all the children (widgets) in the subjects container
        all_subjects = self.ids.subjects.children
        valid_subjects = []

        # Iterate over the subjects and print their names
        for subject_widget in all_subjects:
            subject_name = subject_widget.subject_name
            subject_grade = subject_widget.ids.grade_text_field.text.upper()

            if subject_grade == "X" or len(subject_grade) > 1:
                print("Error Value")
            else:
                user_subject = {"name": subject_name, "grade": subject_grade}
                valid_subjects.append(user_subject)

        # Send all the valid subjects to the backend and create new user subjects
        response = ApplicationsRoutes(client=self.manager.connection_client).post_apply(
            json={"subject_ids": []}
        )

        if response.status_code == 200:
            self.manager.push("my_subjects")

    def apply(self, *rgs, **kwargs):
        self.get_subjects_with_symbols()

    def show_check_icon(self, dt=None):
        # Create and add the check icon
        check_button = MDIconButton(
            icon="check",
            style="tonal",
            theme_font_size="Custom",
            font_size=self.ICON_SIZE,
            radius=[self.BUTTON_RADIUS],
            size_hint=(None, None),
            size=self.PROGRESS_INDICATOR_SIZE,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            theme_bg_color="Custom",
            md_bg_color=self.BUTTON_COLOR,
            theme_icon_color="Custom",
            icon_color=self.ICON_COLOR,
        )
        self.ids.check.add_widget(check_button)

    def pending(self, dt=None):
        # Create and add the check icon
        button = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=(0.8, 0.3, 0.8, 5),
        )
        self.ids.check.add_widget(button)

    def sent(self, dt=None):
        # Create and add the check icon
        sent = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color="orange",
        )
        self.ids.check.add_widget(sent)

    def switch_to_next_screen(self, dt=None):
        self.manager.push_replacement("student_dashboard")

    def switch_to_rejected_screen(self, dt=None):
        self.manager.push_replacement("message")
