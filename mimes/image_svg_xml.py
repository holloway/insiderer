from lxml import etree
import base64
import os
import sys
import tempfile
try:
  parent_directory = os.path.dirname(os.path.dirname(__file__))
  sys.path.insert(0, parent_directory)
  import insiderer
except ImportError as e:
  print(e)
  pass

svg_namespace      = "http://www.w3.org/2000/svg"
xlink_namespace    = "http://www.w3.org/1999/xlink"
inkscape_namespace = "http://www.inkscape.org/namespaces/inkscape"
sodipodi_namespace = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"

namespaces = {"svg": svg_namespace, "xlink": xlink_namespace, "sodipodi":sodipodi_namespace, "inkscape":inkscape_namespace}
base64_prefix = "base64,"

def image_svg_xml(path, metadata, children):
  svg = etree.parse(path)
  fields = {
    'export-filename': '//@inkscape:export-filename',
    'docname':         '@sodipodi:docname'
  }
  for key in fields.keys():
    result = svg.xpath(fields[key], namespaces=namespaces)
    if len(result) > 1:
      metadata[key] = result
    elif len(result) > 0:
      metadata[key] = result[0]
  base64images = svg.xpath('//svg:image', namespaces=namespaces)
  for image in base64images:
    key = image.xpath('local-name()')
    href = image.attrib.get('{%s}href' % xlink_namespace)
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

