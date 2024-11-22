from kivymd.uix.screen import MDScreen
from libs.applibs.generated_connection_manager import CoreRoutes


class ResetPasswordScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_enter(self, *agrs, **kwargs):
        # Get user ID from shared data
        user_data = self.manager.get_shared_data("user")
        if user_data:
            self.user_id = user_data.get("id")
        #     if self.user_id:
        #         print(f"User ID: {self.user_id}")
        #     else:
        #         print("User ID not found in shared data.")
        # else:
        #     print("No user data found in shared data.")

    def reset(
        self,
        email: str,
        password: str,
    ):
        response = CoreRoutes(
            client=self.manager.connection_client
        ).patch_reset_password(
            user_id=self.user_id,
            email=email,
            password=password,
        )
        print(response)
