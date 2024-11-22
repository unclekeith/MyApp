from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText


class PictureSelectScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create a layout to hold the image and the button
        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Add the button to open file manager

        # BoxLayout to hold the selected image
        self.image_container = BoxLayout()
        self.main_layout.add_widget(self.image_container)

        self.add_widget(self.main_layout)

    def open_file_manager(self, instance):
        # Create a file chooser to select image files
        filechooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg"],  # Restrict file types to images
            size_hint=(0.9, 0.9),
        )

        # Create a popup to show the file chooser
        popup = Popup(
            title="Choose a Picture", content=filechooser, size_hint=(0.9, 0.9)
        )

        # Bind the 'on_submit' event of filechooser to select image
        filechooser.bind(on_submit=self.load_image_from_selection)

        popup.open()

    def load_image_from_selection(self, filechooser, selection, *args):
        if selection:
            # Get the selected image path
            image_path = selection[0]

            # Remove any previously loaded image in the container
            self.image_container.clear_widgets()

            # Create an Image widget and add it to the layout
            selected_image = Image(
                source=image_path, allow_stretch=True, keep_ratio=True
            )
            self.image_container.add_widget(selected_image)
            self.ids.send_fab.disabled = False
        else:
            # If no selection, ensure the button is disabled
            self.ids.send_fab.disabled = True

    def dummy_proceed(self):
        MDSnackbar(
            MDSnackbarSupportingText(
                text="Sending proof of certificate is still under construction !",
            ),
            y=dp(24),
            orientation="vertical",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            # background_color="white",
        ).open()
