from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

KV = '''
<ClickableTextFieldRound>:
	pwd_text:pwd_text
	user_text:user_text
	size_hint_y: None
	height: pwd_text.height

	MDTextField:
		id: pwd_text
		hint_text: "Password"
		text: root.text
		password: True

	MDIconButton:
		icon: "eye-off"
		pos_hint: {"center_y": .5}
		pos: pwd_text.width - self.width + dp(8), 0
		theme_text_color: "Hint"
		on_release:
			self.icon = "eye" if self.icon == "eye-off" else "eye-off"
			pwd_text.password = False if pwd_text.password is True else True

	MDTextField:
		id: user_text
		pos_hint: {"center_y": 1.5}
		hint_text: "Username"
		text: root.text

	MDIconButton:
		icon: "language-python"
		pos_hint: {"center_y": -0.2 , "center_x": .5}
		id: m_button
		on_press: app.check_pwd()

	# MDIconButton:
	#     icon: "eye-off"
	#     pos_hint: {"center_y": .5}
	#     pos: user_text.width - self.width + dp(8), 0
	#     theme_text_color: "Hint"
	#     on_release:
	#         self.icon = "eye" if self.icon == "eye-off" else "eye-off"
	#         user_text.password = False if user_text.password is True else True


MDScreen:

	ClickableTextFieldRound:
		id:ClickableTextFieldRound
		size_hint_x: None
		width: "300dp"
		# hint_text: "Password"
		pos_hint: {"center_x": .5, "center_y": .5}
'''


class ClickableTextFieldRound(MDRelativeLayout):
	text = StringProperty()
	hint_text = StringProperty()
	# Here specify the required parameters for MDTextFieldRound:
	# [...]


class wz_app(MDApp):
	def build(self):
		return Builder.load_string(KV)

	def check_pwd(self, *args, **kwargs):
		user = self.root.ids.ClickableTextFieldRound.user_text.text
		pwd = self.root.ids.ClickableTextFieldRound.pwd_text.text
		if user != 'a' or pwd != '1':
			self.dialog = MDDialog(
				title="Wrong user or password ..",
				buttons=[
					MDFlatButton(
						text="OK",
						theme_text_color="Custom",
						text_color=self.theme_cls.primary_color,
						on_release= self.closeDialog
					)
				],
				)
			self.dialog.open()

	def closeDialog(self,inst):
		self.dialog.dismiss()

wz_app().run()