from PIL import Image, ImageDraw

def crop_circle_center(image_path):
    # Open the original image
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # Calculate center
    center_x, center_y = width // 2, height // 2

    # Create same-sized mask with black background
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    radius = width/2

    # Draw white filled circle at center
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=255
    )

    # Apply mask to image
    result = Image.new("RGBA", img.size)
    result.paste(img, (0, 0), mask)

    # Crop to bounding box of the circle
    cropped = result.crop((
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ))

    return cropped

# Example usage
cropped_circle = crop_circle_center("profile.png")
cropped_circle.save("profile.png")
cropped_circle = crop_circle_center("profile-hover.png")
cropped_circle.save("profile-hover.png")