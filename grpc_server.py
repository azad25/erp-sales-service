"""
gRPC Server for ERP Sales Service
"""
import os
import sys
import django
from concurrent import futures
import grpc
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Import gRPC service implementation
from grpc_services import SalesServiceServicer


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the sales service (commented out until proto files are generated)
    # sales_pb2_grpc.add_SalesServiceServicer_to_server(
    #     SalesServiceServicer(), server
    # )
    
    # Get gRPC port from settings or use default
    grpc_port = getattr(settings, 'GRPC_PORT', 50051)
    server_address = f'[::]:{grpc_port}'
    
    server.add_insecure_port(server_address)
    server.start()
    
    print(f"gRPC Sales Service server started on port {grpc_port}")
    print("Note: Proto files need to be generated for full gRPC functionality")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down gRPC server...")
        server.stop(0)


if __name__ == '__main__':
    serve() 