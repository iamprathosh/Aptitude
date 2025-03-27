import os
import base64
import google.generativeai as genai
import logging

def setup_gemini():
    """Configure the Gemini API client with the API key from environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.warning("GEMINI_API_KEY not found in environment variables. OCR will not work properly.")
        return False
    
    genai.configure(api_key=api_key)
    return True

def encode_image_to_base64(image_file):
    """Encode an image file to base64 for the Gemini API."""
    image_bytes = image_file.read()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_image

def extract_text_from_image(image_file, prompt_type):
    """
    Use the Gemini API to extract text from an image.
    
    Args:
        image_file: The uploaded image file
        prompt_type: Either 'question' or 'options' to determine the prompt
    
    Returns:
        Extracted text from the image
    """
    try:
        # Set up the Gemini API
        if not setup_gemini():
            return "Error: Gemini API key not configured"
        
        # Encode the image to base64
        encoded_image = encode_image_to_base64(image_file)
        
        # Reset file pointer for potential reuse
        image_file.seek(0)
        
        # Configure the model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Define the prompt based on the type
        if prompt_type == 'question':
            prompt = "Extract the question text from this image. Return only the complete question as plain text."
        elif prompt_type == 'options':
            prompt = "Extract the multiple-choice options from this image. Format your response as a list with each option starting on a new line (e.g., 'A. Option text'). Return only the options without any additional text."
        else:
            return "Error: Invalid prompt type"
        
        # Make the API request
        response = model.generate_content([
            prompt,
            {
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": encoded_image
                }
            }
        ])
        
        # Return the extracted text
        return response.text.strip()
    
    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}")
        return f"Error: {str(e)}"

def parse_options(options_text):
    """
    Parse the options text extracted from the image into a list of options.
    
    Args:
        options_text: The text containing the options
        
    Returns:
        List of option texts
    """
    # Split by newlines and filter empty lines
    options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
    
    # Remove option indicators like "A.", "1.", etc. if present
    cleaned_options = []
    for opt in options:
        # Check if the option starts with a letter or number followed by a dot or parenthesis
        parts = opt.split('.', 1)
        if len(parts) > 1 and len(parts[0].strip()) <= 2:
            cleaned_options.append(parts[1].strip())
        else:
            parts = opt.split(')', 1)
            if len(parts) > 1 and len(parts[0].strip()) <= 2:
                cleaned_options.append(parts[1].strip())
            else:
                cleaned_options.append(opt)
    
    return cleaned_options
