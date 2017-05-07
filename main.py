import os;
import time;
import json;
import requests;
import urllib.parse;
import urllib.request
import pafy;
from omxplayer import OMXPlayer;
from pydub import AudioSegment

addr_serv = "http://192.168.43.19:5000"
dir_path = os.path.dirname(os.path.realpath(__file__));

class Video(object):
	currentTime = 0;
	startTime = 0;

	player = OMXPlayer(dir_path + "/a.mp3", pause=True);
	
	id = "";
	listId = "";
	state = "";
	info = {};

	def dispstart(self):
		return self.startTime;

	def dispcur(self):
		return self.currentTime;

	def setStartTime(self, time):
		self.startTime = time;

	def setCurrentTime(self, time):
		self.currentTime = time;

	def getCurrentTime(self):
		now = int(time.time());
		self.currentTime = now - self.startTime;
		return self.currentTime;

	def create(self):
		videoToPlay = pafy.new("https://www.youtube.com/watch?v=" + self.info["encrypted_id"]);

		bestaudio = videoToPlay.getbestaudio(preftype="m4a", ftypestrict=True);
		file_name =  dir_path + "/music/" + self.id + ".m4a";
		try :
		   bestaudio.download(file_name);
		except:
		   pass
		self.player.quit()
		self.player = OMXPlayer(file_name, pause=True);
		
		AudioSegment.from_file(file_name).export(dir_path + "/music/" + self.id + ".mp3", format="mp3");
		
		r = requests.post(addr_serv + "/serv", data=str(self.id));
		if r.status_code != 200:
			print(r);
			print("error post to 2nd server");
		else:
			print("postb 2nd ok");
	
	def seek(self, timeValue):
		self.player.set_position(timeValue);
		
	def play(self):
		now = int(time.time());
		self.startTime = now - self.currentTime;  # calculate the starting point
		self.state = "1";

		self.player.play();
		
		
		r = requests.post(addr_serv + "/serv", data=self.state);
		if r.status_code != 200:
			print(r);
			print("error post to 2nd server");
		else:
			print("postb 2nd ok");

	def pause(self):
		self.getCurrentTime();
		self.state = "2";

		self.player.pause();
		
		r = requests.post(addr_serv + "/serv", data=self.state);
		if r.status_code != 200:
			print(r);
			print("error post to 2nd server");
		else:
			print("postb 2nd ok");
		
	def stop(self): # useless for the moment but mayby later...
		self.state = "0";
	
	def volume(self, volume):
		self.player.set_volume(-6000 + volume * 60); #-6000/100 car omx va de -6000 a 0 et volume de 0 a 100


class List(object):
	id = "";
	ctt = "";
	videos = [];
	info = {};
	currentIndex = 0;

	def setFromJson(self,arrayJson):
		self.info = arrayJson;

		self.videos = arrayJson["video"];

	def reset(self, id):
		self.id = id;
		self.videos = [];
		self.info = {};
		self.currentIndex = 0;

class Screen(object):
	id = "";
	info = {};
	volume = 100;

	def __init__(self, name = "raspberry", app = "yt-server", uid = "2a026ce9-4429-4c5e-8ef5-0101eddf5671"):
		self.name = name;
		self.app = app;
		self.uid = uid;


