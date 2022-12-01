package org.archangelproject.metadreams.xml;

public class XMLAttribute {
	private String key;
	private String value;
	private String description;
	
	public XMLAttribute(String key, String value) {
		super();
		this.key = key;
		this.value = value;
	}

	public XMLAttribute(String key, String value, String description) {
		super();
		this.key = key;
		this.value = value;
		this.description = description;
	}

	public String getKey() {
		return key;
	}

	public void setKey(String key) {
		this.key = key;
	}

	public String getValue() {
		return value;
	}

	public void setValue(String value) {
		this.value = value;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	@Override
	public String toString() {
		return "XMLAttribute [key=" + key + ", value=" + value + "]";
	}
}
