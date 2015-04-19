from wand.image import Image
import os
import sys
import datetime
import dateutil.parser
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

def image(path, metadata, children):
    try:
      with Image(filename=path) as i:
          for key, value in i.metadata.items():
            if not in_blacklist(key, value):
              newkey = insiderer.de_dup(key, metadata)
              metadata[newkey] = value;
    except Exception as e:
       print("Error parsing image", e)
       pass

def in_blacklist(key, value):
  blacklist = { #note that in the value can either be None, a singular value, or a list of values.
    # As to why these ones are blacklisted the reason is that too much information makes it hard to see the important details.
    # It seems unlikely the the shutterspeed could possibly be something that reveals information, so that is excluded.
    # If I got it wrong then please let me know, but do remember that this isn't supposed to display all fields, just important ones (in my opinion)
    # and people can always display metadata in other tools if they want.
    "jpeg:colorspace": "2",
    "jpeg:sampling-factor": "2x2,1x1,1x1",
    "exif:ExifOffset":  None,
    "exif:ApertureValue": None,
    "exif:ColorSpace": None,
    "exif:JPEGInterchangeFormat": None,
    "exif:JPEGInterchangeFormatLength": None,
    "exif:ImageLength": None,
    "exif:ImageWidth": None,
    "exif:LightSource": None,
    "exif:Flash": None,
    "exif:ExposureTime": None,
    "exif:ExifVersion": None,
    "exif:FlashPixVersion": None,
    "exif:ISOSpeedRatings": None,
    "exif:InteroperabilityIndex": None,
    "exif:InteroperabilityOffset": None,
    "exif:InteroperabilityVersion": None,
    "exif:ResolutionUnit": None,
    "exif:ComponentsConfiguration": None,
    "exif:ShutterSpeedValue": None,
    "exif:SubSecTime": None,
    "exif:SubSecTimeDigitized": None,
    "exif:SubSecTimeOriginal": None,
    "exif:FNumber": None,
    "exif:FocalLength": None,
    "exif:Orientation": None,
    "exif:WhiteBalance": None,
    "exif:XResolution": None,
    "exif:XResolution": None,
    "exif:YResolution": None,
    "exif:YCbCrPositioning": None,
    "exif:MeteringMode": None,
    "flash": None,
  }
  if key in blacklist:
    blacklist_values = blacklist[key]
    if blacklist_values is None:
      return True
    if not isinstance(blacklist_values, list):
      blacklist_values = [blacklist_values]
    if value in blacklist_values:
      return True
  print(key)
  try:
    timestamp = dateutil.parser.parse(value).timestamp()
    if wasNotRecently(timestamp):
      return True
  except Exception as e:
    if value.startswith("19") or value.startswith("20"):
      try:
        parts = value.split()
        parts[0] = parts[0].replace(":", "/")
        timestamp = dateutil.parser.parse(parts[0] + " " + parts[1]).timestamp()
        if wasNotRecently(timestamp):
          return True
      except Exception as e:
        pass
    print(e)
    pass
  return False

def wasNotRecently(timestamp):
  nowTimestamp = datetime.datetime.now().timestamp()
  #if timestamp is from a few seconds ago then we can assume it was made during Insiderer extraction and ignore it
  if timestamp > nowTimestamp - insiderer.ignore_date_if_seconds_old: 
    return True

