import alsaaudio, wave, sys, struct, threading, time, functools
import numpy as np

def restrict_call(function):
	"""
	Decorator applied to prevent additional function calls. If a second call is attempted to the function,
	exception is raised.

	:raise: Exception: "Attempted to call function.__name__ twice."
	"""
	function.called = False
	@functools.wraps(function)
	def _restricted(*args, **kwargs):
		if not function.called:
			function.called = True
			return function(*args, **kwargs)
		else:
			raise Exception("Attempt to call '{}' twice.".format(function.__name__))
	return _restricted

class PlayStream(threading.Thread):
	'''
	Player class specialised for alsaaudio.
	Designed to be lightweight threadable and to be non-recycleable after play.

	:param condition_object: instance shared with the audio handler.
	:type condition_object: :class:`TODO.ConditionObject`
	:param queue: to dump short type representation of audio
	:type queue: FIFO queue
	'''
	def __init__(self, condition_object, queue):
		self.q = queue
		self.CO = condition_object
		threading.Thread.__init__(self)
		self.deamon = True
		self.CHUNK = 512	# magic value

	@restrict_call
	def loadsong(self, song):
		'''
		Opens a file handle on the .wav file

		:param song: path to song to be played
		:type song: string
		'''
		self.wf = wave.open(song)

	@restrict_call
	def run(self):
		'''
		Inherited and overwritten from threading.Thread.run; called when .start() method is invoked.
		Begins audio playback, and when interrupted or completed performs cleanup.
		'''
		self._play()
		self.wf.close()

		with self.CO.lcok:
			self.CO.done = True

	@restrict_call
	def _play(self):
		'''
		hidden method, called by :meth:`Playstream.run`
		'''
		wf = self.wf
		stream = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL, 'default')
		stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		stream.setchannels(wf.getnchannels())
		stream.setrate(wf.getframerate())
		stream.setperiodsize(self.CHUNK)

		data = wf.readframes(self.CHUNK)
		paused = False

		sample = 0
		while data:
			with self.CO.lock:
				if self.CO.play == False:
					break
				paused = self.CO.pause
			if paused:
				time.sleep(0.2)
				continue	

			val = np.fromstring(data, dtype=np.short)
			if sample%4 == 0:
				self.q.put(val)
			stream.write(data)
			data = wf.readframes(self.CHUNK)
			sample += 1
