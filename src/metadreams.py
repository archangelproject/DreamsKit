import argparse
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from PIL import Image

VERBOSE = False


def process_png_file(file):
    """
    Extracts metadata and size from a PNG file.
    :param file: The PNG file to process
    :return: A tuple containing the metadata and size of the image
    """
    printVerbose(f"Processing file: {file}...")

    try:
        with Image.open(file) as im:
            metadata = im.info
            size = im.size
    except OSError as e:
        # handle the error and provide a more informative error message
        print(f"Error processing {file}: {e}")
        return None, None

    return metadata, size


def add_single_element(element, key, value):
    """
    Adds a single value subelement (<key>value</key>) in the specified xml tag
    :param element: The xml element where the subelement will be added
    :param key: The key of the subelement
    :param value: The value of the subelement
    """

    subelement = ET.SubElement(element, key.lower())
    subelement.text = value


def add_multi_element(element, key):
    """
    Adds a subelement in the specified xml tag that can contain multiple subelements
    :param element: The xml element where the subelement will be added
    :param key: The key of the subelement
    """

    subelement = ET.SubElement(element, key.lower())

    return subelement


def add_attr_element(element, key, value):
    """
    Adds an attribute to a specified tag (<tag attribute="value">)
    :param element: The xml element where the attribute will be added
    :param key: The key of the attribute
    :param value: The value of the attribute
    """

    element.set(key.lower(), value)


def parse_image_info(value):
    """
    Prepares the json info read from the tag 'image' inside the 'sd-metadata'
    and return the dictionary with the json info
    :param value: The value of the 'image' key
    :return: A dictionary with the json info
    """

    if value == None:
        return None

    # parse the string value of image as JSON. The keys are
    # coded with single quotes, it is required to replace
    # them with double quotes
    value = str(value).replace("'", '"')
    # Required to replace None per null
    value = value.replace("None", "null")

    sd_image = json.loads(value)
    return sd_image


def write_image_info(element, dict_image):
    """
    Writes inside the xml tag 'sd_metadata' the data stored in the json dict image
    :param element: The xml element where the data will be written
    :param dict_image: The dictionary with the image information
    """

    if not dict_image == None:
        # loop through the elements in the image
        for img_key, img_value in dict_image.items():
            # add the value as a text node to the XML element
            add_single_element(element, img_key, str(img_value))


def create_image_element(doc, filename, file_path, metadata, size, ckpt):
    """
    Creates an XML element for an image.
    :param doc: The xml document where the element will be added
    :param filename: The filename of the image
    :param file_path: The file path of the image
    :param metadata: The metadata of the image
    :param size: The size of the image
    :param ckpt: The checkpoint name
    :return: The created xml element
    """

    element = ET.Element("image")
    add_attr_element(element, "filename", filename)

    # add the image filepath
    add_single_element(element, "path", file_path)

    # add the image size
    add_single_element(element, "size", str(size))

    for key, value in metadata.items():
        if key == "sd-metadata":
            # parse the string value of sd-metadata as JSON
            sd_metadata = json.loads(value)

            # create a new element for the sd-metadata
            sd_element = add_multi_element(element, key)

            # add ckpt tag if exists
            if ckpt:
                add_single_element(sd_element, "ckpt", ckpt)

            # loop through the elements in the sd-metadata
            for sd_key, sd_value in sd_metadata.items():
                if sd_key == "image":
                    sd_image = parse_image_info(sd_value)
                    write_image_info(sd_element, sd_image)
                else:
                    # add the value as a text node to the XML element
                    add_single_element(sd_element, sd_key, str(sd_value))

        else:
            # add the value as a text node to the XML element
            add_single_element(element, key, value)

    return element


def create_xml_document(folder, ckpt):
    """
    Creates an XML document containing metadata for all PNG files in a folder.
    :param folder: The folder containing the PNG files.
    :param ckpt: The checkpoint name.
    """

    # create the root element and adds an argument for software and version
    root = ET.Element("metadata")
    add_attr_element(root, "software", f"MetaDreams {__version__}")

    # loop through all the png files in the given directory
    for filename in os.listdir(folder):
        if not filename.endswith(".png"):
            continue

        file_path = os.path.join(folder, filename)
        metadata, size = process_png_file(file_path)

        if metadata is None or size is None:
            continue

        # create an XML element for the image
        element = create_image_element(root, filename, file_path, metadata, size, ckpt)
        root.append(element)

    # create an XML document from the root element
    doc = ET.ElementTree(root)

    # create a pretty string representation of the XML document
    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

    return xml_string


def write_xml_document(folder, filename, ckpt):
    """
    Writes the XML document to a file
    :param root: The root element of the XML document
    :param filename: The name of the file to write the XML document to
    :param ckpt The optional argument to add in the metadata information the ckpt model used to generate the images
    """

    try:
        # Create XML document
        xml_string = create_xml_document(folder, ckpt)

        # Write XML document to file
        output_path = os.path.join(str(folder), str(filename))
        with open(output_path, "w") as f:
            f.write(xml_string)

        printVerbose(f"XML file created: {output_path}")
    except OSError as e:
        # handle the error and provide a more informative error message
        print(f"Error writing XML file {folder}: {type(e)}: {e}")


