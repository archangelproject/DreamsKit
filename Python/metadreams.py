import argparse
import json
import os
import xml.dom.minidom

from PIL import Image

def process_png_file(file, verbose):
    with Image.open(file) as im:
        metadata = im.info
        size = im.size

    if verbose:
        print(f"Processing {file}...")

    return metadata, size

def create_xml_document(folder, verbose):
    # create a new XML document
    doc = xml.dom.minidom.Document()

    # create the root element
    root = doc.createElement("metadata")
    doc.appendChild(root)

    # loop through all the png files in the given directory
    for filename in os.listdir(folder):
        if not filename.endswith(".png"):
            continue

        file_path = os.path.join(folder, filename)
        metadata, size = process_png_file(file_path, verbose)

        # create a new element for the image
        element = doc.createElement("image")
        element.setAttribute("filename", filename)
        
        # create tag path 
        img_element = doc.createElement("path")
        img_element.appendChild(doc.createTextNode(file_path))
        element.appendChild(img_element)
        
        # create tag size
        img_element = doc.createElement("size")
        img_element.appendChild(doc.createTextNode(str(size)))
        element.appendChild(img_element)
        
        
        root.appendChild(element)

        # add the metadata to the element
        for key, value in metadata.items():
            if key == "sd-metadata":
                # parse the string value of sd-metadata as JSON
                sd_metadata = json.loads(value)

                # create a new element for the sd-metadata
                sd_element = doc.createElement(key)
                element.appendChild(sd_element)

                # loop through the elements in the sd-metadata
                for sd_key, sd_value in sd_metadata.items():
                    # add the value as a text node to the XML document
                    sub_element = doc.createElement(sd_key)
                    sub_element.appendChild(doc.createTextNode(str(sd_value)))
                    sd_element.appendChild(sub_element)
            else:
                img_element = doc.createElement(key)
                img_element.appendChild(doc.createTextNode(value))
                element.appendChild(img_element)

    return doc

def write_xml_document(doc, folder, verbose):
    # write the XML document to a file
    filename = os.path.join(folder, "metadata.xml")
    with open(filename, "w") as f:
	    doc 
	    f.write(doc.toprettyxml())
	    if verbose:
	        print(f"XML file created: {filename}")
	    
    return filename

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to a PNG file")
    parser.add_argument("-F", "--folder", help="Path to a folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()

    png_file = args.file
    folder = args.folder
    verbose = args.verbose
    
    if verbose:
        print("Verbose mode enabled")
        
    if png_file:
        metadata, size = process_png_file(png_file, verbose)
        print("Metadata for PNG file:")
        print("Size: "+str(size))
        print("Metadata: "+str(metadata))
        # Print the metadata to the screen
        
    if folder:
        #Get XML document from function
        print("Folder: "+folder)
        doc = create_xml_document(folder, verbose)
        write_xml_document(doc, folder, verbose)

### MAIN
if __name__ == "__main__":
    main()