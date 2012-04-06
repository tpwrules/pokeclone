#defines a whole bunch of different exceptions for error handling

class QuitException(Exception): #exception to force a quit
	def __init__(self, message=""):
		Exception.__init__(self, message)