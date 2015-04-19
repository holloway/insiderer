import sys
import io
import tempfile
import types
import json
import os
import PyPDF2
import subprocess
import datetime
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

def application_pdf(path, metadata, children):
  pdf_document = PyPDF2.PdfFileReader(open(path, 'rb'))
  metadata["info"] = pdf_document.getDocumentInfo()
  metadata["xmp"] = dict()
  xmp = pdf_document.getXmpMetadata()
  if xmp:
    for name in dir(xmp):
      if name.startswith("_"):
        pass
      else:
        try:
          xmp_data = getattr(xmp, name)
          if isinstance(xmp_data, datetime.datetime):
            metadata["xmp"][name] = str(xmp_data.now())
          else:
            str_xmp_data = str(xmp_data)
            try:
              metadata["xmp"][name] = json.loads(str_xmp_data)
            except Exception:
              if str_xmp_data.startswith("<DOM "):
                metadata["xmp"][name] = xmp_data.toxml()
              else:
                metadata["xmp"][name] = str_xml_data
              pass
        except Exception as e:
          print("Can't serialize %s. %s", name, e)
  try:
    uncompressed_pdf = tempfile.mkstemp(dir=insiderer.TMP_DIR)[1]
    stdout = subprocess.check_output(["pdftk", path, "output", uncompressed_pdf, "uncompress"])
    children.extend(extract_jpegs(open(uncompressed_pdf, 'rb').read()))
  except Exception as e:
    print("PDF exception", e)  
  finally:
    insiderer.safedelete(uncompressed_pdf)

def extract_jpegs(data):
  children = []
  minimum_seek = 20
  startfix = 0
  endfix = 2
  i = 0
  
  formats = {
      "jpeg": {
          "start": b'\xff\xd8',
          "end":   b'\xff\xd9'
      }
  }

  while True:
      istream = data.find(b'stream', i)
      if istream < 0:
          return children

      iend = data.find(b'endstream', istream)
      if iend < 0:
          return children

      istart = data.find(formats["jpeg"]["start"], istream, istream + minimum_seek)
      if istart < 0:
          i = istream + minimum_seek
          continue

      iend = data.find(formats["jpeg"]["end"], iend - minimum_seek)
      if iend < 0:
          iend = len(data)
      else: 
          iend += len(formats["jpeg"]["end"])

      istart += startfix
      child_metadata = process_a_jpeg(data[istart:iend])
      children.append(child_metadata)
      i = iend

def process_a_jpeg(jpeg_data):
  try:
    jpeg_path = tempfile.mkstemp(dir=insiderer.TMP_DIR)[1]
    jpeg_handle = open(jpeg_path, "wb")
    jpeg_handle.write(jpeg_data)
    jpeg_handle.close()
    import mimes.image
    jpeg_metadata = dict()
    mimes.image.image(jpeg_path, jpeg_metadata, None)
  except Exception as e:
    print("PDF JPEG exception", e)  
  finally:
    insiderer.safedelete(jpeg_path)
    
  return jpeg_metadata

