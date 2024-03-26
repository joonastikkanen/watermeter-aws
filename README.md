# watermeter-aws

This is simple Python script that analyses watermeter digits using AWS Rekognition service. 

Links:
 * Boto3 docs on detect_text: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition/client/detect_text.html
 * AWS Docs: https://docs.aws.amazon.com/rekognition/latest/APIReference/Welcome.html

 ## Nix Shell development environment

 I use NixOS on my development machine so I use nix-shell to get packages needed. To load dependencies to nix-shell just run **nix-shell** command on root of this directory.

 ## Configurations

 Check config.yaml.example file to get example configs to run this script.