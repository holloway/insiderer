from lxml import etree
import base64
import os
import sys
import tempfile
import re
import xmltodict
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

namespaces = {
  "svg":      "http://www.w3.org/2000/svg",
  "xlink":    "http://www.w3.org/1999/xlink",
  "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
  "inkscape": "http://www.inkscape.org/namespaces/inkscape",
  "rdf":      "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "rdfs":     "http://www.w3.org/2000/01/rdf-schema#",
  "dc":       "http://purl.org/dc/elements/1.1/"
}

base64_prefix = "base64,"

def image_svg_xml(path, metadata, children):
  svg = etree.parse(path)
  fields = {
    'export-filename': '//@inkscape:export-filename',
    'docname':         '//@sodipodi:docname',
    'description':     '//svg:desc',
    'title':           '//svg:title',
    'dca':             '//@*[namespace-uri()="%s"][not(ancestor::dc:*)]' % namespaces["dc"], #because selecting by namespace attributes doesn't seem to work
    'rdf':             '//rdf:*[not(ancestor::rdf:*)]'
  }
  for key in fields.keys():
    results = svg.xpath(fields[key], namespaces=namespaces)

    for result in results:
      key_name = key
      if '*' in fields[key] and len(results) > 0:
        if hasattr(result, "attrname"):
          key_name = re.sub(r'\{.*?\}', '', result.attrname)
        else:
          key_name = result.xpath('name()')

      key_name = insiderer.de_dup(key_name, metadata)

      if isinstance(result, etree._ElementUnicodeResult):
        metadata[key_name] = str(result)
      else:
        metadata[key_name] = xmltodict.parse(etree.tostring(result, encoding='utf8', method='xml').decode('utf-8'))

  base64images = svg.xpath('//svg:image', namespaces=namespaces)
  for image in base64images:
    key = image.xpath('local-name()')
    href = image.attrib.get('{%s}href' % namespaces["xlink"])
    name = image.attrib.get('id') or "unknown"
    if href.startswith("data:") and base64_prefix in href[0:100]:
      image_data = base64.standard_b64decode( href[href.find(base64_prefix) + len(base64_prefix):] )
      try:
        image_path = tempfile.mkstemp(dir=insiderer.TMP_DIR)[1]
        image_handle = open(image_path, "wb")
        image_handle.write(image_data)
        image_handle.close()
        child = insiderer.get_metadata(image_path, name)
        children.append(child)
      finally:
        insiderer.safedelete(image_path)
 

