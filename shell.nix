{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11") {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    python311
    python311Packages.boto3
    python311Packages.pyyaml
    python311Packages.pillow
    python311Packages.black
  ];
}