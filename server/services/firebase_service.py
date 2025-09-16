"""
Firebase service for authentication and Firestore operations.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os

# Firebase Admin SDK imports
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage, exceptions

from core.config import settings
from models.user import UserProfile, UserProvider, UserStatus, UserPreferences

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for Firebase Authentication and Firestore operations."""
    
    def __init__(self):
        """Initialize Firebase services."""
        self.auth = None
        self.db = None
        
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
            # Initialize Firebase Admin SDK
            if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path) and os.path.getsize(settings.firebase_credentials_path) > 0:
                # Use service account credentials file
                cred = credentials.Certificate(settings.firebase_credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': settings.firebase_project_id,
                    'storageBucket': settings.firebase_storage_bucket or f"{settings.firebase_project_id}.firebasestorage.app"
                })
                logger.info(f"Firebase initialized with service account from {settings.firebase_credentials_path}")
            elif settings.firebase_project_id:
                # Use default credentials (for Cloud Run, GCE, etc.)
                try:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {
                        'projectId': settings.firebase_project_id,
                        'storageBucket': settings.firebase_storage_bucket or f"{settings.firebase_project_id}.firebasestorage.app"
                    })
                    logger.info("Firebase initialized with application default credentials")
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase with default credentials: {e}")
                    raise
            else:
                logger.error("Firebase configuration missing. Set FIREBASE_CREDENTIALS_PATH or FIREBASE_PROJECT_ID")
                raise ValueError("Firebase configuration missing")
        
        # Initialize Firebase services
        self.auth = auth
        self.db = firestore.client()
        self.storage_bucket = storage.bucket()
        logger.info("Firebase services initialized successfully")

    def _handle_firebase_error(self, error: Exception, operation: str) -> None:
        """
        Centralized Firebase error handling and logging.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
        """
        if isinstance(error, exceptions.InvalidArgumentError):
            logger.error(f"{operation} failed: Invalid arguments - {error}")
        elif isinstance(error, exceptions.NotFoundError):
            logger.error(f"{operation} failed: Resource not found - {error}")
        elif isinstance(error, exceptions.AlreadyExistsError):
            logger.error(f"{operation} failed: Resource already exists - {error}")
        elif isinstance(error, exceptions.PermissionDeniedError):
            logger.error(f"{operation} failed: Permission denied - {error}")
        elif isinstance(error, exceptions.UnauthenticatedError):
            logger.error(f"{operation} failed: Unauthenticated - {error}")
        elif isinstance(error, exceptions.ResourceExhaustedError):
            logger.error(f"{operation} failed: Resource exhausted/quota exceeded - {error}")
        elif isinstance(error, exceptions.FailedPreconditionError):
            logger.error(f"{operation} failed: Failed precondition - {error}")
        elif isinstance(error, exceptions.AbortedError):
            logger.error(f"{operation} failed: Operation aborted - {error}")
        elif isinstance(error, exceptions.OutOfRangeError):
            logger.error(f"{operation} failed: Out of range - {error}")
        elif isinstance(error, exceptions.UnimplementedError):
            logger.error(f"{operation} failed: Unimplemented - {error}")
        elif isinstance(error, exceptions.InternalError):
            logger.error(f"{operation} failed: Internal error - {error}")
        elif isinstance(error, exceptions.UnavailableError):
            logger.error(f"{operation} failed: Service unavailable - {error}")
        elif isinstance(error, exceptions.DataLossError):
            logger.error(f"{operation} failed: Data loss - {error}")
        elif isinstance(error, exceptions.FirebaseError):
            logger.error(f"{operation} failed: Firebase error - {error}")
        else:
            logger.error(f"{operation} failed: Unexpected error - {error}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on Firebase services.
        
        Returns:
            Dictionary with service status information
        """
        health_status = {
            "firebase_admin": False,
            "auth": False,
            "firestore": False,
            "timestamp": datetime.utcnow().isoformat(),
            "errors": []
        }
        
        try:
            # Check if Firebase Admin is initialized
            firebase_admin.get_app()
            health_status["firebase_admin"] = True
        except Exception as e:
            health_status["errors"].append(f"Firebase Admin: {str(e)}")
        
        try:
            # Test Auth service
            if self.auth:
                # Try to get a non-existent user (this tests auth connectivity)
                try:
                    self.auth.get_user("health-check-non-existent-user")
                except exceptions.UserNotFoundError:
                    # This is expected and means auth is working
                    health_status["auth"] = True
                except Exception as e:
                    health_status["errors"].append(f"Auth service: {str(e)}")
            else:
                health_status["errors"].append("Auth service not initialized")
        except Exception as e:
            health_status["errors"].append(f"Auth check: {str(e)}")
        
        try:
            # Test Firestore service
            if self.db:
                # Try to read from a collection (minimal operation)
                collection_ref = self.db.collection('health-check')
                list(collection_ref.limit(1).stream())
                health_status["firestore"] = True
            else:
                health_status["errors"].append("Firestore service not initialized")
        except Exception as e:
            health_status["errors"].append(f"Firestore service: {str(e)}")
        
        return health_status

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user record by email from Firebase Auth.
        
        Args:
            email: User email address
            
        Returns:
            User record dictionary or None if not found
        """
        try:
            user_record = self.auth.get_user_by_email(email)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'phone_number': user_record.phone_number,
                'photo_url': user_record.photo_url,
                'disabled': user_record.disabled,
                'email_verified': user_record.email_verified,
                'provider_data': [
                    {
                        'uid': p.uid,
                        'email': p.email,
                        'display_name': p.display_name,
                        'phone_number': p.phone_number,
                        'photo_url': p.photo_url,
                        'provider_id': p.provider_id
                    } for p in user_record.provider_data
                ],
                'metadata': {
                    'creation_timestamp': user_record.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': user_record.user_metadata.last_sign_in_timestamp,
                    'last_refresh_timestamp': user_record.user_metadata.last_refresh_timestamp,
                }
            }
            
        except exceptions.UserNotFoundError:
            logger.info(f"User with email {email} not found in Firebase Auth")
            return None
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid email format: {e}")
            return None
        except exceptions.FirebaseError as e:
            self._handle_firebase_error(e, f"Getting user by email {email}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user by email {email}: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new user in Firebase Auth.
        
        Args:
            user_data: User data (email, password, display_name, etc.)
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            user_record = self.auth.create_user(**user_data)
            logger.info(f"Created user {user_record.uid} with email {user_data.get('email')}")
            return user_record.uid
            
        except exceptions.EmailAlreadyExistsError:
            logger.error(f"User with email {user_data.get('email')} already exists")
            return None
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid user data: {e}")
            return None
        except exceptions.FirebaseError as e:
            self._handle_firebase_error(e, "Creating user")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            return None

    async def update_user(self, uid: str, user_data: Dict[str, Any]) -> bool:
        """
        Update user record in Firebase Auth.
        
        Args:
            uid: User ID
            user_data: Updated user data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.auth.update_user(uid, **user_data)
            logger.info(f"Updated user {uid}")
            return True
            
        except exceptions.UserNotFoundError:
            logger.error(f"User {uid} not found for update")
            return False
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid user data for update: {e}")
            return False
        except exceptions.FirebaseError as e:
            self._handle_firebase_error(e, f"Updating user {uid}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating user {uid}: {e}")
            return False

    async def delete_user(self, uid: str) -> bool:
        """
        Delete user from Firebase Auth.
        
        Args:
            uid: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.auth.delete_user(uid)
            logger.info(f"Deleted user {uid} from Firebase Auth")
            return True
            
        except exceptions.UserNotFoundError:
            logger.error(f"User {uid} not found for deletion")
            return False
        except exceptions.FirebaseError as e:
            self._handle_firebase_error(e, f"Deleting user {uid}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting user {uid}: {e}")
            return False

    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token and return user claims.
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Dictionary with user claims (uid, email, etc.)
        """
        try:
            # Run the synchronous Firebase verification in an executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            decoded_token = await loop.run_in_executor(None, self.auth.verify_id_token, id_token)
            return decoded_token
            
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid ID token format: {e}")
            raise ValueError("Invalid ID token format")
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error verifying ID token: {e}")
            raise ValueError("Invalid or expired ID token")
        except Exception as e:
            logger.error(f"Unexpected error verifying ID token: {e}")
            raise ValueError("Token verification failed")

    async def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> str:
        """
        Create a custom token for a user.
        
        Args:
            uid: User ID
            additional_claims: Additional claims to include
            
        Returns:
            Custom token string
        """
        try:
            custom_token = self.auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8')
            
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid arguments for custom token: {e}")
            raise ValueError("Invalid user ID or claims")
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error creating custom token: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating custom token: {e}")
            raise

    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user record from Firebase Auth.
        
        Args:
            uid: User ID
            
        Returns:
            User record dictionary or None if not found
        """
        try:
            user_record = self.auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'phone_number': user_record.phone_number,
                'photo_url': user_record.photo_url,
                'disabled': user_record.disabled,
                'email_verified': user_record.email_verified,
                'provider_data': [
                    {
                        'uid': p.uid,
                        'email': p.email,
                        'display_name': p.display_name,
                        'phone_number': p.phone_number,
                        'photo_url': p.photo_url,
                        'provider_id': p.provider_id
                    } for p in user_record.provider_data
                ],
                'metadata': {
                    'creation_timestamp': user_record.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': user_record.user_metadata.last_sign_in_timestamp,
                    'last_refresh_timestamp': user_record.user_metadata.last_refresh_timestamp,
                }
            }
            
        except exceptions.UserNotFoundError:
            logger.info(f"User {uid} not found in Firebase Auth")
            return None
        except exceptions.InvalidArgumentError as e:
            logger.error(f"Invalid user ID format: {e}")
            return None
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting user {uid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user {uid}: {e}")
            return None

    async def create_user_document(self, user_profile: UserProfile) -> bool:
        """
        Create user document in Firestore.
        
        Args:
            user_profile: User profile to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(user_profile.uid)
            doc_ref.set(user_profile.dict())
            logger.info(f"Created user document for {user_profile.uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error creating user document: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating user document: {e}")
            return False

    async def get_user_document(self, uid: str) -> Optional[UserProfile]:
        """
        Get user document from Firestore.
        
        Args:
            uid: User ID
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            doc_ref = self.db.collection('users').document(uid)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return UserProfile(**data)
            logger.info(f"User document not found for {uid}")
            return None
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting user document: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user document: {e}")
            return None

    async def update_user_document(self, uid: str, updates: Dict[str, Any]) -> bool:
        """
        Update user document in Firestore.
        
        Args:
            uid: User ID
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(uid)
            doc_ref.update(updates)
            logger.info(f"Updated user document for {uid}")
            return True
            
        except exceptions.NotFoundError:
            logger.error(f"User document not found for update: {uid}")
            return False
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error updating user document: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating user document: {e}")
            return False

    async def save_chat_session(self, uid: str, session_data: Dict[str, Any]) -> bool:
        """
        Save chat session to Firestore.
        
        Args:
            uid: User ID
            session_data: Session data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(uid).collection('chat_sessions').document(session_data['session_id'])
            doc_ref.set(session_data)
            logger.info(f"Saved chat session {session_data['session_id']} for {uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error saving chat session: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving chat session: {e}")
            return False

    async def get_chat_session(self, uid: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chat session from Firestore.
        
        Args:
            uid: User ID
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        try:
            doc_ref = self.db.collection('users').document(uid).collection('chat_sessions').document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            logger.info(f"Chat session {session_id} not found for {uid}")
            return None
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting chat session: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting chat session: {e}")
            return None

    async def save_mood_entry(self, uid: str, mood_data: Dict[str, Any]) -> bool:
        """
        Save mood entry to Firestore.
        
        Args:
            uid: User ID
            mood_data: Mood entry data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(uid).collection('mood_entries').document(mood_data['id'])
            doc_ref.set(mood_data)
            logger.info(f"Saved mood entry {mood_data['id']} for {uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error saving mood entry: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving mood entry: {e}")
            return False

    async def get_mood_entries(self, uid: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent mood entries for a user.
        
        Args:
            uid: User ID
            limit: Maximum number of entries to return
            
        Returns:
            List of mood entries
        """
        try:
            collection_ref = self.db.collection('users').document(uid).collection('mood_entries')
            query = collection_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            entries = [doc.to_dict() for doc in docs]
            logger.info(f"Retrieved {len(entries)} mood entries for {uid}")
            return entries
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting mood entries: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting mood entries: {e}")
            return []

    async def save_journal_entry(self, uid: str, journal_data: Dict[str, Any]) -> bool:
        """
        Save journal entry to Firestore.
        
        Args:
            uid: User ID
            journal_data: Journal entry data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(uid).collection('journal_entries').document(journal_data['id'])
            doc_ref.set(journal_data)
            logger.info(f"Saved journal entry {journal_data['id']} for {uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error saving journal entry: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving journal entry: {e}")
            return False

    async def get_journal_entries(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent journal entries for a user.
        
        Args:
            uid: User ID
            limit: Maximum number of entries to return
            
        Returns:
            List of journal entries
        """
        try:
            collection_ref = self.db.collection('users').document(uid).collection('journal_entries')
            query = collection_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            docs = query.stream()
            entries = [doc.to_dict() for doc in docs]
            logger.info(f"Retrieved {len(entries)} journal entries for {uid}")
            return entries
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting journal entries: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting journal entries: {e}")
            return []

    async def save_meditation_session(self, uid: str, meditation_data: Dict[str, Any]) -> bool:
        """
        Save meditation session to Firestore.
        
        Args:
            uid: User ID
            meditation_data: Meditation session data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('users').document(uid).collection('meditation_sessions').document(meditation_data['id'])
            doc_ref.set(meditation_data)
            logger.info(f"Saved meditation session {meditation_data['id']} for {uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error saving meditation session: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving meditation session: {e}")
            return False

    async def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Perform batch write operations.
        
        Args:
            operations: List of operations to perform
            Each operation should have:
            - type: 'set', 'update', or 'delete'
            - collection: collection path
            - document: document ID
            - data: data to write (for set/update operations)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            batch = self.db.batch()
            
            for op in operations:
                if 'collection' in op and 'document' in op:
                    doc_ref = self.db.collection(op['collection']).document(op['document'])
                elif 'ref' in op:
                    # Support legacy format with direct reference
                    doc_ref = op['ref']
                else:
                    logger.error(f"Invalid operation format: {op}")
                    continue
                
                if op['type'] == 'set':
                    batch.set(doc_ref, op['data'])
                elif op['type'] == 'update':
                    batch.update(doc_ref, op['data'])
                elif op['type'] == 'delete':
                    batch.delete(doc_ref)
                else:
                    logger.error(f"Unknown operation type: {op['type']}")
                    continue
            
            batch.commit()
            logger.info(f"Successfully completed batch write with {len(operations)} operations")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error performing batch write: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error performing batch write: {e}")
            return False

    async def get_user_collections_data(self, uid: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all user's collection data for analytics or export.
        
        Args:
            uid: User ID
            
        Returns:
            Dictionary with collection names as keys and document lists as values
        """
        try:
            user_data = {}
            collections = ['chat_sessions', 'mood_entries', 'journal_entries', 'meditation_sessions']
            
            for collection_name in collections:
                collection_ref = self.db.collection('users').document(uid).collection(collection_name)
                docs = collection_ref.stream()
                user_data[collection_name] = [doc.to_dict() for doc in docs]
                
            logger.info(f"Retrieved all collection data for {uid}")
            return user_data
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error getting user collections: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error getting user collections: {e}")
            return {}

    async def delete_user_data(self, uid: str) -> bool:
        """
        Delete all user data from Firestore (for GDPR compliance).
        
        Args:
            uid: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all subcollections first
            collections = ['chat_sessions', 'mood_entries', 'journal_entries', 'meditation_sessions']
            
            for collection_name in collections:
                collection_ref = self.db.collection('users').document(uid).collection(collection_name)
                docs = collection_ref.list_documents()
                
                # Delete in batches to avoid timeout
                batch = self.db.batch()
                count = 0
                
                for doc in docs:
                    batch.delete(doc)
                    count += 1
                    
                    if count >= 500:  # Firestore batch limit
                        batch.commit()
                        batch = self.db.batch()
                        count = 0
                
                if count > 0:
                    batch.commit()
            
            # Delete main user document
            self.db.collection('users').document(uid).delete()
            
            logger.info(f"Successfully deleted all data for user {uid}")
            return True
            
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error deleting user data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting user data: {e}")
            return False

    # Firebase Storage methods

    async def upload_file_to_storage(
        self, 
        file_data: bytes, 
        file_path: str, 
        content_type: str = "image/jpeg",
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Upload a file to Firebase Storage.
        
        Args:
            file_data: File data as bytes
            file_path: Path in storage (e.g., "mitra_profiles/mitra.jpg")
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        try:
            # Get blob reference
            blob = self.storage_bucket.blob(file_path)
            
            # Set metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            blob.upload_from_string(
                file_data,
                content_type=content_type
            )
            
            # Make blob publicly readable
            blob.make_public()
            
            # Return public URL
            public_url = blob.public_url
            logger.info(f"Successfully uploaded file to {file_path}: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading file to storage {file_path}: {e}")
            return None

    async def download_file_from_storage(self, file_path: str) -> Optional[bytes]:
        """
        Download a file from Firebase Storage.
        
        Args:
            file_path: Path in storage
            
        Returns:
            File data as bytes or None if not found
        """
        try:
            blob = self.storage_bucket.blob(file_path)
            
            if not blob.exists():
                logger.debug(f"File does not exist in storage: {file_path}")
                return None
            
            file_data = blob.download_as_bytes()
            logger.debug(f"Successfully downloaded file from {file_path}")
            return file_data
            
        except Exception as e:
            logger.error(f"Error downloading file from storage {file_path}: {e}")
            return None

    async def delete_file_from_storage(self, file_path: str) -> bool:
        """
        Delete a file from Firebase Storage.
        
        Args:
            file_path: Path in storage
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            blob = self.storage_bucket.blob(file_path)
            
            if not blob.exists():
                logger.debug(f"File does not exist in storage: {file_path}")
                return True  # Consider as successful deletion
            
            blob.delete()
            logger.info(f"Successfully deleted file from storage: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from storage {file_path}: {e}")
            return False

    async def get_file_public_url(self, file_path: str) -> Optional[str]:
        """
        Get the public URL of a file in Firebase Storage.
        
        Args:
            file_path: Path in storage
            
        Returns:
            Public URL or None if file doesn't exist
        """
        try:
            blob = self.storage_bucket.blob(file_path)
            
            if not blob.exists():
                logger.debug(f"File does not exist in storage: {file_path}")
                return None
            
            # Make sure it's public
            blob.make_public()
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error getting public URL for {file_path}: {e}")
            return None

    async def list_files_in_directory(self, directory_path: str) -> List[str]:
        """
        List all files in a specific directory in Firebase Storage.
        
        Args:
            directory_path: Directory path in storage (e.g., "mitra_profiles/")
            
        Returns:
            List of file paths
        """
        try:
            # Ensure directory path ends with /
            if not directory_path.endswith("/"):
                directory_path += "/"
            
            blobs = self.storage_bucket.list_blobs(prefix=directory_path)
            file_paths = [blob.name for blob in blobs if not blob.name.endswith("/")]
            
            logger.debug(f"Found {len(file_paths)} files in {directory_path}")
            return file_paths
            
        except Exception as e:
            logger.error(f"Error listing files in {directory_path}: {e}")
            return []

    async def save_flashcards(self, uid: str, journal_id: str, flashcards: List[Dict[str, Any]]) -> bool:
        """
        Save flashcards to a journal entry subcollection.

        Args:
            uid: User ID
            journal_id: Journal entry ID
            flashcards: List of flashcard data

        Returns:
            True if successful, False otherwise
        """
        try:
            operations = []
            for card in flashcards:
                operations.append({
                    'type': 'set',
                    'collection': f'users/{uid}/journal_entries/{journal_id}/flashcards',
                    'document': card['id'],
                    'data': card
                })
            return await self.batch_write(operations)
        except Exception as e:
            logger.error(f"Error saving flashcards to subcollection: {e}")
            return False
