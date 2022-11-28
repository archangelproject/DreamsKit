package org.archangelproject.metadreams.metadata.image;

import java.io.File;

import org.archangelproject.metadreams.exception.MetadataException;
import org.archangelproject.metadreams.metadata.MetadataReader;

public abstract class ImageMetadataReader extends MetadataReader {

	public ImageMetadataReader(String filepath) throws MetadataException {
		super(filepath);
	}

	public ImageMetadataReader(File file) throws MetadataException {
		super(file);
	}
	
	public abstract ImageDimension getSize();
}
