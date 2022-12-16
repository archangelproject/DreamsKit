package org.archangelproject.metadreams.main;

import java.io.File;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;

import org.archangelproject.metadreams.exception.MetadataException;
import org.archangelproject.metadreams.metadata.MetadataNode;
import org.archangelproject.metadreams.metadata.image.ImageDimension;
import org.archangelproject.metadreams.metadata.image.ImageMetadataReader;
import org.archangelproject.metadreams.metadata.image.png.PNGReader;
import org.archangelproject.metadreams.xml.XMLAttribute;
import org.archangelproject.metadreams.xml.XMLDream;
import org.archangelproject.metadreams.xml.XMLFolder;

public class Main {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		for(int i=0;i<args.length;i++) {
			i = parse(args, i);
		}
	}
	
	private static int parse(String[] args, int index) {
		int i = index;
		String command = args[i].substring(0, 2); //only single letter parameters allowed with this setup
		switch(command) {
			case "-f":
				try {
					PNGReader reader = new PNGReader(args[i+1]);
					System.out.println("DIMENSION: "+reader.getSize());
					List<MetadataNode> nodes;
				
					nodes = reader.getMetadata();
				
					for(int j=0;j<nodes.size();j++) {
						System.out.println(nodes.get(j));
					}
					i++;
				} catch (MetadataException e) {
					System.out.println(e.getMessage());
				}
				break;
			
			case "-F":
				try {
					File folder = new File(args[++i]);
					if (folder.isDirectory()){
						File[] files = folder.listFiles();
						
						XMLFolder xmlFolder = new XMLFolder(folder.getAbsolutePath());
						XMLDream xmlDream;
						
						ImageMetadataReader reader;
						ImageDimension dimension;
						for (int j = 0; j < files.length; j++) {
							if(!files[j].isDirectory()) {
								try { //Catch the MetadataException to ignore the files that are not PNG
									xmlDream = new XMLDream(files[j].getName());
									reader = new PNGReader(files[j]);
									dimension = reader.getSize();
									xmlDream.addAttribute(new XMLAttribute("width", String.valueOf(dimension.getWidth())));
									xmlDream.addAttribute(new XMLAttribute("height", String.valueOf(dimension.getHeight())));
									List<MetadataNode> nodes = reader.getMetadata();
									for (int k = 0; k < nodes.size(); k++) {
										xmlDream.addAttribute(new XMLAttribute(nodes.get(k).getKeyword(), nodes.get(k).getValue()));
									}
									xmlFolder.addDream(xmlDream);
								}
								catch(MetadataException except) {
									//Not a PNG file, ignore
								}
							}
						}
						
						System.out.println("File generated in: "+xmlFolder.writeXMLFile());
					}
					else {
						System.out.println("The specified path is not a directory");
					}
				} catch (ParserConfigurationException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (TransformerException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				break;
		}
		return i;
	}
}
