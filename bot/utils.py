
import requests

def compare_images(url):
    
    local_path = "assets/maxresdefault.jpg"
    with open(local_path, "rb") as f:
        local_data = f.read()

    response = requests.get(url)
    url_data = response.content

    if local_data == url_data:
        return True
    else:
        return False