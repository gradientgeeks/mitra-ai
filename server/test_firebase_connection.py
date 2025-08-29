#!/usr/bin/env python3
"""
Simple Firebase connection test for Mitra AI server
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.append(str(Path(__file__).parent))

from services.firebase_service import FirebaseService

async def test_firebase_connection():
    """Test Firebase service connection and basic operations"""
    print("🔥 Testing Firebase Connection...")
    
    try:
        # Initialize Firebase service
        firebase_service = FirebaseService()
        print("✅ Firebase service initialized successfully")
        
        # Test health check
        health_status = await firebase_service.health_check()
        print(f"📊 Health check results:")
        for service, status in health_status.items():
            if service != 'errors' and service != 'timestamp':
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {service}: {status}")
        
        if health_status.get('errors'):
            print(f"⚠️  Errors: {health_status['errors']}")
        
        # Test basic Firestore operations
        print("\n🗄️  Testing Firestore operations...")
        
        # Try to get a user (should return None for non-existent user)
        test_uid = "test_user_12345"
        user_profile = await firebase_service.get_user_document(test_uid)
        if user_profile is None:
            print("✅ Firestore read operation working (user not found as expected)")
        else:
            print(f"📄 Found existing user: {user_profile}")
            
        print("\n🎉 Firebase connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Mitra AI Firebase Connection Test")
    print("=" * 50)
    
    # Check environment variables
    print("🔧 Checking environment variables...")
    firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
    firebase_creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    
    print(f"   FIREBASE_PROJECT_ID: {firebase_project_id}")
    print(f"   FIREBASE_CREDENTIALS_PATH: {firebase_creds_path}")
    
    if not firebase_project_id:
        print("❌ FIREBASE_PROJECT_ID not set in environment")
        sys.exit(1)
        
    if not firebase_creds_path:
        print("❌ FIREBASE_CREDENTIALS_PATH not set in environment")
        sys.exit(1)
        
    if not os.path.exists(firebase_creds_path):
        print(f"❌ Firebase credentials file not found: {firebase_creds_path}")
        sys.exit(1)
    
    print("✅ Environment variables configured correctly")
    print()
    
    # Run the test
    success = asyncio.run(test_firebase_connection())
    
    if success:
        print("\n🎉 All tests passed! Firebase is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        sys.exit(1)