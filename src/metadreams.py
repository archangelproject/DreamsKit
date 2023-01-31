import argparse
import json
import os
import traceback
import xml.etree.ElementTree as eltree
from xml.dom import minidom

from PIL import Image

# Global variables

__version__ = "v.1.0"

VERBOSE: bool = False

MESSAGE_INFO: int = 2
MESSAGE_FATAL_ERROR: int = 1
MESSAGE_WARNING: int = 0

KEY_FOLDER: str = 'folder'
KEY_FOLDER_NAME: str = 'name'
KEY_FOLDER_PATH: str = 'path'
KEY_IMAGE: str = 'image'
KEY_IMAGE_PATH: str = 'path'
KEY_CKPT: str = 'ckpt'
KEY_DREAM: str = 'dream'

FILE_METADATA = 'metadata.xml'
FILE_PROMPTS = 'prompts.sdp'


def process_png_file(file):
    """
    Extracts metadata and size from a PNG file.
    :param file: The PNG file to process
    :return: A tuple containing the metadata and size of the image
    """
    print_verbose(f"Processing file: {file}...")

    try:
        with Image.open(file) as im:
            metadata = im.info
            size = im.size
    except OSError as exception:
        # handle the error and provide a more informative error message
        print(f"Error processing {file}: {exception}")
        return None, None

    return metadata, size


def add_single_element(element, key, value):
    """
    Adds a single value sub-element (<key>value</key>) in the specified xml tag
    :param element: The xml element where the sub-element will be added
    :param key: The key of the sub-element
    :param value: The value of the sub-element
    """

    subelement = eltree.SubElement(element, key.lower())
    subelement.text = value


def add_multi_element(element, key):
    """
    Adds a subelement in the specified xml tag that can contain multiple sub-elements
    :param element: The xml element where the sub-element will be added
    :param key: The key of the sub-element
    """

    subelement = eltree.SubElement(element, key.lower())

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

    if value is None:
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

    if dict_image is not None:
        # loop through the elements in the image
        for img_key, img_value in dict_image.items():
            # add the value as a text node to the XML element
            add_single_element(element, img_key, str(img_value))


def create_image_element(file_path, metadata, size, ckpt):
    """
    Creates an XML element for an image.
    :param file_path: The file path of the image
    :param metadata: The metadata of the image
    :param size: The size of the image
    :param ckpt: The checkpoint name
    :return: The created xml element
    """

    element = eltree.Element("image")
    add_attr_element(element, "filename", os.path.basename(file_path))

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
                add_single_element(sd_element, KEY_CKPT, ckpt)

            # loop through the elements in the sd-metadata
            for sd_key, sd_value in sd_metadata.items():
                if sd_key == KEY_IMAGE:
                    sd_image = parse_image_info(sd_value)
                    write_image_info(sd_element, sd_image)
                else:
                    # add the value as a text node to the XML element
                    add_single_element(sd_element, sd_key, str(sd_value))

        else:
            # add the value as a text node to the XML element
            add_single_element(element, key, value)

    return element


def create_folder_element(xml_element, folder, recursive, ckpt):
    """
    Creates a xml element for the folder that contains the information of the images in that folder
    :param xml_element The xml element to add the information of the specified folder
    :param folder The folder containing the PNG files
    :param recursive Parameter that enables the retrieval of information from the sub-folders
    :param ckpt The checkpoint name.
    """

    folder_element = add_multi_element(xml_element, KEY_FOLDER)
    add_attr_element(folder_element, KEY_FOLDER_NAME, os.path.basename(folder))
    add_attr_element(folder_element, KEY_FOLDER_PATH, folder)
    # loop through all the files in the given directory
    for filename in os.listdir(folder):
        if not is_folder_empty(folder):
            filename = os.path.join(folder, filename)
            if os.path.isdir(filename) and recursive:
                print_verbose(f"Processing folder: {filename} ...")
                create_folder_element(folder_element, filename, recursive, ckpt)

            elif os.path.isfile(filename) and filename.endswith(".png"):
                metadata, size = process_png_file(filename)

                if metadata is None or size is None:
                    continue

                # create an XML element for the image
                element = create_image_element(filename, metadata, size, ckpt)
                folder_element.append(element)
        else:
            print_verbose(f"Folder {folder} is empty. Ignored")

    return folder_element


