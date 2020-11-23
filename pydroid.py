"""
note: if running on a non android platform you will only have access to is_android function 

info:

most of the code can be found here - https://developer.android.com/docs/

to compile java files with buildozer just add the java filename to 'android.add_src' line in your buildozer.spec file

for information on pyjnius visit - https://pyjnius.readthedocs.io/en/latest/
python-4-android page - https://python-for-android.readthedocs.io/en/latest/troubleshooting/
a better understanding for python-4-android check this link out - https://github.com/kivy/python-for-android/issues/388 

I spent quite a few days working a lot of undocumented python4android code out lost many hair strands in the process!!"""

__version__ = "0.1.3"
__author__ = "Paul Millar"

import threading

try:
	from android.runnable import run_on_ui_thread
	from android import api_version as API_VERSION
	_is_android = True
	import time
except ImportError:
	_is_android = False


def is_android():
	return _is_android
	
if is_android():

	from jnius import autoclass
	from jnius import cast
	from android import activity

	## Java STD classes
	String = autoclass("java.lang.String")
	CharSequence = autoclass('java.lang.CharSequence')
	Locale = autoclass("java.util.Locale")

	## Android classes
	Toast = autoclass('android.widget.Toast')
	PythonActivity = autoclass('org.kivy.android.PythonActivity')
	TexttoSpeech = autoclass("android.speech.tts.TextToSpeech")
	Context = autoclass('android.content.Context')
	Activity = autoclass("android.app.Activity")
	Intent = autoclass("android.content.Intent")
	## android SPEECH api
	
	RecognizerIntent = autoclass('android.speech.RecognizerIntent')
	
	## Android networking
	Uri = autoclass("android.net.Uri")

	RingtoneManager = autoclass("android.media.RingtoneManager")
	Ringtone = autoclass("android.media.Ringtone")
	
	## Android contacts
	#ContactsContract = autoclass('android.provider.ContactsContract')
	#Intents = autoclass('android.provider.Contacts.Intents')
	
	## Use the logging object to show output on logcat
	Log = autoclass("android.util.Log")
	TAG = "python"
	
	## Custom Classes
	Gps = autoclass("Gps")
	Contact = autoclass("Contact")
	
	CURRENT_CONTEXT = PythonActivity.mActivity.getApplicationContext()

else:
	# Not Android platform so create dummy decorators
	def run_on_ui_thread(func):
		def wrapper(*args):
			return False
		return wrapper


def navigate_google_maps(uri):
	if is_android():
		gmm_intent_uri = Uri.parse(uri)
		map_intent = Intent(Intent.ACTION_VIEW, gmm_intent_uri)
		map_intent.setPackage('com.google.android.apps.maps')
		PythonActivity.mActivity.startActivity(map_intent)
	else:
		print("Cannot send intent to Google Maps as not Android platform")


def navigate_waze(lat, lng):
	if is_android():
		"""
		uses the older url format waze://. use https for newer phones
		"""
		#url = f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"
		#url = f"https://waze.com/ul?ll={lat},{lng}"
		url = f"waze://?ll={lat},{lng}&navigate=yes&z=4"
		intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
		PythonActivity.mActivity.startActivity(intent)
	else:
		print("Cannot send intent to waze as not Android Platform")


def play_system_sound(sound_type):
	"""
	play_system_sound(sound_type) -> None
	Parameters:
		sound_type - str
			"notification"
			"alert"
			"ringtone"
	"""
	if is_android():
		if sound_type == "notification":
			uri_type = RingtoneManager.TYPE_NOTIFICATION
		elif sound_type == "alert":
			uri_type = RingtoneManager.TYPE_ALARM
		elif sound_type == "ringtone":
			uri_type = RingtoneManager.TYPE_RINGTONE
		else:
			raise NameError('''sound_type did not match any defaults. use one of these three - "notification", ""''')
		sound_uri = RingtoneManager.getDefaultUri(uri_type)
		ringtone = RingtoneManager.getRingtone(PythonActivity.mActivity, sound_uri)
		ringtone.play()
		return True
	else:
		return False


