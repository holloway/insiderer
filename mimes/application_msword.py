import requests
import io
import zipfile
import tempfile
import os
import sys
import mimes.application_vnd_oasis_opendocument_text as application_vnd_oasis_opendocument_text
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

def application_msword(path, metadata, children):
  response = None
  try:
    response = requests.post('http://localhost:8080/web-service',
      files={'upload_file[]': open(path,'rb')},
      data={'pipeline':'open document', 'afterconversion': 'zip'})
  except Exception as e:
    metadata["INSIDERER_WARNING"] = "Could not access Docvert on localhost:8080"
    pass
  
  if response is None:
    return

  #print("response.content",response.content)
  zipdata = io.BytesIO(response.content)
  myzip = zipfile.ZipFile(zipdata)

  for name in myzip.namelist():
    if not name.endswith(".odt"):
      continue
    tmp_path = tempfile.mkdtemp(dir=insiderer.TMP_DIR)
    myzip.extract(name, tmp_path)
    odt_path = tmp_path + "/" + name
    application_vnd_oasis_opendocument_text.application_vnd_oasis_opendocument_text(odt_path, metadata, children, True)

