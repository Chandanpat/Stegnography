def calculate_required_percentage_ii(cover_image_size, secret_image_size):
    # Calculate the total number of pixels in the cover image
    total_cover_pixels = cover_image_size[0] * cover_image_size[1]
    
    # Calculate the total number of pixels in the secret image
    total_secret_pixels = secret_image_size[0] * secret_image_size[1]
    
    # Calculate the required percentage
    required_percentage = (total_secret_pixels / total_cover_pixels) * 100
    
    return required_percentage


def calculate_required_percentage_ti(image_size, message_size):
    total_image_pixels = image_size[0] * image_size[1]

    # Assuming each character in the message takes 1 byte
    required_percentage = (message_size * 8) / total_image_pixels * 100

    return required_percentage

