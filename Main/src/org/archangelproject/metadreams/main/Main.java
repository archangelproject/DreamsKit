package org.archangelproject.metadreams.main;

import java.util.List;

import org.archangelproject.metadreams.exception.MetadataException;
import org.archangelproject.metadreams.metadata.MetadataNode;
import org.archangelproject.metadreams.png.PNGReader;

public class Main {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		for(int i=0;i<args.length;i++) {
			i = parse(args, i);
		}
	}
	
	private static int parse(String[] args, int index) {
		int i = index;
		String command = args[i].substring(0, 2);
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
		}
		return i;
	}

}
