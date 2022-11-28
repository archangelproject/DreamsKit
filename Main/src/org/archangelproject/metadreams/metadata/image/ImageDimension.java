package org.archangelproject.metadreams.metadata.image;

public class ImageDimension {

	private int width;
	private int height;
	
	public ImageDimension() {
		this.setWidth(this.setHeight(0));
	}
	
	public ImageDimension(int width, int height) {
		this.setWidth(width);
		this.setHeight(height);
	}

	public int getWidth() {
		return this.width;
	}

	public int setWidth(int width) {
		this.width = width;
		return width;
	}

	public int getHeight() {
		return this.height;
	}

	public int setHeight(int height) {
		this.height = height;
		return height;
	}
	
	public String toString() {
		return "Width: "+this.getWidth()+" Height: "+this.getHeight();
	}
}
