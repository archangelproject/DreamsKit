package org.archangelproject.metadreams.metadata;

public class MetadataNode {

	private String keyword;
	private String value;
	
	public MetadataNode() {
		setKeyword(setValue(""));
	}
	
	public MetadataNode(String keyword, String value) {
		if(keyword==null)
			throw new IllegalArgumentException("Keyword must not be null");
		
		this.setKeyword(keyword.trim());
		this.setValue(value);
	}

	public String getKeyword() {
		return keyword;
	}

	public void setKeyword(String keyword) {
		this.keyword = keyword;
	}

	public String getValue() {
		return value;
	}

	public String setValue(String value) {
		this.value = value;
		return value;
	}
	
	public String toString() {
		return keyword+": "+value;
	}
}
