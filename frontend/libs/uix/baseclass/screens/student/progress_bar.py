from kivy.clock import Clock
from kivymd.uix.button import MDIconButton
from kivymd.uix.screen import MDScreen


class Progress(MDScreen):
    PROGRESS_INDICATOR_SIZE = ("120dp", "120dp")
    BUTTON_RADIUS = 42  # Half of the button's width/height
    BUTTON_COLOR = "green"
    ICON_COLOR = "white"
    ICON_SIZE = "28sp"
    PROGRESS_DURATION = 10  # Duration of the progress in seconds

    def on_enter(self):
        self.ids.progress.start()
        # Schedule the progress completion and transition
        Clock.schedule_once(self.complete_progress, self.PROGRESS_DURATION)

    def complete_progress(self, dt):
        # Hide or remove the progress indicator
        self.ids.progress.value = 100
        self.ids.progress.opacity = 0  # Hides the progress indicator

        # Add the check icon and update the label
        self.show_check_icon()

        # Schedule the transition to the next screen
        Clock.schedule_once(self.switch_to_next_screen, 2)  # Adjust delay if needed

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

        # Update the existing label to display "Approved"
        self.ids.label.text = "[b][color=#008000]Approved.[/color][/b]"

        # Set flags in the StudentDashboardScreen
        student_dashboard = self.manager.get_screen("student_dashboard")
        student_dashboard.enable_studentid = True
        student_dashboard.enable_newsletter = True
        student_dashboard.enable_profilepicture = True

    def switch_to_next_screen(self, dt=None):
        self.manager.current = "student_dashboard"

    def on_leave(self):
        self.ids.progress.stop()
