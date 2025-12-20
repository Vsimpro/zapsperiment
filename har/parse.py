import json


def contents_from_json( json_object : json ) -> list:
    """
    TODO: docstrings :)
    """
    
    objects : list[dict] = []
    
    for entry in json_object["log"]["entries"]:
        status = entry["response"]["status"]
        
        # If status is 0, skip this entry.    
        if status == 0:
            continue
        
        # Parse relevant information from the entry.
        encoding = None
        url      = entry["request"]["url"]
        text     = entry["response"]["content"]["text"]
        
        # Check if data is encoded. None, if not.
        if "encoding" in entry["response"]["content"]:
            encoding = entry["response"]["content"]["encoding"]
        
        # Store to a list
        objects.append({ "url" : url, "status" : status, "text" : text, "encoding" : encoding })
        
    return objects
