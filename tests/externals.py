
silent_mode: bool = False

def silent(mode: bool) -> None:
	global silent_mode
	silent_mode = mode


def errorHandler(msg: str | None, msgs: list[str] | None) -> None:
	global silent_mode
	if not silent_mode:
		if msg != None and msg != "NORAISE":
			print(msg)
		elif msgs != None:
			for msg in msgs:
				print(msg)
		else:
			print("Error handler called with no message or messages")

	if msg is not None and not "NORAISE" in msg:
		raise

def prompter(msg: str) -> None:
	global silent_mode
	if not silent_mode:
		print(msg)