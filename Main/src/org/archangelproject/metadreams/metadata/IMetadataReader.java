package org.archangelproject.metadreams.metadata;

import java.util.List;

import org.archangelproject.metadreams.exception.MetadataException;

public interface IMetadataReader {
	
	public List<MetadataNode> getMetadata() throws MetadataException;
	
	public void refresh() throws MetadataException;
	
	public void close();
	
	public boolean isClosed();
}
