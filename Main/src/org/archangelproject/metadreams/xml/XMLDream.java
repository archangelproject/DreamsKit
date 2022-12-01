/**
 * 
 */
package org.archangelproject.metadreams.xml;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/**
 * @author archangelproject
 * File containing all the info for a generated dream
 */

public class XMLDream {
	
	private Map<String, XMLAttribute> attributes;
	private String dreamName;

	public XMLDream(String dreamName) {
		super();
		
		this.dreamName = dreamName;
		this.attributes = new HashMap<String, XMLAttribute>(5);
	}
	
	public String getDreamName() {
		return this.dreamName;
	}
	
	public XMLAttribute addAttribute(String key, String value) {
		return this.addAttribute(new XMLAttribute(key, value));
	}
	
	public XMLAttribute addAttribute(XMLAttribute attribute) {
		if (attribute != null) {
			this.attributes.put(attribute.getKey(), attribute);
			return attribute;
		}
		
		return null;
	}
	
	public Set<String> getAttributeKeys() {
		return this.attributes.keySet();
	}
	
	public XMLAttribute getAttribute(String key) {
		return this.attributes.get(key);
	}
	
	public XMLAttribute deleteAttribute(String key) {
		return this.attributes.remove(key);
	}
}
