import sys
import io
import tempfile
import types
import PyPDF2
import json
import os
import re
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass


def application_pdf(path, metadata, children):
  fp = open(path, 'rb')

  pdf = PyPDF2.PdfFileReader(fp)

  data = pdf.getDocumentInfo()
  if data:
    metadata["info"] = data

  data = pdf.getXmpMetadata()
  if data:
    metadata["xmp"] = data

  list(pdf.pages) # Process all the objects.

  pdf.read(fp)


  objects = pdf.resolvedObjects

  #_authenticateUserPassword', '_buildDestination', '_buildField', '_buildOutline', '_checkKids', '_decrypt', '_decryptObject', '_flatten',
  #'_getObjectFromStream', '_override_encryption', '_pairs', '_writeField', '_zeroXref', 'cacheGetIndirectObject', 'cacheIndirectObject',
  #'decrypt', 'documentInfo', 'flattenedPages', 'getDocumentInfo', 'getFields', 'getIsEncrypted', 'getNamedDestinations', 'getNumPages', 'getObject',
  #'getOutlines', 'getPage', 'getPageLayout', 'getPageMode', 'getXmpMetadata', 'isEncrypted', 'namedDestinations', 'numPages', 'outlines', 'pageLayout',
  #'pageMode', 'pages', 'read', 'readNextEndLine', 'readObjectHeader', 'resolvedObjects', 'stream', 'strict', 'trailer', 'xmpMetadata',
  #'xref', 'xrefIndex', 'xref_objStm']



  def findIn(haystack, children, depth=0):
    def parseThing(tmp_metadata, key, child, stream):
      if isinstance(tmp_metadata, bytes):
        tmp_file = tempfile.NamedTemporaryFile(delete=False).name
        handle = open(tmp_file, 'wb')
        #print("before", tmp_metadata[0:10])
        tmp_metadata = PyPDF2.filters.decodeStreamData(stream)
        #print(stream.get("/Filter", ()))
        #print("after ", tmp_metadata[0:10])

        #tmp_metadata = PyPDF2.filters.FlateDecode.decode(tmp_metadata)
        #jpeg = extract_jpeg(tmp_metadata)
        handle.write(tmp_metadata)
        #print("  - child[getObjectBytes] ", type(tmp_metadata), tmp_file)
        return insiderer.get_metadata(tmp_file, str(key))
      else:
        #print("  - child[getObject] ", type(tmp_metadata), tmp_metadata)
        try:
          tmp_metadata = re.sub('<PyPDF2(.*?)>', '"w"', str(tmp_metadata)).replace("'", '"')
          return json.loads(tmp_metadata)
        except Exception as e:
          #print("ERROR Unable to parse as JSON", e, str(tmp_metadata))
          return tmp_metadata

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
          istream = pdf.find(b'stream', i)
          if istream < 0:
              break
          iend = pdf.find(b'endstream', istream)
          if iend < 0:
              raise Exception("Didn't find end of stream!")

          istart = pdf.find(formats["jpeg"]["start"], istream, istream + minimum_seek)
          if istart < 0:
              iend = pdf.find(b'endstream', istart)
              return pdf[istream:iend]
          iend = pdf.find(formats["jpeg"]["end"], iend - minimum_seek)
          if iend < 0:
              raise Exception("Didn't find end of JPG!")

          istart += startfix
          iend += endfix
          return pdf[istart:iend]

    #print(haystack)
    #print(dir(haystack))
    #print("dESCND", haystack)
    keys = None
    if hasattr(haystack, "keys"):
      keys = haystack.keys()
    elif hasattr(haystack, "__len__"):
      keys = list(range(0, haystack.__len__()))
    else:
      pass
      #print("ERROR descending on", type(haystack), dir(haystack))

    #print(" - keys", keys)
    try:
      for key in keys:
        value = None
        try:
          value = haystack[key]
          #print(" - keys:", key, "value", type(value), value)
          if isinstance(value, PyPDF2.generic.EncodedStreamObject):
            pass
            #print("PyPDF2.generic.EncodedStreamObject!!!!", dir(value))
        except:
          continue

        if isinstance(value, PyPDF2.generic.IndirectObject):
          #print("    +   ", type(value), dir(value))
          if hasattr(value, "getObject"):
            value = value.getObject()
            #print("    !   ", type(value), dir(value))

        if value is None:
          pass
        elif isinstance(value, str) or isinstance(value, PyPDF2.generic.BooleanObject) or isinstance(value, PyPDF2.generic.NumberObject) or isinstance(value, PyPDF2.generic.FloatObject):
          pass
          #print("    -    string", value)
        elif isinstance(value, PyPDF2.generic.EncodedStreamObject):
          #print("    -    ", type(value), dir(value))
          child = {}
          if hasattr(value, "getXmpMetadata"):
            tmp_metadata = value.getXmpMetadata();
            if tmp_metadata:
              #print("  - child ", type(tmp_metadata), tmp_metadata)
              child["xmp"] = metadata
          if hasattr(value, "getData"):
            tmp_metadata = value.getData()
            if tmp_metadata:
              child["data"] = parseThing(tmp_metadata, key, child, value)
          if hasattr(value, "getObject"):
            tmp_metadata = value.getObject()
            if tmp_metadata:
              child["object"] = parseThing(tmp_metadata, key, child, value)
          #print("    -         CHILD ", child)
          if len(child.keys()):
            if child["data"] and child["data"]["mimetype"] == "inode/x-empty; charset=binary":
              pass
            else:
              children.append(child)
        elif isinstance(value, dict) or isinstance(value, PyPDF2.generic.DictionaryObject) or isinstance(value, PyPDF2.generic.ArrayObject):
          #print("   - group of...", type(value))
          if depth < 10:
            findIn(value, children, depth + 1)
        else:
          pass
          #print("    -   HUH?", type(value) , dir(value))
          #print(value)
    except RuntimeError:
      pass
    #print("END dESCND")

  #print("OBJECTS", objects)

  files = [];
  findIn(objects, children)

  def normalize(children):
    #print(children)
    keys = None
    if hasattr(children, "keys"):
      keys = children.keys()
    elif hasattr(children, "__len__"):
      keys = list(range(0, children.__len__()))
    for key in keys:
      item = children[key]
      if isinstance(item, PyPDF2.generic.PdfObject):
        item = str(item)
        children[key] = item

      if isinstance(item, list) or isinstance(item, dict):
        normalize(item)


  normalize(children)


  #'_authenticateUserPassword', '_buildDestination', '_buildField', '_buildOutline', '_checkKids', '_decrypt', '_decryptObject', '_flatten',
  #'_getObjectFromStream', '_override_encryption', '_pairs', '_writeField', '_zeroXref', 'cacheGetIndirectObject', 'cacheIndirectObject', 'decrypt',
  #'documentInfo', 'flattenedPages', 'getDocumentInfo', 'getFields', 'getIsEncrypted', 'getNamedDestinations', 'getNumPages', 'getObject',
  #'getOutlines', 'getPage', 'getPageLayout', 'getPageMode', 'getXmpMetadata', 'isEncrypted', 'namedDestinations', 'numPages', 'outlines',
  #'pageLayout', 'pageMode', 'pages', 'read', 'readNextEndLine', 'readObjectHeader', 'resolvedObjects', 'stream', 'strict', 'trailer',
  #'xmpMetadata', 'xref', 'xrefIndex', 'xref_objStm']

  #with Image(filename=path) as i:
  #    for key, value in i.metadata.items():
  #      metadata[key.strip()] = value;
