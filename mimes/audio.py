import mutagen
from mutagen.easyid3 import EasyID3
import os
import sys

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
    saveResults(tags, metadata)
  except Exception as e:
    print("audio excep", e)
    pass

def saveResults(audioMetadata, metadata):
  for key in audioMetadata.keys():
    if not in_blacklist(key, audioMetadata[key][0]):
      len_values = len(audioMetadata[key])
      if len_values == 1:
        metadata[key] = audioMetadata[key][0]
      elif len_values > 1:
        metadata[key] = audioMetadata[key]

def in_blacklist(key, value):
  blacklist = { #note that in the value can either be None, a singular value, or a list of values.
    # As to why these ones are blacklisted the reason is that too much information makes it hard to see the important details.
    # If I got it wrong then please let me know, but do remember that this isn't supposed to display all fields, just important ones (in my opinion)
    # and people can always display metadata in other tools if they want.
    "----:com.apple.iTunes:iTunSMPB": None    
  }
  if key in blacklist:
    blacklist_values = blacklist[key]
    if blacklist_values is None:
      return True
    if not isinstance(blacklist_values, list):
      blacklist_values = [blacklist_values]
    if value in blacklist_values:
      return True

  return False

