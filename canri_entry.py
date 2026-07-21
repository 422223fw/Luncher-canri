from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


def build_screen(on_back):
    root = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
    root.add_widget(Label(text="[b]CANRI — גרסת הדגמה[/b]", markup=True,
                          font_size="24sp", size_hint_y=None, height=dp(55)))
    chat = Label(text="שלום! זה מסך CANRI לדוגמה.", halign="right", valign="top")
    root.add_widget(chat)
    box = TextInput(hint_text="כתוב הודעה...", multiline=False,
                    size_hint_y=None, height=dp(52))
    root.add_widget(box)
    send = Button(text="שלח", size_hint_y=None, height=dp(52))

    def reply(*_):
        text = box.text.strip()
        if text:
            chat.text += f"\n\nאתה: {text}\nCANRI: קיבלתי את ההודעה."
            box.text = ""

    send.bind(on_release=reply)
    root.add_widget(send)
    back = Button(text="חזרה ל-Launcher", size_hint_y=None, height=dp(48))
    back.bind(on_release=lambda *_: on_back())
    root.add_widget(back)
    return root
