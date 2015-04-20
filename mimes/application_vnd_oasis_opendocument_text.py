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

def application_vnd_oasis_opendocument_text(path, metadata, children, from_doc=False):
  odtzip = zipfile.ZipFile(path)
  try:
    tmp_path = None
    tmp_path = tempfile.mkdtemp(dir=insiderer.TMP_DIR)
    odtzip.extractall(tmp_path)
    for name in odtzip.namelist():
      childpath = tmp_path + "/" + name
      try:
        #print(childpath, name)
        if name == "meta.xml":
          metaxml = etree.parse(childpath)
          metadatas = metaxml.xpath('/*/*/*')
          for item in metadatas:
            key = item.xpath('local-name()')
            if from_doc is True and key == "generator":
              pass
            else:
              metadata[key] = item.text
        elif name == "content.xml":
          metaxml = etree.parse(childpath)
          trackchanges = metaxml.xpath('//*[local-name() = "change-info"]')
          if len(trackchanges) > 0:
            metadata['track_changes'] = []
            for trackchange in trackchanges:
              trackchange_dict = {}
              for item in trackchange.xpath('*'):
                trackchange_dict[item.xpath('local-name()')] = item.text
              metadata['track_changes'].append(trackchange_dict)
        elif os.path.isdir(childpath):
          pass
        elif name == "mimetype" or name == "manifest.rdf" or name == "META-INF/manifest.xml" or name == "current.xml" or name == "styles.xml" or name == "settings.xml" or name == "" or name == "Configurations2/accelerator/current.xml" or name == "layout-cache":
          pass
        elif from_doc is True and name == "Thumbnails/thumbnail.png":
          pass
        else:
          child = insiderer.get_metadata(childpath, name)
          if child["mimetype"]:
          children.append(child)
      finally:
        if not os.path.isdir(childpath):
          insiderer.safedelete(childpath)
  finally:
    if tmp_path:
      shutil.rmtree(tmp_path)