def ask_permission(permissions=[], timeout=5):
	"""
	api level > 21 requires permissions to be prompted by the user rather than set in the manifest file
	dialog box will oonly be displayed if permission not applied
	"""
	if is_android():
		global PythonActivity
		if API_VERSION > 21:
			print(f"NOW ASKING FOR PERMISSIONS. API LEVEL = {API_VERSION}")
			PythonActivity.requestPermissions(permissions)
			time.sleep(timeout)
		else:
			print(f"THIS OS DOES NOT REQUIRE PERMISSIONS TO BE ASKED. ADD PERMISSIONS IN BUILDOZER.SPEC INSTEAD\nAPI LEVEL = {API_VERSION}")
		return True
	else:
		return False


@run_on_ui_thread
def toast(message="", long_time=False):
	"""
	displays a toast dialog box
	"""
	if is_android():
		c = cast(CharSequence, String(message))
		if long_time:
			length = Toast.LENGTH_LONG
		else:
			length = Toast.LENGTH_SHORT
		Toast.makeText(PythonActivity.mActivity, c, length).show()	
		return True
	else:
		return False		


def get_telephony_manager():
	if is_android():
		ask_permission(["android.permission.READ_PHONE_STATE"])
		return PythonActivity.mActivity.getSystemService(Context.TELEPHONY_SERVICE)
	else:
		None


def insert_contact(name, phone):
	"""
	Requires Contact.java 
	"""
	if is_android():
		Contact.addContact(PythonActivity.mActivity, name, phone)
		return True
	else:
		return False


@run_on_ui_thread
def phone_call(phone_number):
	## note: make skype call "skype:<username>?call&video=false"
	if is_android():
		i = Intent('android.intent.action.VIEW')
		i.setData(Uri.parse("tel:" + phone_number))
		Log.i(TAG, "tel:" + phone_number)
		PythonActivity.mActivity.startActivity(i)
		return True
	else:
		return False


class SpeechtoText:
	
	""" SpeechtoText only needs to be instanced once. call show_sp2txt_dialog to prompt user for speech """
	
	REQUEST_SPEECH_RECOGNIZER = 3000
	
	def __init__(self):
		if is_android():
			## reflect our activity with the main apps activity
			self.current_activity = cast("android.app.Activity", PythonActivity.mActivity)
			## tell android where to send our speech results
			activity.bind(on_activity_result=self.on_activity_result)
	
	@run_on_ui_thread
	def show_sp2txt_dialog(self, callback):
		"""callback = must be a python method with a text parameter this will be the processed text from androids speechtotext algorithim"""
		if is_android():
			self._callback = callback
			
			## Create our intent for the recognizerspeech
			intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
			intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
			RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
			intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Tell me what you want to send?")
			## start the speech recognizer activity
			self.current_activity.startActivityForResult(intent, SpeechtoText.REQUEST_SPEECH_RECOGNIZER)
			return True
		else:
			return False
		
	def on_activity_result(self, request_code, result_code, intent):
		if request_code == SpeechtoText.REQUEST_SPEECH_RECOGNIZER:
			if result_code == Activity.RESULT_OK:
				results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
				self._callback(results.get(0))

class GeocoderError(Exception):
	def __init__(self, message):
		super(GeocoderError, self).__init__()
		self.message = message

