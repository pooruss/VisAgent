import io
from PIL import Image
import base64

def img_to_base64(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_byte = buffered.getvalue()
    base64_string = base64.b64encode((img_byte)).decode('utf-8')
    return base64_string

def base64_to_image(base64_string: str):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image