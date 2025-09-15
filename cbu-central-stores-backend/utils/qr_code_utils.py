import qrcode
import json
from io import BytesIO
from django.core.files import File
from django.conf import settings
import os

def generate_qr_code(data, product_id):
    """
    Generate a QR code for a product with the given data.
    Returns the file path of the saved QR code.
    """
    # Convert data to JSON string if it's a dict
    if isinstance(data, dict):
        data_str = json.dumps(data)
    else:
        data_str = str(data)

    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data_str)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    # Create file path
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    filename = f'product_{product_id}_qrcode.png'
    filepath = os.path.join(qr_dir, filename)
    
    # Save file
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return os.path.join('qr_codes', filename)

def decode_qr_code(image_file):
    """
    Decode a QR code from an uploaded image file.
    """
    from pyzbar.pyzbar import decode
    from PIL import Image
    import json
    
    try:
        image = Image.open(image_file)
        decoded_objects = decode(image)
        
        if decoded_objects:
            data = decoded_objects[0].data.decode('utf-8')
            try:
                return json.loads(data)  # Try to parse as JSON
            except json.JSONDecodeError:
                return data  # Return as string
        return None
    except Exception as e:
        print(f"QR decoding error: {e}")
        return None