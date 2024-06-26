import base64
from decimal import Decimal, getcontext

import yaml
import boto3
from PIL import Image


def detect_text(watermeter_image_path, session, rois):
    # Set the precision
    getcontext().prec = 25
    regions_of_interest = []
    with Image.open(watermeter_image_path) as img:
        # Get the width and height
        image_width, image_height = img.size
    for roi in rois:
        # x, y, w, h
        topleft_col, topleft_row, width, height = roi
        width_pos = Decimal(width) / Decimal(image_width)
        height_pos = Decimal(height) / Decimal(image_height)
        left_pos = Decimal(topleft_col) / Decimal(image_width)
        top_pos = Decimal(topleft_row) / Decimal(image_height)
        region = {
            "BoundingBox": {
                "Width": float(width_pos),
                "Height": float(height_pos),
                "Left": float(left_pos),
                "Top": float(top_pos),
            }
        }
        regions_of_interest.append(region)
    print("Regions of interest: " + str(regions_of_interest))
    client = session.client("rekognition")

    # Open the image file in binary mode, encode it to base64
    with open(watermeter_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.detect_text(
        Image={
            "Bytes": base64.b64decode(encoded_image),
        },
        Filters={"RegionsOfInterest": regions_of_interest},
    )

    text_detections = response["TextDetections"]
    # Filter out the detections that are not digits and confidence is more than 90
    digit_detections = [
        d["DetectedText"]
        for d in text_detections
        if d["DetectedText"].isdigit() and d["Confidence"] > 0 and d["Type"] == "WORD"
    ]

    digits = ""

    for digit in digit_detections:
        digits += str(digit)

    return digits


def main():
    # LOAD CONFIG FILE
    def load_config():
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config

    config = load_config()
    prerois = config["prerois"] = [tuple(roi) for roi in config["prerois"]]
    postrois = config["postrois"] = [tuple(roi) for roi in config["postrois"]]
    aws_profile = config["aws_profile"]
    aws_region = config["aws_region"]
    watermeter_image_path = config["watermeter_image_path"]
    # Create a session using your AWS credentials from environment variables
    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    watermeter_image_path = watermeter_image_path

    preroisdigits = str(detect_text(watermeter_image_path, session, prerois))
    print(f"pre_digits: ", preroisdigits)

    postroisdigits = str(detect_text(watermeter_image_path, session, postrois))
    print(f"postroi_digits: ", postroisdigits)

    total_digits = preroisdigits + "." + postroisdigits
    print(f"total_digits: ", total_digits)


if __name__ == "__main__":
    main()