def is_folder_empty(folder):
    """
    Checks if the folder is empty
    :param folder The folder to be checked
    :return: True if the folder is empty. Otherwise, False
    """
    return len(os.listdir(folder)) == 0


def check_metadata_file_overwrite(folder):
    """
    Checks if the metadata file exists in the folder. If it exists, asks for permission to overwrite it
    :param folder The folder where it is checked if the metadata file exists
    :return: True if the metadata file does not exist or it can be overwritten. False if the metadata file exists and
    cannot be overwritten.
    """
    if os.path.exists(os.path.join(folder, FILE_METADATA)):
        response = input(f"File {FILE_METADATA} already exists, do you want to overwrite it? (yes/no): ")
        if response.lower() == "yes" or response.lower() == "y":
            # File exists and user allows to overwrite it, green light for generating new one
            print_verbose(f"{FILE_METADATA} exists. Authorized to overwrite")
            return True
        else:
            # File exists but user selects not to overwrite it, red light for generating new one
            print_verbose(f"{FILE_METADATA} exists. NOT authorized to overwrite")
            return False
    else:
        # File doesn't exist, green light for generating file
        print_verbose(f"{FILE_METADATA} doesn't exist. Proceeding to generate it")
        return True


def create_xml_document(folder, recursive, ckpt):
    """
    Creates an XML document containing metadata for all PNG files in a folder
    :param folder The folder containing the PNG files
    :param recursive Parameter that enables the retrieval of information from the sub-folders
    :param ckpt The checkpoint name.
    :return: The string that contains all the xml information
    """

    # create the root element and adds an argument for software and version
    root = eltree.Element("metadata")
    add_attr_element(root, "software", f"MetaDreams {__version__}")

    create_folder_element(root, folder, recursive, ckpt)

    # create a pretty string representation of the XML document
    xml_string = minidom.parseString(eltree.tostring(root)).toprettyxml(indent="  ")

    return xml_string


def write_xml_document(folder, filename, recursive, ckpt):
    """
    Writes the XML document to a file
    :param folder: The root element of the XML document
    :param filename: The name of the file to write the XML document to
    :param recursive Parameter that enables the recursive generation of metadata inside the subfolders
    :param ckpt The optional argument to add in the metadata information the ckpt model used to generate the images
    """

    try:
        # Create XML document
        xml_string = create_xml_document(folder, recursive, ckpt)

        # Write XML document to file
        output_path = os.path.join(str(folder), str(filename))
        with open(output_path, "w") as f:
            f.write(xml_string)

        print_verbose(f"XML file created: {output_path}")
    except OSError as exception:
        # handle the error and provide a more informative error message
        print(f"Error writing XML file {folder}: {type(exception)}: {exception}")


def write_dreams(dreams, output_file, output_generation):
    """
    Writes the list of dreams (prompts) into the specified file
    :param dreams The list of dreams to be written in the file
    :param output_file The filepath of the file to store the dreams
    :param output_generation Optional argument to add the argument -o to the prompts. This argument contains the "
    "folder path to be added
    """
    with open(output_file, "w") as f:
        if output_generation:
            print_verbose(f"Output to be added: {output_generation}")
        for dream in dreams:
            f.write(dream + "\n")


def parse_metadata_xml_file(xml_file):
    """
    Parses the metadata.xml file
    :param xml_file The file path to the xml file
    :return: The document containing all the info in the metadata file
    """
    print_verbose(f"Parsing the file {xml_file}")
    return eltree.parse(xml_file)


def get_all_prompts(xml_document, output):
    """
    Navigates the xml document and extracts all the prompts found
    :param xml_document The xml document containing the metadata information
    :param output Enables the adding of the -o parameter into the prompt
    :return: An array containing the prompts
    """
    dreams = []
    # loop through all the image elements in the document
    for image in xml_document.iter(KEY_IMAGE):
        # find the Dream element
        dream = image.find(KEY_DREAM)
        if dream is not None:
            # add the text of the Dream element to the list
            prompt = dream.text
            if output:
                img_path = image.find(KEY_IMAGE_PATH).text
                img_path = os.path.dirname(img_path)
                prompt = " -o ".join([prompt, img_path])
            dreams.append(prompt)
            print_verbose(f"Found dream: {prompt}")

    return dreams


