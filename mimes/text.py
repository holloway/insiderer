import re

def text(path, metadata, children):
	#assume source code with <author> ..</author> <email> sdfsdf</email> in comments
	comment_areas = []
	with open(path, "rt", encoding="utf-8") as handler:
		text = handler.read()
		matches = re.findall(r'//.*?$', text, re.MULTILINE)
		for match in matches:
			comment_areas.append(match[2:])
		matches = re.findall(r'/\*.*?\*/', text, re.MULTILINE | re.DOTALL)
		for match in matches:
			comment_areas.append(match[2:-2])
	comments = "".join(comment_areas)
	matches = re.findall(r'<.*?</.*?>', comments, re.MULTILINE | re.DOTALL)
	for match in matches:
		space_index = None
		greater_index = None
		key = None
		try:
			space_index = match.index(" ")
		except ValueError:
			pass
		try:
			greater_index = match.index(">")
		except ValueError:
			pass
		if not greater_index:
			raise "Can't find > character. "
		if(space_index and greater_index > space_index):
			key = match[1:space_index]
		else:
			key = match[1:greater_index]
		metadata[key] = re.sub(r'<.*?>', '', match, re.MULTILINE)
	return metadata
