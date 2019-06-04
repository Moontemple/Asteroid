from flask import Response
from src.main.python.flaskserv.model.Playlist import Playlist
import os, json

class Vote:
	"""
	TODO
	"""
	def __init__(self, request):
		self.request = request
		self.form = request.form

	def handle_vote(self, s_id, u_id, vote):
		"""
		TODO
		"""

		pl = Playlist(os.environ["PLAYLIST_PATH"])
		playlist = pl.get_playlist()

		# check if already exists in database
		exists = False
		for item in playlist:
			if int(s_id) == int(item[0]):
				exists = True

		if exists:
			pl.update_vote(s_id, vote)
			return Response(
					json.dumps({"message":"updated vote"}), 
					status=200
				)
		else:
			pl.add(self.form)
			return Response(
					json.dumps({"message":"added entry into playlist"}), 
					status=201
				)

	def __call__(self):
		if self.request.__dict__["environ"]["REQUEST_METHOD"] == 'GET':
			return Response(
					json.dumps(Playlist(os.environ["PLAYLIST_PATH"]).get_playlist()),
					status=200
				)

		if "s_id" in self.form and "u_id" in self.form and "vote" in self.form:
			return self.handle_vote(self.form['s_id'], self.form["u_id"], self.form["vote"])

		return Response({"message":"no voting operation interpreted from request"}, status=404) 