from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .web3_client import web3_client
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class BlockchainStatusView(APIView):
    """API endpoint to check blockchain connection status."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        },
        description="Check blockchain connection status and account info"
    )
    def get(self, request):
        try:
            # Initialize if not already done
            if not hasattr(web3_client, 'simulation_mode'):
                web3_client._initialize()
            
            if web3_client.simulation_mode:
                return Response({
                    'status': 'simulation_mode',
                    'message': 'Blockchain environment variables not configured'
                })
            
            # Test connection
            is_connected = web3_client.w3.is_connected()
            latest_block = web3_client.w3.eth.block_number
            account_balance = web3_client.w3.eth.get_balance(web3_client.account.address)
            
            return Response({
                'connected': is_connected,
                'latest_block': latest_block,
                'account_balance': web3_client.w3.from_wei(account_balance, 'ether'),
                'contract_address': web3_client.contract_address,
                'account_address': web3_client.account.address
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class BlockchainEventsView(APIView):
    """API endpoint to get blockchain events for a request."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='request_id', type=int, location=OpenApiParameter.PATH, description='Request ID to filter events')
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        },
        description="Get blockchain events for a specific request"
    )
    

    def get(self, request, request_id):
        try:
            # Initialize if not already done
            if not hasattr(web3_client, 'simulation_mode'):
                web3_client._initialize()
            
            if web3_client.simulation_mode:
                return Response({
                    'status': 'simulation_mode',
                    'message': 'Blockchain environment variables not configured',
                    'events': []
                })
            
            events = web3_client.get_approval_events(request_id)
            serialized_events = []
            
            for event in events:
                serialized_events.append({
                    'transaction_hash': event['transactionHash'].hex(),
                    'block_number': event['blockNumber'],
                    'request_id': event['args']['requestId'],
                    'stage': event['args']['stage'],
                    'approver_role': event['args']['approverRole'],
                    'approved': event['args']['approved'],
                    'comment': event['args']['comment'],
                    'timestamp': event['args']['timestamp']
                })
            
            return Response({'events': serialized_events})
        except Exception as e:
            return Response({'error': str(e)}, status=500)