from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import StudentsRoutes


class StudentId(MDScreen):
    first_name = ObjectProperty()
    last_name = ObjectProperty()
    gender = ObjectProperty()
    date_of_birth = ObjectProperty()

    def get_student_details_by_id(self, *agrs, **kwargs):
        response = StudentsRoutes(
            client=self.manager.connection_client
        ).get_student_by_id(
            student_id=self.manager.current_student_id,
        )
        self.first_name = self.manager.get_shared_data("user").get("first_name")
        self.last_name = self.manager.get_shared_data("user").get("last_name")
        self.gender = self.manager.get_shared_data("user").get("gender")
        self.date_of_birth = self.manager.get_shared_data("user").get("date_of_birth")

    def on_pre_enter(self):
        self.get_students_event = self.get_student_details_by_id()

    def on_enter(self):
        self.animate_offline()

    def on_leave(self):
        if self.get_students_event:
            self.get_students_event.cancel()

    def animate_offline(self, *args, **kwargs):
        # self.animation.stop(self.ids.status_label)  # Stop any existing animation

        self.animation = (
            Animation(font_size=20, duration=0.2)
            + Animation(font_size=24, duration=0.2)
            + Animation(font_size=20, duration=0.2)
        )
        self.animation.repeat = True  # Make the animation loop indefinitely

        self.animation.start(self.ids.status_label)
        self.ids.status_label.text_color = "#FF0000"
        self.ids.status_label.text = "Print out your student_id"
