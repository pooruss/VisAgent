import base64
import os
import appdirs
import random
import string

from html2image import Html2Image


# Using appdirs to determine user-specific config path
config_dir = appdirs.user_config_dir("Open Interpreter")

def get_storage_path(subdirectory=None):
    if subdirectory is None:
        return config_dir
    else:
        return os.path.join(config_dir, subdirectory)


def html_to_png_base64(code):
    # Convert the HTML into an image using html2image
    hti = Html2Image()

    # Generate a random filename for the temporary image
    temp_filename = "".join(random.choices(string.digits, k=10)) + ".png"
    hti.output_path = get_storage_path()
    hti.screenshot(
        html_str=code,
        save_as=temp_filename,
        size=(960, 540),
    )

    # Get the full path of the temporary image file
    file_location = os.path.join(get_storage_path(), temp_filename)

    # Convert the image to base64
    with open(file_location, "rb") as image_file:
        screenshot_base64 = base64.b64encode(image_file.read()).decode()

    # Delete the temporary image file
    os.remove(file_location)

    return screenshot_base64
