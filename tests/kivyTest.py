from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        # 레이아웃 설정
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 레이블 생성
        self.label = Label(text="버튼을 클릭하세요!", font_size=24)
        layout.add_widget(self.label)

        # 버튼 생성
        button = Button(text="클릭", font_size=24)
        button.bind(on_press=self.on_button_click)  # 버튼 클릭 시 이벤트 바인딩
        layout.add_widget(button)

        return layout

    # 버튼 클릭 시 실행될 함수
    def on_button_click(self, instance):
        self.label.text = "버튼이 클릭되었습니다!"

# 앱 실행
if __name__ == "__main__":
    MyApp().run()
