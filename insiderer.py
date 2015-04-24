#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import math
if sys.version_info[0] < 3:
    raise "Must be using Python 3"
import re
import os.path
import glob
import optparse
import tempfile
import socket
import cherrypy
import json
import hashlib
import datetime
import dateutil.parser
import shutil

insiderer_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(insiderer_dir)
#from cherrypy.process.plugins import Daemonizer, DropPrivileges, PIDFile

#DropPrivileges(cherrypy.engine, uid=1000, gid=1000).subscribe()
#Daemonizer(cherrypy.engine).subscribe()

# START DEFAULT CONFIG
host='0.0.0.0'
port=80
sslcert = os.path.join(parent_dir, 'cert.pem')
sslcertkey = os.path.join(parent_dir, 'certkey.pem')
if os.path.exists(sslcert) and os.path.exists(sslcertkey):
  port = 443
ignore_date_if_seconds_old = 15

TMP_DIR = '/media/tmp/'
# END CONFIG
parser = optparse.OptionParser()
parser.add_option("-p", "--port", dest="port", help="Port", type="int")
parser.add_option("-H", "--host", dest="host", help="Host/IP", type="str")
parser.add_option("-t", "--tmp", dest="port", help="Temporary directory", type="str")
(options, args) = parser.parse_args()
if options.port:
  port = options.port
if options.host:
  host = options.host

class Site(object):
  exposed = True

  def GET(self):
    return open('static/index.html', 'r').read()

  @cherrypy.tools.json_out()
  def POST(self, **kwargs):
    metadata_files = []
    for key, postfiles in kwargs.items():
      if not isinstance(postfiles, list):
        postfiles = [postfiles]
      for postfile in postfiles:
        tmp_path = None
        try:
          try:
            tmp_path = tempfile.mkstemp(dir=TMP_DIR)[1]
          except IOError as e:
            print("FATAL ERROR: Unable to write to " + TMP_DIR)
            raise e
          handle = open(tmp_path, 'wb')
          handle.write(postfile.file.read())
          handle.close()
          metadata = get_metadata(tmp_path, postfile.filename)
          metadata_files.append(metadata)
        finally:
          if tmp_path is not None:
            safedelete(tmp_path)
    return normalize(metadata_files)

class MimeTypeIcons(object):
  exposed = True

  def GET(self, mimetype):
    icons_dir = "static/icons/"
    icons_local_dir = os.path.join(insiderer_dir, icons_dir)
    chosen_icon = "text.svg"
    parts = mimetype.split("/")
    parts[0] = sanitise(parts[0])
    parts[1] = sanitise(parts[1])
    exact_mimetype = parts[0] + "_" + parts[1] + ".svg"
    basic_mimetype = parts[0] + ".svg"
    if os.path.exists(os.path.join(icons_local_dir, exact_mimetype)):
      raise cherrypy.HTTPRedirect(icons_dir + exact_mimetype)
    elif os.path.exists(os.path.join(icons_local_dir, basic_mimetype)):
      raise cherrypy.HTTPRedirect(icons_dir + basic_mimetype)
    else:
      raise cherrypy.HTTPRedirect(icons_dir + "text.svg")

class Tests(object):
  exposed = True

  def GET(self, path="", **kwargs):
    if path == "":
      return open("static/tests/index.html", 'r').read()
    elif path == "list":
      list = []
      test_pattern = os.path.join(insiderer_dir, "tests") + "/*"
      paths = glob.glob(test_pattern)
      for path in paths:
        if not path.endswith(".json"):
          list.append(os.path.basename(path))
      cherrypy.response.headers['Content-Type'] = "application/json"
      return json.dumps(list).encode("utf-8")
    test = {}
    actual_metadata = None
    tmp_path = None
    try:
      tmp_path = tempfile.mkstemp(dir=TMP_DIR)[1]
      source = os.path.join("tests", path)
      shutil.copyfile(source, tmp_path)
      actual_metadata = json.dumps(normalize(get_metadata(tmp_path, os.path.basename(path))))
    finally:
      if tmp_path is not None:
        safedelete(tmp_path)
    print(    actual_metadata)
    expected_metadata = open(os.path.join("tests", path + ".json"), 'rb').read().decode('utf-8')
    cherrypy.response.headers['Content-Type'] = "application/json"
    return json.dumps({'filename':path, 'actual':actual_metadata, 'expected':expected_metadata}).encode('utf-8')
  
def sanitise(mimetype):
  return re.sub(r'[^a-z]', '_', mimetype)

