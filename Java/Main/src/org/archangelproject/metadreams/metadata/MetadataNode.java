package org.archangelproject.metadreams.metadata;

public class MetadataNode {

	private String keyword;
	private String value;
	private String description;
	
	public MetadataNode() {
		setKeyword(setValue(setDescription("")));
	}
	
	public MetadataNode(String keyword, String value) {
		if(keyword==null)
			throw new IllegalArgumentException("Keyword must not be null");
		
		this.setKeyword(keyword.trim());
		this.setValue(value);
		this.setDescription("");
	}

	public String getKeyword() {
		return keyword;
	}

	public String setKeyword(String keyword) {
		this.keyword = keyword;
		return keyword;
	}

	public String getValue() {
		return value;
	}

	public String setValue(String value) {
		this.value = value;
		return value;
	}

	public String getDescription() {
		return description;
	}

	public String setDescription(String description) {
		this.description = description;
		return this.description;
	}
	
	public String toString() {
		return keyword+": "+value;
	}
}
