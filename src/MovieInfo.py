from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Button import Button
from Screens.Screen import Screen
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.config import *
from Components.ConfigList import *

import json, os
from urllib2 import Request, urlopen


config.EMC.movieinfo = ConfigSubsection()
config.EMC.movieinfo.language = ConfigSelection(default='0', choices=[('0', _('German')), ('1', _('English'))])

class DownloadMovieInfo(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="600,450" title="Movie Information Download (TMDb)">
		<widget name="movie_name" position="5,5" size="600,22" zPosition="0" font="Regular;21" valign="center" transparent="1" foregroundColor="#00bab329" backgroundColor="#000000"/>
		<widget name="movielist" position="10,50" size="570,330" scrollbarMode="showOnDemand"/>
		<widget name="resulttext" position="5,380" size="600,22" zPosition="0" font="Regular;21" valign="center" transparent="1" foregroundColor="#00bab329" backgroundColor="#000000"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EnhancedMovieCenter/img/key_menu.png" position="5,410" size="35,25" alphatest="on" />
		<eLabel text="Setup" position="45,410" size="300,25" font="Regular;18" halign="left" valign="center" transparent="1" />
		</screen>"""

	def __init__(self, session, service, moviename):
		Screen.__init__(self, session)
		self.session = session
		self.service = service
		self["actions"] = HelpableActionMap(self, "EMCMovieInfo",
		{
			"EMCEXIT":		self.exit,
			"EMCOK":		self.ok,
			"EMCMenu":		self.setup,
			#"EMCINFO":		self.info
		}, -1)

		substitutelist = [("."," "), ("_"," "), ("-"," "), ("1080p",""), ("720p",""), ("x264",""), ("h264",""), ("1080i",""), ("AC3","")]
		(moviepath,ext) = os.path.splitext(service.getPath())

		if config.EMC.movie_show_format:
			extVideo = ["ts", "avi", "divx", "f4v", "flv", "img", "ifo", "iso", "m2ts", "m4v", "mkv", "mov", "mp4", "mpeg", "mpg", "mts", "vob", "wmv"]
			for rem in extVideo:
				moviename = moviename.replace(rem,"")

		for (phrase,sub) in substitutelist:
			moviename = moviename.replace(phrase,sub)

		self["movie_name"] = Label("Search results for:   " + moviename)

		response=self.fetchdata("http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=" + moviename.replace(" ","+"))
		if response is not None:
			movies = response["results"]
			movielist = []
			for mov in movies:
				movielist.append((_(str(mov["title"])), mov["id"]))

			self["movielist"] = MenuList(movielist)
			self["resulttext"] = Label(str(len(movies)) + " movies found!")
		else:
			self["movielist"] = MenuList([])
			self["resulttext"] = Label("An error occured! Internet connection broken?")

	def exit(self):
		self.close()

	def ok(self):		
		sel = self["movielist"].l.getCurrentSelection()

		if sel is not None:
			id = sel[1]
			lang = "en"
			if config.EMC.movieinfo.language == 0:
				lang = "de"
			elif config.EMC.movieinfo.language == 1:
				lang = "en"
			response=self.fetchdata("http://api.themoviedb.org/3/movie/" + str(id) + "?api_key=8789cfd3fbab7dccf1269c3d7d867aff&language=" + lang)

			if response is not None:
				blurb = (str(response["overview"])).encode('utf-8')
				runtime = (str(response["runtime"])).encode('utf-8')
				releasedate = (str(response["release_date"])).encode('utf-8')	
				countrylist = response["production_countries"]
				countries  = ""
				for i in countrylist:
					if countries == "":
						countries = i["name"]
					else:
						countries = countries + ", " + i["name"]

				(moviepath,ext) = os.path.splitext(self.service.getPath())
				file(moviepath + ".txt",'w').write("Laufzeit: " + runtime + " Minuten\n\n" + "Inhalt: " + blurb + "\n\nProduktionsland: " + countries)
				self.session.open(MessageBox, _('Movie Information downloaded successfully!'), MessageBox.TYPE_INFO, 10)
				self.exit()
			else:
				self.session.open(MessageBox, _("An error occured! Internet connection broken?"), MessageBox.TYPE_ERROR, 10)

	#def info(self):
		#TODO

	def fetchdata(self, url):
		try:
			headers = {"Accept": "application/json"}
			request = Request(url, headers=headers)
			jsonresponse = urlopen(request).read()
			response = json.loads(jsonresponse)
			return response
		except:
			return None

	def setup(self):
		self.session.open(MovieInfoSetup)



class MovieInfoSetup(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="600,450" title="Movie Information Download Setup">
		<widget name="config" position="5,10" size="570,350" scrollbarMode="showOnDemand" />
		<widget name="key_red" position="0,390" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="#ffffff" font="Regular;18"/>
		<widget name="key_green" position="140,390" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="#ffffff" font="Regular;18"/>
		<ePixmap name="red" pixmap="skin_default/buttons/red.png" position="0,390" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
		<ePixmap name="green" pixmap="skin_default/buttons/green.png" position="140,390" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		#self.session = session
		self.list = []
		self.list.append(getConfigListEntry(_("Language:"), config.EMC.movieinfo.language))
		ConfigListScreen.__init__(self, self.list, session)
		self["actions"] = HelpableActionMap(self, "EMCMovieInfo",
		{
			"EMCEXIT":		self.exit,
			"EMCOK":		self.red,
			#"EMCMenu":		self.setup,
			#"EMCINFO":		self.info,
			"EMCGreen":		self.green,
			"EMCRed":		self.red,
		}, -1)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("OK"))
		
	def exit(self):
		self.close()

	def green(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.close(True)
		
	def red(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False)