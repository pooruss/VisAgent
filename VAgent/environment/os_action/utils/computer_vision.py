import io

from PIL import Image

try:
    import cv2
    import numpy as np
except:
    # Optional packages
    pass

try:
    from pytesseract import Output, pytesseract
except:
    # this is very very optional, we don't even reccomend it unless the api has failed
    pass

def easyocr_get_text(img):
    # 导入easyocr
    import easyocr
    # 创建reader对象
    reader = easyocr.Reader(['ch_sim','en']) 
    # 读取图像
    result = reader.readtext(img)
    # 结果
    result_str = ""
    for i in result:
        word = i[1]
        result_str += f"\n{word}"
    return result_str

def surya_get_text(img):
    from PIL import Image
    from surya.detection import batch_inference
    from surya.model.segformer import load_model, load_processor

    model, processor = load_model(), load_processor()

    # predictions is a list of dicts, one per image
    predictions = batch_inference([img], model, processor)
    return predictions[0]

def pytesseract_get_text(img):
    # Convert PIL Image to NumPy array
    img_array = np.array(img)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to get the text from the image
    text = pytesseract.image_to_string(gray)

    return text


def find_text_in_image(img, text):
    # Convert PIL Image to NumPy array
    img_array = np.array(img)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to get the data from the image
    d = pytesseract.image_to_data(gray, output_type=Output.DICT)

    # Initialize an empty list to store the centers of the bounding boxes
    centers = []

    # Get the number of detected boxes
    n_boxes = len(d["level"])

    # Create a copy of the grayscale image to draw on
    img_draw = np.array(gray.copy())

    # Convert the img_draw grayscale image to RGB
    img_draw = cv2.cvtColor(img_draw, cv2.COLOR_GRAY2RGB)

    id = 0
    # Loop through each box
    for i in range(n_boxes):
        # Print the text of the box
        # If the text in the box matches the given text
        if text.lower() in d["text"][i].lower():
            # Find the start index of the matching text in the box
            start_index = d["text"][i].lower().find(text.lower())
            # Calculate the percentage of the box width that the start of the matching text represents
            start_percentage = start_index / len(d["text"][i])
            # Move the left edge of the box to the right by this percentage of the box width
            d["left"][i] = d["left"][i] + int(d["width"][i] * start_percentage)

            # Calculate the width of the matching text relative to the entire text in the box
            text_width_percentage = len(text) / len(d["text"][i])
            # Adjust the width of the box to match the width of the matching text
            d["width"][i] = int(d["width"][i] * text_width_percentage)

            # Calculate the center of the bounding box
            center = (
                d["left"][i] + d["width"][i] / 2,
                d["top"][i] + d["height"][i] / 2,
            )

            # Add the center to the list
            centers.append(center)

            # Draw the bounding box on the image in red and make it slightly larger
            larger = 10
            cv2.rectangle(
                img_draw,
                (d["left"][i] - larger, d["top"][i] - larger),
                (
                    d["left"][i] + d["width"][i] + larger,
                    d["top"][i] + d["height"][i] + larger,
                ),
                (255, 0, 0),
                7,
            )

            # Create a small black square background for the ID
            cv2.rectangle(
                img_draw,
                (
                    d["left"][i] + d["width"][i] // 2 - larger * 2,
                    d["top"][i] + d["height"][i] // 2 - larger * 2,
                ),
                (
                    d["left"][i] + d["width"][i] // 2 + larger * 2,
                    d["top"][i] + d["height"][i] // 2 + larger * 2,
                ),
                (0, 0, 0),
                -1,
            )

            # Put the ID in the center of the bounding box in red
            cv2.putText(
                img_draw,
                str(id),
                (
                    d["left"][i] + d["width"][i] // 2 - larger,
                    d["top"][i] + d["height"][i] // 2 + larger,
                ),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (255, 155, 155),
                4,
            )

            # Increment id
            id += 1

    if not centers:
        word_centers = []
        for word in text.split():
            for i in range(n_boxes):
                if word.lower() in d["text"][i].lower():
                    center = (
                        d["left"][i] + d["width"][i] / 2,
                        d["top"][i] + d["height"][i] / 2,
                    )
                    center = (center[0] / 2, center[1] / 2)
                    word_centers.append(center)

        for center1 in word_centers:
            for center2 in word_centers:
                if (
                    center1 != center2
                    and (
                        (center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2
                    )
                    ** 0.5
                    <= 400
                ):
                    centers.append(
                        ((center1[0] + center2[0]) / 2, (center1[1] + center2[1]) / 2)
                    )
                    break
            if centers:
                break

    bounding_box_image = Image.fromarray(img_draw)
    bounding_box_image.format = img.format

    # Convert centers to relative
    img_width, img_height = img.size
    centers = [(x / img_width, y / img_height) for x, y in centers]

    # Debug by showing bounding boxes:
    bounding_box_image.show()

    return centers
