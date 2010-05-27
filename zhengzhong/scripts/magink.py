#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#


from __future__ import with_statement
import hashlib
import logging
import os
import sys
from optparse import OptionParser
from PIL import Image


_MAGINK_VERSION = "magink version 1.0, by ZHENG Zhong"
_MAGINK_ID = "MAGINK1"


def _read_binary_file(file_name):
    """
    Reads a binary file and returns a byte array as a str.
    """
    with open(file_name, "rb") as file:
        bytes = file.read()
    return bytes


def _save_binary_file(file_name, bytes):
    """
    Writes a byte array as a str to a binary file.
    """
    with open(file_name, "wb") as file:
        file.write(bytes)
        file.flush()


def _prepend_header(bytes):
    """
    Prepends header string to the bytes.
    """
    md5 = hashlib.md5(bytes).hexdigest().upper()
    header = "%s/%s/%d/" % (_MAGINK_ID, md5, len(bytes))
    logging.info("Prepending header: %s" % header)
    return header + bytes


def _check_header(bytes):
    """
    Extracts header string from the input bytes, and checks the header.
    """
    try:
        magink_id, md5, length, bytes = bytes.split("/", 3)
        if magink_id != _MAGINK_ID:
            raise Exception("inconsistent Magink ID: %s" % magink_id)
        elif not length.isdigit():
            raise Exception("bad length format: %s" % length)
        bytes = bytes[:int(length)]
        if md5 != hashlib.md5(bytes).hexdigest().upper():
            raise Exception("inconsistent MD5: %s" % md5)
        logging.info("Extracting: %s/%s/%s/..." % (magink_id, md5, length))
        return bytes
    except Exception, exc:
        logging.error("Failed to check header in bytes: %s" % exc)
        return None


def _get_color_mapping(channels):
    channels = filter(lambda c: c in "RGB", channels.upper())
    mapping = []
    for c in channels:
        mapping.append("RGB".index(c))
    return mapping or [0, 1, 2]


def _encrypt_rgb(bytes, mask_file_name, channels):
    """
    Encrypts bytes into color channels of the mask image file.
    """
    # Convert the channels string to color mapping.
    color_mapping = _get_color_mapping(channels)
    # Check the size of the mask image file.
    mask_image = Image.open(mask_file_name)
    width, height = mask_image.size
    if width * height * len(color_mapping) < len(bytes):
        raise Exception("Mask image is too small for %d bytes." % len(bytes))
    logging.info("Encrypting %d bytes to mask image %s..." % (len(bytes), mask_file_name))
    # Create the target image.
    target_image = Image.new("RGB", (width, height))
    # Encrypt the data into the specified channels.
    mask_pixels = mask_image.load()
    target_pixels = target_image.load()
    for y in range(0, height):
        for x in range(0, width):
            rgb = list(mask_pixels[x, y])
            for i in range(0, len(color_mapping)):
                pos = y * width * len(color_mapping) + x * len(color_mapping) + i
                if pos < len(bytes):
                    rgb[color_mapping[i]] ^= ord(bytes[pos])
            target_pixels[x, y] = tuple(rgb)
    # Return the encrypted image.
    return target_image


def _decrypt_rgb(image, mask_file_name, channels):
    """
    Decrypts bytes from color channels of the image file.
    """
    # Convert the channels string to color mapping.
    color_mapping = _get_color_mapping(channels)
    # Check the size of the mask image file.
    mask_image = Image.open(mask_file_name)
    if image.size != mask_image.size:
        raise Exception("Size of mask image is inconsistent, should be %dx%d." % image.size)
    
    bytes = []
    width, height = image.size
    mask_pixels = mask_image.load()
    pixels = image.load()
    for y in range(0, height):
        for x in range(0, width):
            mask_rgb = mask_pixels[x, y]
            rgb = pixels[x, y]
            for index in color_mapping:
                byte_ord = mask_rgb[index] ^ rgb[index]
                bytes.append(chr(byte_ord))
    logging.info("Decrypting the %dx%d image to %d bytes..." % (width, height, len(bytes)))
    return "".join(bytes)


def _create_option_parser():
    """
    Creates an option parser to parse command-line arguments.
    """
    parser = OptionParser(usage="""%prog <INPUT_FILE_NAME>
    Use -h or --help for help.""")
    parser.add_option(
        "-v", "--version",
        dest="version",
        default=False,
        action="store_true",
        help="print magink version and exit"
    )
    parser.add_option(
        "-m", "--mask",
        dest="mask",
        metavar="MASK_FILE",
        help="specify the mask image file"
    )
    parser.add_option(
        "-c", "--channels",
        dest="channels",
        default="RGB",
        metavar="RGB",
        help="specify the encryption channels, defaults to RGB"
    )
    parser.add_option(
        "-d", "--decrypt",
        dest="decrypt",
        default=False,
        action="store_true",
        help="specify whether to decrypt the file, defaults to encrypt"
    )
    parser.add_option(
        "-o", "--output",
        dest="output",
        metavar="OUTPUT_FILE",
        help="specify the output file (required)"
    )
    return parser


def main(argv=None):
    """
    Main entry point.
    """

    # Get command line arguments as necessary.
    if argv is None:
        argv = sys.argv[1:]

    # Configure logging, set logging level to INFO.
    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(logging.DEBUG)

    # Parse command-line arguments to opts and args.
    parser = _create_option_parser()
    (opts, args) = parser.parse_args(argv)
    
    # If the version info is requested, print version info and exit.
    if opts.version:
        logging.info(_MAGINK_VERSION)
        exit()
    
    # Check opts and args.
    if not opts.mask:
        parser.error("The mask image file (-m or --mask) is required.")
    elif not opts.output:
        parser.error("The output file name (-o or --output) is required.")
    elif not args:
        parser.error("The input file name argument is required.")
    elif len(args) > 1:
        parser.error("Too many input file name arguments.")
    
    input_file_name = args[0]
    output_file_name = opts.output
    mask_file_name = opts.mask
    channels = opts.channels
    
    if opts.decrypt:
        try:
            if not input_file_name.lower().endswith(".png"):
                raise Exception("The file to decrypt should be a PNG file.")
            image = Image.open(input_file_name)
            bytes = _decrypt_rgb(image, mask_file_name, channels)
            bytes = _check_header(bytes)
            _save_binary_file(output_file_name, bytes)
            logging.info("Decrypted %s -> %s" % (input_file_name, output_file_name))
        except Exception, exc:
            logging.error("Failed to decrypt file: %s" % exc)
    else:
        try:
            bytes = _read_binary_file(input_file_name)
            bytes = _prepend_header(bytes)
            image = _encrypt_rgb(bytes, mask_file_name, channels)
            if not output_file_name.lower().endswith(".png"):
                output_file_name += ".png"
            image.save(output_file_name, "PNG")
            logging.info("Encrypted %s -> %s" % (input_file_name, output_file_name))
        except Exception, exc:
            logging.error("Failed to encrypt file: %s" % exc)


if __name__ == "__main__":
    main()


# EOF