class YtServer(object):
	ofs = 0;
	currentCmdIndex = 0;
	bindVals = {};

	def __init__(self):
		self.screen = Screen();
		self.video = Video();
		self.list = List();

		self.createScreenId();
		self.createLoungeToken();
		self.bindValues();
		self.getPairingCode();

	def createScreenId(self):
		r = requests.get("https://www.youtube.com/api/lounge/pairing/generate_screen_id");
		if r.status_code != 200:
			print("error get id");
		else :
			self.screen.id = r.text; #the screen id

	def createLoungeToken(self):
		payload = {"screen_ids": self.screen.id }
		r = requests.post("https://www.youtube.com/api/lounge/pairing/get_lounge_token_batch", params=payload)
		if r.status_code != 200:
			print("error get token");
		else :
			self.screen.info = r.json()['screens'][0];

	def bindValues(self):
		self.bindVals = {
		"device":		 "LOUNGE_SCREEN",
		"id":			 self.screen.uid,
		"name":			 self.screen.name,
		"app":			 self.screen.app,
		"theme":		 "cl",
		"capabilities":	 {},
		"mdx-version":	 "2",
		"loungeIdToken": self.screen.info['loungeToken'],
		"VER":			 "8",
		"v":			 "2",
		"RID":			 "1337",
		"AID":			 "42",
		"zx":			 "xxxxxxxxxxxx",
		"t":			 "1",
				};

		r = requests.post("https://www.youtube.com/api/lounge/bc/bind", params=self.bindVals , data={"count": "0"});

		self.decodeBindStreamFromR(r);

	def decodeBindStreamFromR(self, r):
		textJson = "[" + r.text.split("[",1)[1]; #take all after the 1st [
		textJson = textJson.rsplit("]",1)[0] + "]";# take all before the last ]
		self.decodeBindStreamFromJson(json.loads(textJson));

	def decodeBindStreamFromJson(self, jsonArray):

		for item in jsonArray:
			print("aaaaaaaaaaa");
			print(item);
			index = item[0];
			cmd = item[1];
			self.genericCmd(index, cmd[0], cmd[1:]);
			
			# r = requests.post(addr_serv + "/serv", data=str(item));
			# if r.status_code != 200:
				# print(r);
				# print("error post to 2nd server");
			# else:
				# print("postb 2nd ok");
			
			#moche de faire ça la, mais pour le moment, oui copier coller de next pas beau
			if cmd[0] == "noop" and self.video.state == "1" and not self.video.player.is_playing():
				if self.list.currentIndex + 1 < len(self.list.videos):
					print(">>FIN")
					self.list.currentIndex += 1;
					self.video.currentTime = 0;
					self.video.setStartTime(int(time.time()) - self.video.currentTime);
					self.video.id = self.list.videos[self.list.currentIndex]["encrypted_id"];
					self.video.info = self.list.videos[self.list.currentIndex];
					self.video.listId = self.list.id;

					self.postBind("nowPlaying", {
						"videoId" : self.video.id,
						"currentTime": str(self.video.getCurrentTime()),
						"listId" : self.list.id,
						"currentIndex" : self.list.currentIndex,
						"state" : "3", # loading
						});
					self.video.create();
					self.video.play();

					self.postBind("onStateChange", {
						"currentTime" : str(self.video.getCurrentTime()),
						"state" : self.video.state,
						"duration": self.video.info["length_seconds"],
						"cpn" : "foo"
						});

	def genericCmd(self, index, cmd, args):
		if self.currentCmdIndex > 0 and index <= self.currentCmdIndex:
			print("cmd already did");
			return;

		self.currentCmdIndex = index;
		
		if cmd == "noop":
			print("noop cmd");
		elif cmd == "S":
			self.bindVals["gsessionid"] = args[0];
			print("gsession id: " + self.bindVals["gsessionid"]);
		elif cmd == "c":
			self.bindVals["SID"] = args[0];
			print("session id: " + self.bindVals["SID"]);
		elif cmd == "getNowPlaying":
			if self.video.id == "":
				self.postBind("nowPlaying", {});
			else :
				self.postBind("nowPlaying", {
					"videoId" : self.video.id,
					"currentTime": str(self.video.getCurrentTime()),
					"cct" : self.list.ctt,
					"listId" : self.list.id,
					"currentIndex" : self.list.currentIndex,
					"state" : self.video.state,
					});
		elif cmd == "remoteConnected":
			name = args[0]["name"];
			print("Remote " + name + " connected");
		elif cmd == "remoteDisconnected":
			name = args[0]["name"];
			print("Remote " + name + " disconnected");
		elif cmd == "play":
			self.video.play();

			self.postBind("onStateChange", {
				"currentTime" : str(self.video.getCurrentTime()),
				"state" : self.video.state,
				"duration": self.video.info["length_seconds"],
				"cpn" : "foo"
				});

			print("Play");
		elif cmd == "pause":
			self.video.pause();

			self.postBind("onStateChange", {
				"currentTime" : str(self.video.getCurrentTime()),
				"state" : self.video.state,
				"duration": self.video.info["length_seconds"],
				"cpn" : "foo"
				})

			print("Pause");
		elif cmd == "stopVideo":
			self.postBind("nowPlaying", {});

			print("Stop");
		elif cmd == "getVolume":
			self.postBind("onVolumeChanged", {"volume": self.screen.volume, "muted": "false"});

			print("getVolume");
		elif cmd == "setVolume":
			self.screen.volume = args[0]["volume"];
			self.video.volume(float(self.screen.volume));
			self.postBind("onVolumeChanged", {"volume": self.screen.volume, "muted": "false"});

			print("setVolume", self.screen.volume);
		elif cmd == "next":
			if self.list.currentIndex + 1 < len(self.list.videos):
				self.list.currentIndex += 1;
				self.video.currentTime = 0;
				self.video.setStartTime(int(time.time()) - self.video.currentTime);
				self.video.id = self.list.videos[self.list.currentIndex]["encrypted_id"];
				self.video.info = self.list.videos[self.list.currentIndex];
				self.video.listId = self.list.id;

				self.postBind("nowPlaying", {
					"videoId" : self.video.id,
					"currentTime": str(self.video.getCurrentTime()),
					"listId" : self.list.id,
					"currentIndex" : self.list.currentIndex,
					"state" : "3", # loading
					});
				self.video.create();
				self.video.play();

				self.postBind("onStateChange", {
					"currentTime" : str(self.video.getCurrentTime()),
					"state" : self.video.state,
					"duration": self.video.info["length_seconds"],
					"cpn" : "foo"
					});

				print("Next");
		elif cmd == "previous":
			if self.list.currentIndex > 0:
				self.list.currentIndex -= 1;
				self.video.currentTime = 0;
				self.video.setStartTime(int(time.time()) - self.video.currentTime);
				self.video.id = self.list.videos[self.list.currentIndex]["encrypted_id"];
				self.video.info = self.list.videos[self.list.currentIndex];
				self.video.listId = self.list.id;

				self.postBind("nowPlaying", {
					"videoId" : self.video.id,
					"currentTime": str(self.video.getCurrentTime()),
					"listId" : self.list.id,
					"currentIndex" : self.list.currentIndex,
					"state" : "3", # loading
					});
				self.video.create();
				self.video.play();

				self.postBind("onStateChange", {
					"currentTime" : str(self.video.getCurrentTime()),
					"state" : self.video.state,
					"duration": self.video.info["length_seconds"],
					"cpn" : "foo"
					});

			print("Prev");
		elif cmd == "onUserActivity":
			print("onUserActivity : ");
		elif cmd == "seekTo":
			newTime = args[0]["newTime"];

			self.video.currentTime = int(newTime);
			self.video.startTime = int(time.time()) - self.video.currentTime;
			self.postBind("onStateChange",{
				"currentTime" : self.video.currentTime,
				"state" : self.video.state,
				"duration" : self.video.info["length_seconds"],
				"cpn" : "foo"
				});

			self.video.seek(int(newTime));
				
			print("seek to ", newTime);
		elif cmd == "setPlaylist":
			data = args[0];
			self.video.id = data["videoId"];
			self.video.listId = data["listId"];
			self.list.id = data["listId"];
			self.getInfosPlaylist();
			self.video.setCurrentTime(int(data["currentTime"]));
			self.video.setStartTime(int(time.time()) - self.video.currentTime); # hypothesys that we start imediatly (which is done with .play)

			self.list.currentIndex = 0;
			if data["currentIndex"] != "":
				self.list.currentIndex = int(data["currentIndex"]);

			self.video.info = self.list.videos[self.list.currentIndex];

			if data["ctt"]: # if exist
				self.list.ctt = data["ctt"];
			else:
				self.list.ctt = "";

			self.postBind("nowPlaying", { #try remove that bind and keep only the 2nd
				"videoId":		self.video.id,
				"currentTime":	str(self.video.currentTime),
				"ctt":			self.list.ctt,
				"listId":		self.list.id,
				"currentIndex": self.list.currentIndex,
				"state": "3" #mean loading
				});

			self.video.create();
			self.video.play();

			self.postBind("onStateChange", {
				"currentTime" : str(self.video.getCurrentTime()),
				"state" : self.video.state,
				"duration": self.video.info["length_seconds"],
				"cpn" : "foo"
				});

			print("setPlaylist : ", self.list.id);
		elif cmd == "updatePlaylist":
			data = args[0];
			self.list.id = data["listId"];
			if "videoIds" not in data or data["videoIds"] == "":
				self.list.reset(data["listId"]);
			else :
				self.getInfosPlaylist();

			print("updatePlaylist");



	def getInfosPlaylist(self):
		r = requests.get("https://www.youtube.com/list_ajax?style=json&action_get_list=1&list=" + self.list.id);

		if r.status_code != 200:
			raise('error get playlist info');
		else :
			self.list.setFromJson(json.loads(r.text));

	def postBind(self, sc, params):
		self.ofs += 1;
		postVals = { "count": "1", "ofs": self.ofs };
		postVals["req0__sc"] = sc ;

		for key, value in params.items():
			postVals["req0_" + key] = value;

		print('##########');
		print('##########');
		print(postVals);
		print('##########');
		print('##########');


		self.bindVals["RID"] = "1337";
		r = requests.post("https://www.youtube.com/api/lounge/bc/bind", params=self.bindVals, data=postVals);

		if r.status_code != 200:
			print(r);
			raise("error postbind");
		else:
			print("postbind ok");

	def getPairingCode(self):
		r = requests.post("https://www.youtube.com/api/lounge/pairing/get_pairing_code?ctx=pair", data = {
			"access_type":	"permanent",
			"app":			self.screen.app,
			"lounge_token": self.screen.info['loungeToken'],
			"screen_id":	self.screen.info['screenId'],
			"screen_name":	self.screen.name,
		});
		if r.status_code != 200 :
			raise("error get pair");
		else :
			print(r.text[0:3] + "-" + r.text[3:6] + "-" + r.text[6:9] + "-" + r.text[9:12]);

	def myPrint(self, string):
		print(string);



	def run(self):
		decoder = json.JSONDecoder();
		while True : # normally not needed cause request never end, but in case
			self.ofs +=1;
			bindValsGet = self.bindVals
			bindValsGet["RID"] = "rpc";
			bindValsGet["CI"] = "0";
			params = urllib.parse.urlencode(bindValsGet);
			url = "https://www.youtube.com/api/lounge/bc/bind?%s" % params

			print("-------------");
			print(url);

			r = requests.get(url, stream=True);

			textCmd = "";
			for line in r.iter_lines():
				
				if line: # filtre les lignes vides (keep-alive)
					text = line.decode("utf-8");
##					  print("******");
##					  print(text);
##					  print("******");

					textCmd += text;
					try :
						textCmd = "[" + textCmd.split("[",1)[1]; #take all after the 1st [ to ensure not number took and select json
						textDecoded, index = decoder.raw_decode(textCmd);
						textCmd = textCmd[index:];
						decodeSuccess =	 True;
					except:
						decodeSuccess = False;

					if decodeSuccess:
						print("cmd receiv");
						self.decodeBindStreamFromJson(textDecoded);


##					  print(">" + textCmd);
			print('request ended');





if __name__ == "__main__":
	ytserver = YtServer();
	ytserver.run();