import mutagen
import mutagen.id3
from mutagen.easyid3 import EasyID3
import os
import sys
import tempfile

try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

def audio(path, metadata, children):
  try:
    tags = mutagen.File(path)
    #print(tags)
    saveResults(tags, metadata, children)
  except Exception as e:
    print("audio exception", e)
    pass

def saveResults(audioMetadata, metadata, children):
  for key in audioMetadata.keys():
    #print("key:", key)
    if not in_blacklist(key, audioMetadata[key]):
      #print("TYPE:", type(audioMetadata[key]))  
      value = audioMetadata[key]
      if hasattr(value, 'data'):
        #an embedded binary
        name = "cover"
        if hasattr(value, 'desc'):
          name = value.desc
        childpath = tempfile.mkstemp(dir=insiderer.TMP_DIR)[1]
        try:
          tmp_handle = open(childpath, "wb")
          tmp_handle.write(value.data)
          tmp_handle.close()
          child = insiderer.get_metadata(childpath, name)
          children.append(child)
        finally:
           insiderer.safedelete(childpath)
        continue
      if not hasattr(value, '__len__') and hasattr(value, 'text'):
        value = value.text
      if hasattr(value, '__len__') and len(value) == 1:
        value = value[0]
      metadata[key] = value
        
def in_blacklist(key, value):
  blacklist = {
    #note that in the value can either be None, a singular value, or a list of values.
    # As to why these ones are blacklisted the reason is that too much information makes it hard to see the important details.
    # If I got it wrong then please let me know, but do remember that this isn't supposed to display all fields, just important ones (in my opinion)
    # and people can always display metadata in other tools if they want.
    "----:com.apple.iTunes:iTunSMPB": None,
    "COMM:iTunSMPB:eng": None,
    "COMM:iTunNORM:eng": None
  }
  #print(key)
  if key in blacklist:
    blacklist_values = blacklist[key]
    if blacklist_values is None:
      return True
    if not isinstance(blacklist_values, list):
      blacklist_values = [blacklist_values]
    if value in blacklist_values:
      return True

  return False