def create_dreams_file(folder, prompt_filename, xml_file, output_argument):
    """
    Creates the file containing the dreams (prompts) read in the xml file
    :param folder The folder where the file will be stored
    :param prompt_filename The name of the file with the prompts
    :param xml_file Filepath of the xml to be read in order to get the prompts
    :param output_argument Optional argument, it contains the route to add to the parameter -o of the prompt
    """

    xml_path = os.path.join(folder, xml_file)
    prompts_filepath = os.path.join(folder, prompt_filename)

    # Read the xml file and put every dream in the sdp file
    write_dreams(get_all_prompts(parse_metadata_xml_file(xml_path), output_argument), prompts_filepath,
                 output_argument)


def print_verbose(message):
    """
    Prints a message if verbose flag is true
    :param message: The message to be printed
    """

    if VERBOSE:
        message = " ".join(['VERBOSE:', message])
        print(message)


def print_message(message, type_message):
    if type_message == MESSAGE_WARNING:
        message = " ".join(['WARNING:', message])
    elif type_message == MESSAGE_FATAL_ERROR:
        message = " ".join(['ERROR:', message])
    elif type_message == MESSAGE_INFO:
        message = " ".join(['INFO:', message])

    print(message)

    if type_message == MESSAGE_FATAL_ERROR:
        exit(MESSAGE_FATAL_ERROR)


def main():
    """
    The main function that coordinates the processing of PNG files,
    and the creation of the XML document.
    """
    parser = argparse.ArgumentParser(description="Process PNG files and generate an XML file with metadata.")

    # -f --file
    parser.add_argument("-f", "--file", help="Path to a PNG file or a folder. If a file is selected, the metadata info"
                                             "of the file is shown in screen. If a folder is selected, the file "
                                             "metadata.xml will be created with all the metadata information.")

    # -d --dreams
    parser.add_argument("-d", "--dreams", action="store_true",
                        help="Generate a file (prompts.sdp) with the prompts to create the images stored in the xml "
                             "file")

    # -r --recursive
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="This option allows the program to access the subfolders of the specified root folder")

    # -o --output
    parser.add_argument("-o", "--output", action="store_true", help="Adds the parameter -o to the prompt in order to "
                        "be generated in the same folder that is specified in the xml file")

    # -c --ckpt
    parser.add_argument("-c", "--ckpt", help="Set manually the ckpt model used to generate the images")

    # -v --verbose
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # --version
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args()

    file = args.file
    xml_file = "metadata.xml"
    dreams = args.dreams
    prompts = "prompts.sdp"
    recursive = args.recursive
    output = args.output
    ckpt = args.ckpt

    global VERBOSE
    VERBOSE = args.verbose

    print_verbose("Verbose mode enabled")

    if not file:
        parser.error("You must specify either a file or a folder. For more info please use the argument -h or --help")
        return

    if file:
        ###
        # FILE PROCESSING
        ###
        if os.path.isfile(file):
            metadata, size = process_png_file(file)
            if metadata is None or size is None:
                print_message(f"Could not extract metadata from {file}", MESSAGE_FATAL_ERROR)
                return

            print_message("Metadata for PNG file:", MESSAGE_INFO)
            print_message("Size: " + str(size), MESSAGE_INFO)
            print_message("Metadata: " + str(metadata), MESSAGE_INFO)
        ###
        # FOLDER PROCESSING
        ###
        elif os.path.isdir(file):
            try:
                if check_metadata_file_overwrite(file):
                    folder = file
                    print_verbose(f"Selected Folder generation. Recursive: {recursive}")
                    write_xml_document(folder, xml_file, recursive, ckpt)

            except OSError as exception:
                print_message(f"Error creating the XML information in folder {file}: {exception} ", MESSAGE_FATAL_ERROR)
        else:
            print_message(f"The file {file} is not a file or a folder", MESSAGE_WARNING)

    if dreams:
        try:
            print_verbose(f"Selected: Prompts file generation. Recursive: {recursive}")
            create_dreams_file(file, prompts, xml_file, output)
        except OSError as exception:
            print_message(f"Error processing the dreams in the folder {dreams}: {exception}", MESSAGE_FATAL_ERROR)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # print_message(str(e), MESSAGE_FATAL_ERROR)
        trace = traceback.format_exc()
        print_message("\n\n".join([trace, str(e)]), MESSAGE_FATAL_ERROR)
