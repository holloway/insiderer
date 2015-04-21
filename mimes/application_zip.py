import zipfile
import tempfile
import os
import sys
import shutil
from lxml import etree
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

def application_zip(path, metadata, children, from_doc=False):
  aZipFile = zipfile.ZipFile(path)
  try:
    tmp_path = None
    tmp_path = tempfile.mkdtemp(dir=insiderer.TMP_DIR)
    aZipFile.extractall(tmp_path)
    for name in aZipFile.namelist():
      childpath = os.path.join(tmp_path, name)
      try:
        if os.path.isdir(childpath):
          pass
        else:
          child = insiderer.get_metadata(childpath, name)
          children.append(child)
      finally:
        if not os.path.isdir(childpath):
          insiderer.safedelete(childpath)
  finally:
    if tmp_path:
      shutil.rmtree(tmp_path)
