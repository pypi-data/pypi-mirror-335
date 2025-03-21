import requests
import json

def upload_image(path, client_id, use_face_enhance=False, use_large_model=True, use_repair_mode=False):
    # URL to the PHP script
    url = "https://image-upscaling.net/imageupscaling/upload.php"

    data = {}
    if use_face_enhance:
        data["fx"] = ""
    if use_large_model:
        data["lm"] = ""
    if use_repair_mode:
        data["rm"] = ""

    # Cookie with a valid 32-digit hexadecimal client_id
    cookies = {
        "client_id": client_id
    }

    files = {
        "image": open(path, "rb")
    }

    headers = {
        "Origin": "https://image-upscaling.net"
    }

    response = requests.post(url, data=data, files=files, cookies=cookies, headers=headers)

    return response.text


def get_uploaded_images(client_id):

  # URL to the PHP script
  url = "https://image-upscaling.net/imageupscaling/get_images_client.php"

  # Cookie with a valid 32-digit hexadecimal client_id
  cookies = {
      "client_id": client_id
  }


  # Send the POST request
  response = requests.get(url, cookies=cookies)

  # Print the response from the server
  data = json.loads(response.text)

  # Access the arrays (lists)
  waiting = ["https://image-upscaling.net/imageupscaling/"+i for i in data["images1"]]
  completed = ["https://image-upscaling.net/imageupscaling/"+i for i in data["images2"]]
  in_progress = ["https://image-upscaling.net/imageupscaling/"+i for i in data["images3"]]

  return waiting, completed, in_progress
  
  