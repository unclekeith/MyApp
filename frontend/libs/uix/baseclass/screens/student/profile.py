from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen


class StudentProfileScreen(MDScreen):
    first_name = ObjectProperty()
    last_name = ObjectProperty()
    date_of_birth = ObjectProperty()
    id_number = ObjectProperty()
    number_of_passed_subjects = ObjectProperty()
    gender = ObjectProperty()
    previous_school = ObjectProperty()
    academic_level = ObjectProperty()
    next_of_kin = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_user_data = None  # Store the previous user data
        print("Initializing StudentProfileScreen...")

        # Schedule the update check every 2 seconds
        Clock.schedule_once(self.initial_check, 0)  # Initial check on enter
        Clock.schedule_interval(self.check_for_updates, 2)  # Check every 2 seconds
        
    def on_leave(self):
        """Called when the screen is left. Unschedule the checks."""
        print("Leaving StudentProfileScreen... Stopping data checks.")
        Clock.unschedule(self.initial_check)  # Unschedule the initial check
        Clock.unschedule(self.check_for_updates)  # Unschedule the periodic updates


    def initial_check(self, dt):
        # Force initial update when screen is first shown
        print("Performing initial data load...")
        self.update_user_data()

    def check_for_updates(self, dt):
        """This function is called every 2 seconds to check for user data updates."""
        print("Checking for user data updates...")
        current_user_data = self.manager.get_shared_data("user")
        
        if current_user_data != self.previous_user_data:
            print("User data has changed, updating the profile...")
            self.update_user_data()
            self.previous_user_data = current_user_data  # Update the previous data reference
        else:
            print("No changes detected in user data.")

    def on_enter(self):
        """Called when the screen is entered"""
        self.update_user_data()

    def update_user_data(self):
        """Populate the fields with user data."""
        self.user = self.manager.get_shared_data("user")

        if self.user:
            try:
                self.first_name = self.user.get("first_name", "")
                self.last_name = self.user.get("last_name", "")
                self.date_of_birth = self.user.get("date_of_birth", "")
                self.id_number = self.user.get("id_number", "")
                self.number_of_passed_subjects = self.user.get("number_of_passed_subjects", "")
                self.previous_school = self.user.get("previous_school", "")
                self.academic_level = self.user.get("current_academic_level", "")
                self.next_of_kin = self.user.get("next_of_kin", "")
                self.gender = self.user.get("gender", "")
                print("User data populated successfully.")
            except Exception as e:
                print(f"Error updating user data: {e}")
        else:
            print("No user data found.")
