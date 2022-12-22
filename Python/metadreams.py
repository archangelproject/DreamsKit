import argparse
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from PIL import Image

def process_png_file(file, verbose=False):
    """Extract metadata and size from a PNG file."""
    printVerbose(verbose, f"Processing file: {file}...")

    try:
        with Image.open(file) as im:
            metadata = im.info
            size = im.size
    except OSError as e:
        # handle the error and provide a more informative error message
        print(f"Error processing {file}: {e}")
        return None, None

    return metadata, size

def create_image_element(doc, filename, file_path, metadata, size):
    """Create an XML element for an image."""
    element = ET.Element("image")
    element.set("filename", filename)

    path_element = ET.SubElement(element, "path")
    path_element.text = file_path

    size_element = ET.SubElement(element, "size")
    size_element.text = str(size)

    for key, value in metadata.items():
        if key == "sd-metadata":
            # parse the string value of sd-metadata as JSON
            sd_metadata = json.loads(value)

            # create a new element for the sd-metadata
            sd_element = ET.SubElement(element, key)

            # loop through the elements in the sd-metadata
            for sd_key, sd_value in sd_metadata.items():
                # add the value as a text node to the XML element
                sub_element = ET.SubElement(sd_element, sd_key)
                sub_element.text = str(sd_value)
        else:
            # add the value as a text node to the XML element
            sub_element = ET.SubElement(element, key)
            sub_element.text = value

    return element

def create_xml_document(folder, verbose=False):
    """Create an XML document containing metadata for all PNG files in a folder."""
    # create the root element
    root = ET.Element("metadata")

    # loop through all the png files in the given directory
    for filename in os.listdir(folder):
        if not filename.endswith(".png"):
            continue

        file_path = os.path.join(folder, filename)
        metadata, size = process_png_file(file_path, verbose=verbose)

        if metadata is None or size is None:
            continue

        # create an XML element for the image
        element = create_image_element(root, filename, file_path, metadata, size)
        root.append(element)

    # create an XML document from the root element
    doc = ET.ElementTree(root)

    # create a pretty string representation of the XML document
    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

    return xml_string

def write_xml_document(folder, filename, verbose):
    """Write an XML document to a file."""
    try:
        # Create XML document
        xml_string = create_xml_document(folder, verbose=verbose)
    
        # Write XML document to file
        output_path = os.path.join(str(folder), str(filename))
        with open(output_path, "w") as f:
            f.write(xml_string)
    
        printVerbose(verbose, f"XML file created: {output_path}")
    except OSError as e:
        # handle the error and provide a more informative error message
        print(f"Error writing XML file {folder}: {type(e)}: {e}")


def extract_dreams(xml_filepath, verbose):
    """Extract the "Dream" field from the metadata file and returns an array with the dreams"""
    dreams = []
    doc = ET.parse(xml_filepath)

    # loop through all the image elements in the document
    for image in doc.iter("image"):
        # find the Dream element
        dream = image.find("Dream")
        if dream is not None:
            # add the text of the Dream element to the list
            dreams.append(dream.text)
            printVerbose(verbose, f"Found dream: {dream.text}")

    return dreams

def write_dreams(dreams, output_file, output_generation, verbose):
    # write the dreams to the output file
    with open(output_file, "w") as f:
        if output_generation:
            printVerbose(verbose, f"Output to be added: {output_generation}")
        for dream in dreams:
            if output_generation:
                dream = dream + " -o " + output_generation
            f.write(dream + "\n")

def create_dreams_file(folder, prompt_filename, output_argument, xml_file, verbose):
    #Check if the file metadata.xml exists in the folder specified in the argument dreams.
    if not os.path.isfile(os.path.join(folder, xml_file)):
        #The xml file has not been generated yet. Generate the xml file
        printVerbose(verbose, f"File {xml_file} not found. Generating new file")
        write_xml_document(folder, xml_file, verbose)
        
    #Read the xml file and put every dream in the sdp file
    full_xml_filepath = os.path.join(folder, xml_file)
    printVerbose(verbose, f"Parsing the file {full_xml_filepath}")
    
    full_prompts_filename = os.path.join(folder, prompt_filename)
    write_dreams(extract_dreams(full_xml_filepath, verbose), full_prompts_filename, output_argument, verbose)
    printVerbose(verbose, f"Created file: {full_prompts_filename}")
    
def printVerbose(verbose, message):
    if verbose:
        print(message)

__version__ = "v.0.5.5"

def main():
    parser = argparse.ArgumentParser(description="Process PNG files and generate an XML file with metadata.")
    parser.add_argument("-f", "--file", help="Path to a PNG file")
    parser.add_argument("-F", "--folder", help="Path to a folder. File (metadata.xml) will be created with all the metadata information")
    parser.add_argument("-d", "--dreams", help="Generate a file (prompts.sdp) with the prompts to create the images stored in the xml file")
    parser.add_argument("-r", "--recursive", action="store_true", help="This option allows the program to access the subfolders of the specified root folder")
    parser.add_argument("-o", "--output", help="Add the argument -o to each prompt stored in the prompts file")
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
    verbose = args.verbose
    
    if verbose:
        print("Verbose mode enabled")
        
    if png_file and folder:
        print("Error: You cannot specify both a file and a folder.")
        return
    
    if png_file and dreams:
        print("Error: You cannot specify both a file and to generate the dreams file")
    
    if not png_file and not folder and not dreams:
        print("Error: You must specify either a file or a folder.")
        return
    
    if png_file:
        metadata, size = process_png_file(png_file, verbose=verbose)
        if metadata is None or size is None:
            print(f"Error: Could not extract metadata from {png_file}")
            return

        print("Metadata for PNG file:")
        print("Size: "+str(size))
        print("Metadata: "+str(metadata))
        
    if folder:
        try:
            if not recursive:
                 printVerbose(verbose, "Selected: Metadata file generation. No recursive.")
                 write_xml_document(folder, xml_file, verbose)
            else:
                 printVerbose(verbose, "Selected: Metadata file generation. Recursive.")
                 for root, dirs, files in os.walk(folder):
                     printVerbose(verbose, f"Processing folder: {root}")
                     write_xml_document(root, xml_file, verbose)
        except OSError as e:
            print(f"Error creating the XML information in folder {folder}: {e} ")
            
    if dreams:
        try:
            if not recursive:
                printVerbose(verbose, "Selected: Prompts file generation. No recursive.")
                create_dreams_file(dreams, prompts, output, xml_file, verbose)
            else:
                printVerbose(verbose, "Selected: Prompts file generation. Recursive.")
                for root, dirs, files in os.walk(dreams):
                    create_dreams_file(root, prompts, output, xml_file, verbose)
        except OSError as e:
            print(f"Error processing the dreams in the folder {dreams}: {e}")
         
if __name__ == "__main__":
    main()
