from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.window import Window
import os

Window.size = (300,500)

from kivy import platform
if platform == "android":
	print("INIII android")
	from android.permissions import request_permissions, Permission
	# request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
	request_permissions([
		Permission.CAMERA,
		Permission.WRITE_EXTERNAL_STORAGE,
		Permission.READ_EXTERNAL_STORAGE])

class MainApp(MDApp):
	def build(self):
		return Builder.load_file('design.kv')

	def check_pwd(self, *args, **kwargs):
		user = self.root.ids.screen_login.user_text.text
		pwd = self.root.ids.screen_login.pwd_text.text
		if user != 'a' or pwd != 'a':
			self.dialog = MDDialog(
				title="Wrong user or password ..",
				radius=[20, 7, 20, 7],
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
		else:
			# from android.storage import primary_external_storage_path
			# path = primary_external_storage_path()
			# with open(os.path.join(path,'../../sdcard0/Documents/myfile2.txt'), 'w') as f:
				# f.write('good luck Jithesh, you are doing great!')
			self.root.current='screen_app'

	def closeDialog(self,inst):
		self.dialog.dismiss()

MainApp().run()