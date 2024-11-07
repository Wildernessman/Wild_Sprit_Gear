from PIL import Image, ImageDraw, ImageFont
import os

def create_image(text, filename, size=(800, 400)):
    # Create image with dark background
    image = Image.new('RGB', size, (45, 50, 55))
    draw = ImageDraw.Draw(image)
    
    # Use a simple font since custom fonts might not be available
    font = ImageFont.load_default()
    
    # Calculate text position for center alignment
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Save image
    os.makedirs('static/uploads', exist_ok=True)
    image.save(os.path.join('static/uploads', filename))

def main():
    # Generate images for each section
    sections = [
        ('Welcome to ThreadCraft', 'welcome.jpg'),
        ('Premium T-Shirt Crafting', 'crafting.jpg'),
        ('Our Collection', 'collection.jpg'),
        ('Sustainable Fashion', 'sustainable.jpg'),
        ('Design Your Perfect Tee', 'design.jpg'),
        ('Join Our Community', 'community.jpg')
    ]
    
    for text, filename in sections:
        create_image(text, filename)

if __name__ == '__main__':
    main()
