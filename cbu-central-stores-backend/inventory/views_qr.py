from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product
from utils.qr_code_utils import decode_qr_code

class QRCodeScanView(APIView):
    """API endpoint to scan and decode QR codes."""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        decoded_data = decode_qr_code(image_file)
        
        if not decoded_data:
            return Response({'error': 'Could not decode QR code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If it's a product QR code, fetch product details
        if isinstance(decoded_data, dict) and 'product_id' in decoded_data:
            try:
                product = Product.objects.get(id=decoded_data['product_id'])
                from .serializers import ProductSerializer
                product_data = ProductSerializer(product).data
                return Response({
                    'decoded_data': decoded_data,
                    'product': product_data
                })
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'decoded_data': decoded_data})

class ProductQRCodeView(APIView):
    """API endpoint to get QR code for a product."""
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            return Response({
                'qr_code_url': product.qr_code.url if product.qr_code else None,
                'qr_code_data': product.qr_code_data
            })
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)