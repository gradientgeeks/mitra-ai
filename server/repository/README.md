# Repository Layer Documentation

This document describes the reorganized repository layer for the Mitra AI server, which has been broken down into specialized repositories for better maintainability and separation of concerns.

## Structure Overview

The repository layer has been refactored from a single monolithic `FirestoreRepository` class into several specialized repositories:

```
repository/
├── __init__.py                    # Package initialization with exports
├── base_repository.py             # Base class with common functionality
├── user_repository.py             # User profile and preferences operations
├── chat_repository.py             # Chat sessions and messages operations
├── wellness_repository.py         # Mood, journal, and meditation operations
└── firestore_repository.py        # Legacy wrapper for backward compatibility
```

## Repository Classes

### BaseRepository

**File**: `base_repository.py`

The base class that all other repositories inherit from. It provides:

- Firebase service initialization
- Common utility methods
- Timestamp conversion helpers
- Batch write operations
- Unique ID generation

### UserRepository

**File**: `user_repository.py`

Handles all user-related operations:

- **User Profile Management**
  - `create_user()` - Create new user profiles
  - `get_user()` - Retrieve user profiles
  - `update_user()` - Update user profiles
  - `update_user_preferences()` - Update user preferences
  - `increment_user_sessions()` - Track session counts

- **User Analytics & Management**
  - `get_user_stats()` - Get aggregated user statistics
  - `cleanup_old_sessions()` - Clean up old chat sessions
  - `delete_user_completely()` - GDPR-compliant user deletion
  - `backup_user_data()` - Create user data backups

### ChatRepository

**File**: `chat_repository.py`

Manages chat sessions and messages:

- **Chat Session Management**
  - `create_chat_session()` - Create new chat sessions
  - `get_chat_session()` - Retrieve specific chat sessions
  - `update_session_summary()` - Update session summaries
  - `get_chat_sessions_for_user()` - Get user's chat sessions
  - `delete_chat_session()` - Delete specific sessions

- **Message Management**
  - `add_message_to_session()` - Add messages to existing sessions

### WellnessRepository

**File**: `wellness_repository.py`

Handles wellness-related data operations:

- **Mood Tracking**
  - `create_mood_entry()` - Create mood entries
  - `get_mood_entries()` - Retrieve mood entries with date filtering
  - `update_mood_entry()` - Update existing mood entries
  - `delete_mood_entry()` - Delete mood entries

- **Journaling**
  - `create_journal_entry()` - Create journal entries
  - `get_journal_entries()` - Retrieve journal entries
  - `update_journal_entry()` - Update journal entries
  - `delete_journal_entry()` - Delete journal entries

- **Meditation**
  - `create_meditation_session()` - Create meditation sessions
  - `complete_meditation_session()` - Mark sessions as completed
  - `get_meditation_sessions_for_user()` - Retrieve meditation sessions

### FirestoreRepository (Legacy)

**File**: `firestore_repository.py`

A backward-compatible wrapper that delegates all operations to the appropriate specialized repositories. This ensures existing code continues to work without modifications.

## Migration Guide

### For New Development

Use the specialized repositories directly:

```python
from repository import UserRepository, ChatRepository, WellnessRepository

# Initialize specific repositories
user_repo = UserRepository()
chat_repo = ChatRepository()
wellness_repo = WellnessRepository()

# Use them directly
user_profile = await user_repo.get_user(uid)
chat_session = await chat_repo.get_chat_session(uid, session_id)
mood_entries = await wellness_repo.get_mood_entries(uid)
```

### For Existing Code

No changes required! The existing `FirestoreRepository` continues to work:

```python
from repository import FirestoreRepository

# This continues to work exactly as before
repo = FirestoreRepository()
user_profile = await repo.get_user(uid)
chat_session = await repo.get_chat_session(uid, session_id)
mood_entries = await repo.get_mood_entries(uid)
```

### Gradual Migration

You can gradually migrate existing code:

1. **Phase 1**: Use the new structure for new features
2. **Phase 2**: Update dependency injection to use specific repositories
3. **Phase 3**: Remove the legacy wrapper when all code is migrated

Example dependency injection update:

```python
# Before (still works)
def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

# After (new approach)
def get_user_repository() -> UserRepository:
    return UserRepository()

def get_chat_repository() -> ChatRepository:
    return ChatRepository()

def get_wellness_repository() -> WellnessRepository:
    return WellnessRepository()
```

## Benefits of the New Structure

### 1. **Separation of Concerns**
Each repository is focused on a specific domain (users, chat, wellness), making the code easier to understand and maintain.

### 2. **Better Testing**
Individual repositories can be tested in isolation, and you can mock only the specific repository you need for each test.

### 3. **Reduced Complexity**
Instead of one large class with 30+ methods, you now have smaller, focused classes that are easier to reason about.

### 4. **Team Development**
Different team members can work on different repositories without conflicts, as long as they don't modify the base repository.

### 5. **Future Extensibility**
Adding new domains (e.g., `NotificationRepository`, `AnalyticsRepository`) follows the established pattern.

### 6. **Dependency Management**
Each repository only imports what it needs, reducing the dependency footprint.

## Best Practices

### 1. **Use Specific Repositories in New Code**
```python
# Good
from repository import UserRepository
user_repo = UserRepository()

# Avoid (unless maintaining legacy code)
from repository import FirestoreRepository
repo = FirestoreRepository()
```

### 2. **Leverage the Base Repository**
When creating new repositories, inherit from `BaseRepository`:

```python
from repository.base_repository import BaseRepository

class NewDomainRepository(BaseRepository):
    def __init__(self):
        super().__init__()
    
    async def new_domain_operation(self):
        # Your implementation
        pass
```

### 3. **Handle Errors Appropriately**
Each repository method includes proper error handling and logging. Follow the same pattern:

```python
async def your_method(self):
    try:
        # Your operation
        return result
    except Exception as e:
        logger.error(f"Error in your_method: {e}")
        return None  # or appropriate default
```

### 4. **Use Type Hints**
All methods include proper type hints for better IDE support and code documentation.

## File Dependencies

```
base_repository.py
├── services.firebase_service
└── [No domain models]

user_repository.py
├── repository.base_repository
└── models.user

chat_repository.py
├── repository.base_repository
└── models.chat

wellness_repository.py
├── repository.base_repository
└── models.wellness

firestore_repository.py (legacy)
├── repository.user_repository
├── repository.chat_repository
├── repository.wellness_repository
└── [All model imports for backward compatibility]
```

This structure ensures clean dependencies and makes it easy to understand what each repository is responsible for.