package org.archangelproject.metadreams.xml;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class XMLFolder {
	private boolean changed;
	private String folderPath;
	private String xmlFilepath;
	Map<String, XMLDream> dreams;
	
	public XMLFolder(String folderPath) {
		super();
		this.folderPath = folderPath;
		this.changed = true;
		this.xmlFilepath = "";
		this.dreams = new HashMap<String, XMLDream>(5);
	}

	public String getFolderPath() {
		return folderPath;
	}
	
	public XMLDream addDream(XMLDream dream) {
		if(dream != null) {
			this.dreams.put(dream.getDreamName(), dream);
			this.changed = true;
			return dream;
		}
		
		return null;
	}
	
	public XMLDream getDream(String dreamName) {
		return this.dreams.get(dreamName);
	}
	
	public XMLDream removeDream(String dreamName) {
		this.changed = true;
		return this.dreams.remove(dreamName);
	}
	
	public String writeXMLFile() throws ParserConfigurationException, TransformerException {
		if(this.changed) {
			DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
	        DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
	        
	        //Create the folder
	        Document doc = docBuilder.newDocument();
	        Element rootElement = doc.createElement(XMLKeys.XML_FOLDER_KEY);
	        doc.appendChild(rootElement);
	        
	        
	        Attr attrnode = doc.createAttribute("folderPath");
	        attrnode.setValue(this.folderPath);
	        rootElement.setAttributeNode(attrnode);
	        	        
	        Element folderAttr = doc.createElement(XMLKeys.XML_FOLDER_LAST_MODIFIED);
	        folderAttr.appendChild(doc.createTextNode(new SimpleDateFormat("dd/MMM/yyyy HH:mm:ss").format(new Date(new File(this.folderPath).lastModified()))));
	        rootElement.appendChild(folderAttr);
	        
	        Element elementDreams = doc.createElement(XMLKeys.XML_DREAMS_KEY);
	        rootElement.appendChild(elementDreams);
	        
	        Element elementDream;
	        XMLDream xmlDream;
	        
	        Attr attr;
	        XMLAttribute xmlAttr;
	        Element elementAttr;
	        
	        Set<String> dreamKeys = this.dreams.keySet();
	        Set<String> attrKeys;
	        for (String dreamFilename : dreamKeys) {
	        	xmlDream = this.dreams.get(dreamFilename);
				elementDream = doc.createElement(XMLKeys.XML_DREAM_KEY);
				elementDreams.appendChild(elementDream);
				
				attrKeys = xmlDream.getAttributeKeys();
				attr = doc.createAttribute(XMLKeys.DREAM_FILENAME);
				attr.setValue(xmlDream.getDreamName());
				elementDream.setAttributeNode(attr);
				for (String attrKey : attrKeys) {
					xmlAttr = xmlDream.getAttribute(attrKey);
					elementAttr = doc.createElement(xmlAttr.getKey());
					elementAttr.appendChild(doc.createTextNode(xmlAttr.getValue()));
					elementDream.appendChild(elementAttr);
				}
			}
	        
	        TransformerFactory transformerFactory = TransformerFactory.newInstance();
	        transformerFactory.setAttribute("indent-number", 4);
	        Transformer transformer = transformerFactory.newTransformer();
	        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
	        DOMSource source = new DOMSource(doc);
	        this.xmlFilepath = this.folderPath+File.separator+XMLKeys.XML_MAIN_FILENAME;
	        File outputFile = new File(this.xmlFilepath);
	        StreamResult result = new StreamResult(outputFile);

	        // Output to console for testing
	        // StreamResult result = new StreamResult(System.out);

	        transformer.transform(source, result);
		}
		
		return this.xmlFilepath;
	}
}