def get_metadata(path, filename):
  def get_mime(path):
    import magic
    mimey_the_mimetype = magic.from_file(path, mime=True).decode('utf-8')
    if mimey_the_mimetype == "application/octet-stream": #well that's useless
      description = magic.from_file(path).decode('utf-8').lower()
      if "audio " in description:
        mimey_the_mimetype = "audio/mpeg"
    return mimey_the_mimetype

  def sha1OfFile(filepath):
    sha = hashlib.sha1()
    if os.path.isdir(filepath):
      return None
    with open(filepath, 'rb') as f:
      while True:
        block = f.read(2**10) # Magic number: one-megabyte blocks.
        if not block: break
        sha.update(block)
      return sha.hexdigest()

  mimetype = get_mime(path)
   
  mime_app_name = sanitise(mimetype.split(";")[0])
  filedata = {}
  filedata['filename'] = filename;
  filedata['mimetype'] = mimetype.split(";")[0];
  filedata['sha1'] = sha1OfFile(path);
  filedata['filesize_bytes'] = os.path.getsize(path);
  filedata['children'] = [];
  mime_app = None;

  import_obj = 'mimes.%s' % mime_app_name
  if not os.path.exists(import_obj.replace('.', '/') + ".py"):
    mime_app_name = sanitise(mimetype.split("/")[0])
    import_obj =  'mimes.%s' % mime_app_name
    if not os.path.exists(import_obj.replace('.', '/') + ".py"):
      import_obj = None

  if import_obj:
    mime_app = __import__(import_obj)

  if mime_app: #if there was a handler for this mimetype
    mime_app_method = getattr(mime_app, mime_app_name)
    filedata['metadata'] = {}
    #print(mime_app_name)
    getattr(mime_app_method, mime_app_name)(path, filedata['metadata'], filedata['children'])
  if len(filedata['children']) == 0:
    del filedata['children']
  return filedata

def safedelete(path):
    if os.path.isdir(path):
      print("Can't safedelete directory", path)
      return
    sector = 4096
    data = ""
    try:
      filesize = os.path.getsize(path)
      cycles = math.ceil(filesize / sector) + 1
      with open(path, 'wb') as safehandle:
        safehandle.seek(0)
        for x in range(0, cycles):
          safehandle.write(os.urandom(sector))
    except Exception as e:
      print(e)
    finally:
      os.unlink(path)
    
def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'SAMEORIGIN'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src=self"

def normalize(obj):
  newobj = None
  if isinstance(obj, dict):
    newobj = dict()
    keys = list(obj.keys())
    keys.sort()
    for key in keys:
      newkey = str(key)
      newkey = re.sub(r'[\.,_-]', ' ', newkey).replace("@", "").replace("#","").replace("/","").lower().strip()
      if newkey.startswith("xmlns"):
        continue
      if ":" in newkey:
        newkey = newkey[newkey.rfind(":") + 1:]
      newkey = de_dup(newkey, newobj)
      response = normalize(obj[key])
      if contains_values(response):
        newobj[newkey] = response
  elif isinstance(obj, list):
    newobj = list()
    for i in range(len(obj)):
      response = normalize(obj[i])
      if contains_values(response):
        newobj.append(response)
  elif isinstance(obj, int) or obj is None:
    newobj = obj
  else:
    newobj = str(obj).replace("\n", " ")
    newobj = normalize_date(newobj)
  return newobj

def normalize_date(datestring):
  if len(datestring) < 8: # Unfortunately dateutil.parser.parse will think strings like "319/1" are dates, so to avoid that we filter by length. If it's shorter than "YYYYMMDD" then we won't possibly normalizing it into a date.
    return datestring
  try:
    datestring = normalize_malformed_date(datestring)      
    datetime = dateutil.parser.parse(datestring)
    isoformat = datetime.isoformat()
    if datetime.isoformat() != "1972-01-19T00:00:00":
      datestring = isoformat
  except Exception as e:
    if datestring.startswith("D:"):
      return normalize_date(datestring[2:].replace("'", ""))
  return datestring

def normalize_malformed_date(datestring):
  if (datestring.startswith("19") or datestring.startswith("20")) and datestring.count(" ") == 1 and datestring.count(":") == 4:
    # Unfortunately the dateutil parser will read "2014:09:15 14:06:02" as "2015-04-21T14:06:02" (as of today) because it doesn't like colons between year:month:day so we detect that scenario and change it
    parts = datestring.split(" ")
    datestring = parts[0].replace(":", "/") + " " + parts[1]
    return datestring
  return datestring

def contains_values(obj):
  if isinstance(obj, dict):
    return len(obj.keys()) > 0
  elif isinstance(obj, list):
    return len(obj) > 0
  return True

def de_dup(key, obj): #deduplicate keys so that they don't overwrite oneanother
  # Note that key order must be sorted before using de_dup or else two keys that are "description" and "exif:description" will be be insiderer.normalize()d and de_duped to description and description2 in random order, and randomly break tests
  addon = ""
  while (key + str(addon)) in obj:
    if addon == "":
      addon = 2
    else:
      addon += 1
  return key + str(addon)

if __name__ == '__main__':
  global_options = {
    'server.socket_host': host,
    'server.socket_port': port
  }
  if os.path.exists(sslcert):
    global_options.update({
      'server.ssl_module':      'builtin',
      'server.ssl_certificate': sslcert,
      'server.ssl_private_key': sslcertkey
    });

  conf = {
      'global': global_options,
      '/': {
          'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
          'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
          'tools.secureheaders.on': True
      },
      '/mimetypeicon': {
           'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
           'tools.secureheaders.on': True,
       },
      '/tests/*': {
           'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
           'tools.secureheaders.on': True,
       },
      '/static': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': './static'
      }
  }
  webapp = Site()
  webapp.mimetypeicon = MimeTypeIcons()
  webapp.tests = Tests()
  cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize', secureheaders, priority=60)
  cherrypy.quickstart(webapp, '/', conf)


