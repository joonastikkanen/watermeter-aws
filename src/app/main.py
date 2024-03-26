import boto3
import base64
import yaml
from PIL import Image
from decimal import Decimal, getcontext

def detect_text(watermeter_image_path, session, rois):
    # Set the precision
    getcontext().prec = 17
    regions_of_interest = []
    with Image.open(watermeter_image_path) as img:
        # Get the width and height
        image_width, image_height = img.size
    for roi in rois:
        left, top , width, height = roi
        width_pos = Decimal(width) / Decimal(image_width)
        print(f"width_pos: ", width_pos)
        height_pos = Decimal(height) / Decimal(image_height)
        print(f"height_pos: ", height_pos)
        left_pos = Decimal(left) / Decimal(image_width)
        print(f"left_pos: ", left_pos)
        top_pos = Decimal(top) / Decimal(image_height)
        print(f"top_pos: ", top_pos)
        region = {
            'BoundingBox': {
                'Width': float(width_pos),
                'Height': float(height_pos),
                'Left': float(left_pos),
                'Top': float(top_pos)
            }
        }
        regions_of_interest.append(region)
    print('Regions of interest: ' + str(regions_of_interest))
    client = session.client('rekognition')

    # Open the image file in binary mode, encode it to base64
    with open(watermeter_image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    response = client.detect_text(
        Image={
            'Bytes': base64.b64decode(encoded_image),
        },
        Filters={
            'RegionsOfInterest': regions_of_interest
        }
    )

    text_detections = response['TextDetections']
    # Filter out the detections that are not digits
    digit_detections = [d['DetectedText'] for d in text_detections if d['DetectedText'].isdigit()]

    return digit_detections

def main():
    # LOAD CONFIG FILE
    def load_config():
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config
    config = load_config()
    prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
    pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
    postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
    postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
    aws_profile = config['aws_profile']
    aws_region = config['aws_region']
    watermeter_image_path = config['watermeter_image_path']
    # Create a session using your AWS credentials from environment variables
    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    watermeter_image_path = watermeter_image_path
    
    preroisdigits = str(detect_text(watermeter_image_path, session, prerois))
    pregaugeroisdigits = str(detect_text(watermeter_image_path, session, pregaugerois))
    pre_digits = preroisdigits + pregaugeroisdigits
    print(f"pre_digits: ", pre_digits)

    postroisdigits = str(detect_text(watermeter_image_path, session, postrois))
    postgaugeroisdigits = str(detect_text(watermeter_image_path, session, postgaugerois))
    post_digits = postroisdigits + postgaugeroisdigits
    print(f"postroi_digits: ", post_digits)

    total_digits = pre_digits + "." + post_digits
    print(f"total_digits: ", total_digits)

if __name__ == "__main__":
    main()