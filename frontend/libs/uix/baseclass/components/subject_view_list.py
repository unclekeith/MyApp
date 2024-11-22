from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel  # noqa: F401

KV = """
<SubjectListItem>:
    radius: dp(5)
    theme_bg_color: "Custom"
    md_bg_color: root.background_color
    line_color: 0, 1, 1, 1
    size_hint_y: None
    height: dp(60)
    padding: dp(10)
    
    MDLabel:
        text: root.subject_name
    
    MDLabel:
        text: root.grade
"""


Builder.load_string(KV)


class SubjectListItem(ButtonBehavior, MDBoxLayout):
    subject_name = StringProperty()
    grade = StringProperty()
    background_color = StringProperty("grey")
