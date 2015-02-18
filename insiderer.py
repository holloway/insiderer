#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
if sys.version_info[0] < 3:
    raise "Must be using Python 3"
import magic
ms = magic.open(magic.MAGIC_NONE)
ms.load()
ms.setflags(magic.MAGIC_MIME)
import re
import os.path
import optparse
import tempfile
import socket
import json
inside_root = os.path.dirname(os.path.abspath(__file__))
inbuilt_path = os.path.join(inside_root, 'lib/bottle')
try:
    sys.path.insert(0, inbuilt_path)
    from bottle import route, request, run, response, static_file
except ImportError as exception:
    sys.stderr.write("Error: Unable to find libraries in %s. Exiting...\n" % sys.path)
    sys.exit(0)

# START DEFAULT CONFIG
host='localhost'
port=80
# END CONFIG
parser = optparse.OptionParser()
parser.add_option("-p", "--port", dest="port", help="Port", type="int")
parser.add_option("-H", "--host", dest="host", help="Host/IP", type="str")
(options, args) = parser.parse_args()
if options.port:
    port = options.port
if options.host:
    host = options.host


@route('/', method='GET')
def index_get():
    return '<!DOCTYPE html><link rel="stylesheet" href="static/screen.css"><body><div id=logo><img src="static/insiderer.png" width=419></div><form method=post enctype=multipart/form-data><span>Choose file(s)</span><input type=file name=a id=files multiple></form><div id=loading></div><script type="text/javascript" src="static/index.js"></script>'


@route('/', method='POST')
def index_post():
    metadata_files = []
    for files, data in request.files.items():
        postfiles = request.files.getall(files)
        for postfile in postfiles:
            tmp_path = tempfile.mkstemp()
            postfile.save(tmp_path[1], True)
            metadata = get_metadata(tmp_path[1], postfile.filename)
            metadata_files.append(metadata)
    response.content_type = 'application/json; charset=utf-8'
    return json.dumps(metadata_files);


def get_metadata(path, filename):
    #print("L@@K", path, os.path.getsize(path))
    def sanitise(mimetype):
        return re.sub(r'[^a-z]', '_', mimetype)

    def sha1OfFile(filepath):
        import hashlib
        sha = hashlib.sha1()
        if os.path.isdir(filepath):
            return None
        with open(filepath, 'rb') as f:
            while True:
                block = f.read(2**10) # Magic number: one-megabyte blocks.
                if not block: break
                sha.update(block)
            return sha.hexdigest()

    mimetype = ms.file(path)
    if "application/octet-stream" in mimetype:
      with open(path, 'rb') as f:

        new_data = extract_jpeg(f.read())
        print("what?????????", new_data[0:11])
        if new_data:
            print("JPEG with weird header found...")
            path = tempfile.NamedTemporaryFile(delete=False).name
            handle = open(path, 'wb')
            handle.write(new_data)
            handle.close()
            

    #
    filedata = {}
    filedata['filename'] = filename;
    filedata['mimetype'] = mimetype;
    filedata['sha1'] = sha1OfFile(path);
    filedata['filesize_bytes'] = os.path.getsize(path);
    filedata['children'] = [];
    mime_app = None;

    mime_app_name = sanitise(mimetype.split(";")[0])
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
        getattr(mime_app_method, mime_app_name)(path, filedata['metadata'], filedata['children'])
    if len(filedata['children']) == 0:
        del filedata['children']
    return filedata

def extract_jpeg(pdf):
  minimum_seek = 20
  startfix = 0
  endfix = 2
  i = 0
  formats = {
      "jpeg": {
          "start": b'\xff\xd8',
          "end": b'\xff\xd9'
      }
  }

  while True:
      print(pdf[0:10])
      istart = pdf.find(formats["jpeg"]["start"])
      print(pdf[0:10])
      if istart < 0:
          iend = pdf.find(b'endstream', istart)
          print("1.Found start/end of JPEG at", istart, iend)
          return pdf[0:iend]
      iend = pdf.find(formats["jpeg"]["end"], istart)
      if iend < 0:
          print("Didn't find end of JPG!")
          return pdf[istart:]
      iend += len(formats["jpeg"]["end"])
      print("2.Found start/end of JPEG at", istart, iend)
      print(pdf[0:10], pdf[istart:istart+10])
      return pdf[istart:iend]

@route('/static/<filename>', method='GET')
def static(filename):
    return static_file(filename, root='static/')

if __name__ == '__main__':
    try:
        run(host=host, port=port, quiet=False)
    except socket.error as e:
        if 'address already in use' in str(e).lower():
            print('ERROR: %s:%i already in use.' % (host, port))
        else:
            raise