class SCGps:
	
	"""SCGps must be compiled with Gps.java in order use the GPS Android API"""
	geo_address = {}
	is_listening = False
	
	# this method should only be called once
	@run_on_ui_thread
	def start_gps_listener(self):
		"""
		Description: Make sure ACCESS_FINE_LOCATION is set in permissions
		run ask_permission("android.permission.ACCESS_FINE_LOCATION") before starting listener
		"""
		if is_android():
			self._gps = Gps(PythonActivity.mActivity)
			SCGps.is_listening = True
	
	def is_loc_enabled(self):
		if is_android():
			return self._gps.isLocationEnabled()
		else:
			return False
	
	def stop_service(self):
		if is_android():
			self._gps.stopListening()
			return True
		else:
			return False
	
	def getgps(self):
		if is_android():
			return (self._gps.getLatitude(), self._gps.getLongitude())
		else:
			return (52.644699, 1.282040)
	
	@run_on_ui_thread
	def getlocations(self, lat, lng):
		""" this method is a mess needs cleaning up. I managed to get the desired effect
		only not sure how to return values from Androids UI thread so created new strings from the Java string
		as I think there is some garbage collection going on. No crashes just a null reference pointer
		so had to convert from ascii to unicode in order to force python to create new string arrays in memory
		these get filled in with the returned Java string. Also because there is no synchronization with UI thread and the
		calling thread it there is no guarentee that a returning string will come back straight away
		so created a static LIST and fill it in within this method. make sure to wrap this method call up within
		a GeoException error this will ensure that everything went well and there will atleast be something in the static GEO_ADDRESS buffer
		
		GEO_ADDRESS = ["CITY", "COUNTY", "COUNTRY", "POSTCODE", "STREETNAME", "NUMBER"] 
		other wise it contains empty strings remember the properties are unicode not ascii"""
		if is_android():
			self.reset_geo_address()
			exception_message = "Geocoder was unable to identify address."
			if lat == 0.0 and lng == 0.0:
				exception_message = "Latitude and Longitude were both Zero"
			else:
				s = self._gps.getGeoLocation(lat, lng)
				if "\n" in s:
					lst = s.split('\n')
					if len(lst) == 6:
						#SCGps.GEO_ADDRESS = [unicode(geo_prop) for geo_prop in lst]
						# convert each item in list to unicode
						geo = [str(geo_prop) for geo_prop in lst]
						geo.append(str(lat))
						geo.append(str(lng))
						# convert list to GeoAddress namedtuple
						SCGps.geo_address["county"] = geo[0]
						SCGps.geo_address["country"] = geo[1]
						SCGps.geo_address["postcode"] = geo[2]
						SCGps.geo_address["streetname"] = geo[3]
						SCGps.geo_address["number"] = geo[4]
						SCGps.geo_address["latitude"] = geo[5]
						SCGps.geo_address["longitude"] = geo[6]
						return True
						#["city", "county", "country", "postcode", "streetname", "number", "latitude", "longitude"]
					else:
						exception_message = "Geocoder returned less than six items. Check Network connection."
				else:
					exception_message = "Geocoder returned nothing."
			self.reset_geo_address()
			raise GeocoderError(exception_message)
		else:
			GeocoderError("Not running on Android platform")
	
	def reset_geo_address(self):
		SCGps.geo_address = {"city": "", "county": "", "postcode": "", "streetname": "", "number": "", "latitude": 0.0, "longitude": 0.0}


class TextSpeak:

	"""
	converts text to speech
	"""
	
	def __init__(self, **kwargs):
		## setup the tts engine. can not be initiated during runtime
		## this only needs to be initiated once
		if is_android():
			self.__tts = TexttoSpeech(PythonActivity.mActivity, None)
			self.__tts.setLanguage(Locale.US)
	
	@run_on_ui_thread
	def speak(self, text=""):
		if is_android():
			c = cast(CharSequence, String(text))
			self.__tts.speak(c, TexttoSpeech.QUEUE_ADD, None, String("python-speak-id"))
			return True
		else:
			return False

class LogCatReader(threading.Thread):

	"""Reads from the logcat stream. Needs work!!!!"""

	def __init__(self, callback, **kwargs):
		super(LogCatReader, self).__init__()
		self.callback = callback
		self.quit = threading.Event()
	
	def run(self):
		if is_android():
			InputStreamReader = autoclass("java.io.InputStreamReader")
			BufferedReader = autoclass("java.io.BufferedReader")
			Runtime = autoclass("java.lang.Runtime")
			process = Runtime.getRuntime().exec("logcat -v threadtime")
			input_stream = process.getInputStream()
			input_stream_reader = InputStreamReader(input_stream)
			buffered_reader = BufferedReader(input_stream_reader)
			while not self.quit.isSet():
				line = buffered_reader.readLine()
				print("\n\n{}\n\n".format(line))
		