def extract_dreams(xml_filepath):
    """
    Extracts the "Dream" field from the metadata file and returns an array with the dreams
    :param xml_filepath: The filepath to the xml cotaining the metadata where the dreams are stored
    :return: The list of dreams (prompts)
    """
    dreams = []
    doc = ET.parse(xml_filepath)

    # loop through all the image elements in the document
    for image in doc.iter("image"):
        # find the Dream element
        dream = image.find("Dream")
        if dream is not None:
            # add the text of the Dream element to the list
            dreams.append(dream.text)
            printVerbose(f"Found dream: {dream.text}")

    return dreams


def write_dreams(dreams, output_file, output_generation):
    """
    Writes the list of dreams (prompts) into the specified file
    :param dreams The list of dreams to be written in the file
    :param output_file The filepath of the file to store the dreams
    :param output_generation Optional argument to add the argument -o to the prompts. This argument contains the folder path to be added
    """
    with open(output_file, "w") as f:
        if output_generation:
            printVerbose(f"Output to be added: {output_generation}")
        for dream in dreams:
            if output_generation:
                dream = dream + " -o " + output_generation
            f.write(dream + "\n")


def create_dreams_file(folder, prompt_filename, output_argument, xml_file):
    """
    Creates the file cotaining the dreams (prompts) read in the xml file
    :param folder The folder where the file will be stored
    :param prompt_filename The name of the file with the prompts
    :param output_argument Optional argument, it contains the route to add to the parameter -o of the prompt
    :param xml_file Filepath of the xml to be read in order to get the prompts
    """
    # Check if the file metadata.xml exists in the folder specified in the argument dreams.
    if not os.path.isfile(os.path.join(folder, xml_file)):
        # The xml file has not been generated yet. Generate the xml file
        printVerbose(f"File {xml_file} not found. Generating new file")
        write_xml_document(folder, xml_file, None)

    # Read the xml file and put every dream in the sdp file
    full_xml_filepath = os.path.join(folder, xml_file)
    printVerbose(f"Parsing the file {full_xml_filepath}")

    full_prompts_filename = os.path.join(folder, prompt_filename)
    write_dreams(extract_dreams(full_xml_filepath), full_prompts_filename, output_argument)
    printVerbose(f"Created file: {full_prompts_filename}")


def printVerbose(message):
    """
    Prints a message if verbose flag is true
    :param message: The message to be printed
    """

    if VERBOSE:
        print(message)


__version__ = "v.0.6.1"


def main():
    """
    The main function that coordinates the processing of PNG files,
    and the creation of the XML document.
    """
    parser = argparse.ArgumentParser(description="Process PNG files and generate an XML file with metadata.")
    parser.add_argument("-f", "--file", help="Path to a PNG file")
    parser.add_argument("-F", "--folder",
                        help="Path to a folder. File (metadata.xml) will be created with all the metadata information")
    parser.add_argument("-d", "--dreams",
                        help="Generate a file (prompts.sdp) with the prompts to create the images stored in the xml "
                             "file")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="This option allows the program to access the subfolders of the specified root folder")
    parser.add_argument("-o", "--output", help="Add the argument -o to each prompt stored in the prompts file")
    parser.add_argument("-c", "--ckpt", help="Set manually the ckpt model used to generate the images")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args()

    png_file = args.file
    folder = args.folder
    xml_file = "metadata.xml"
    dreams = args.dreams
    prompts = "prompts.sdp"
    recursive = args.recursive
    output = args.output
    ckpt = args.ckpt
    VERBOSE = args.verbose

    printVerbose("Verbose mode enabled")

    if png_file and folder:
        print("Error: You cannot specify both a file and a folder.")
        return

    if png_file and dreams:
        print("Error: You cannot specify both a file and to generate the dreams file")

    if not png_file and not folder and not dreams:
        parser.error("You must specify either a file or a folder. For more info please use the argument -h or --help")
        return

    if png_file:
        metadata, size = process_png_file(png_file)
        if metadata is None or size is None:
            print(f"Error: Could not extract metadata from {png_file}")
            return

        print("Metadata for PNG file:")
        print("Size: " + str(size))
        print("Metadata: " + str(metadata))

    if folder:
        try:
            if not recursive:
                printVerbose("Selected: Metadata file generation. No recursive.")
                write_xml_document(folder, xml_file, ckpt)
            else:
                printVerbose("Selected: Metadata file generation. Recursive.")
                for root, dirs, files in os.walk(folder):
                    printVerbose(f"Processing folder: {root}")
                    write_xml_document(root, xml_file, ckpt)
        except OSError as e:
            print(f"Error creating the XML information in folder {folder}: {e} ")

    if dreams:
        try:
            if not recursive:
                printVerbose("Selected: Prompts file generation. No recursive.")
                create_dreams_file(dreams, prompts, output, xml_file)
            else:
                printVerbose("Selected: Prompts file generation. Recursive.")
                for root, dirs, files in os.walk(dreams):
                    create_dreams_file(root, prompts, output, xml_file)
        except OSError as e:
            print(f"Error processing the dreams in the folder {dreams}: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
