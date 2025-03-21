# image-upscaling.net API Client

A simple Python package to interact with the free [image-upscaling.net](https://image-upscaling.net/) API. This client provides two key functions for uploading images for processing and querying their processing status.

## Features

- **Upload Images**: Send images to the upscaling service with 3 enhancement options.
- **Query Status**: Retrieve the processing status of your images, categorized as waiting, completed, or in progress. This will give you the urls to download processed images.

## Installation

Install the package using pip:

```bash
pip install image-upscaling-api
```

## Usage

### Uploading an Image

The `upload_image` function sends an image for upscaling.

Note: The `client_id` must be a 32-digit hexadecimal string of your choice to identify your requests.

```python
from image_upscaling_api import upload_image

# Example usage:
upload_image("r1.png", "481d40602d3f4570487432044df03a52", 
             use_repair_mode=False, 
             use_large_model=True, 
             use_face_enhance=False)
```

#### Parameters:
- `image_path` (str): Path to the image file.
- `client_id` (str): Your 32-digit hexadecimal client ID.
- `use_repair_mode` (bool): Enable to repair image details.
- `use_large_model` (bool): Enable to use a more robust upscaling model.
- `use_face_enhance` (bool): Enable to improve facial features.

### Querying Processing Status

The `get_uploaded_images` function retrieves the status of your uploaded images.

```python
from image_upscaling_api import get_uploaded_images

# Example usage:
waiting, completed, in_progress = get_uploaded_images("481d40602d3f4570487432044df03a52")
```

#### Returns:
- `waiting` (list): Images queued for processing.
- `completed` (list): Images that have been processed.
- `in_progress` (list): Images currently being processed.

## Availability
This project is fully donation-funded. If you find it useful, please consider making a contribution to help cover server costs and ensure its continued availability.

At the moment, the service is free to use, but its future depends on community support. If donations are insufficient to maintain operations, it may not be possible to sustain long-term availability.<br>

[<img src="https://image-upscaling.net/assets/images/pypl_donate.png" width=200>](https://www.paypal.com/donate/?hosted_button_id=FTQ965QDJBUGY)
[<img src="https://image-upscaling.net/assets/images/more_info.png" width=140>](https://image-upscaling.net/imageupscaling/lang/en/donations.html)

Join our Discord for updates, discussions, or support: https://discord.gg/utXujgAT8R

## License

This project is licensed under the MIT License.



## Source code (you can just copy paste)
```Python

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
  
  

```