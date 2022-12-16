package org.archangelproject.metadreams.metadata;

import java.io.File;

import org.archangelproject.metadreams.exception.MetadataException;

public abstract class MetadataReader implements IMetadataReader {
	
	private File file;
	
	public MetadataReader(String filepath) throws MetadataException {
		if(filepath!=null) {
			this.file=new File(filepath);
			if(!this.file.exists()) throw new MetadataException("The specified file does not exist");
			if(this.file.isDirectory()) throw new MetadataException("The specified file is a directory");
		}
		else new MetadataException("The filepath must contain the path to the file");
	}
	
	public MetadataReader(File file) throws MetadataException {
		if(file!=null)
			this.file=file;
		else
			throw new MetadataException("File must not be null");
	}

	public File getFile() {
		return file;
	}
}
