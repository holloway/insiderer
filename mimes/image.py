from wand.image import Image

def image(path, metadata, children):
    try:
      with Image(filename=path) as i:
          for key, value in i.metadata.items():
          	metadata[key.strip()] = value;
          metadata["_GENERATOR"] = "WARNING: Dates may be erroneous, especially if date is a few moments ago. Manual inspection may be required."
    except Exception as e:
       print("Error parsing image", e)
       pass
