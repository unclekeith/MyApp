from datetime import datetime

from kivymd.uix.screen import MDScreen


class CameraScreen(MDScreen):
     def capture(self):
        capture_time = datetime.now()
        self.ids.zbarcam.export_to_png(
            f"data/images/{capture_time.year}_{capture_time.month}_{capture_time.day}_{capture_time.hour}{capture_time.minute}{capture_time.second}.png"
        )