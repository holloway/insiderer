from wand.image import Image

def image(path, metadata, children):
    try:
      with Image(filename=path) as i:
          for key, value in i.metadata.items():
          	metadata[key.strip()] = value;
    except Exception as e:
       print("Error parsing image", e)
       pass
