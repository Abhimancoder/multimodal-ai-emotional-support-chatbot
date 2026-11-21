# Database Schema Specification

## Database: MySQL (Default Engine: InnoDB, Charset: utf8mb4)

### 1. `chat_sessions` Table
Tracks independent conversation threads.
```sql
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,                 -- UUID v4
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_sessions_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2. `messages` Table
Stores turns for both user and assistant.
```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    modality ENUM('text', 'image', 'audio', 'multimodal') NOT NULL DEFAULT 'text',
    tts_audio_path VARCHAR(512) NULL,
    has_grounding_card BOOLEAN DEFAULT FALSE,
    card_type VARCHAR(64) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    INDEX idx_messages_session (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 3. `media_metadata` Table
Stores metadata for uploaded files attached to messages.
```sql
CREATE TABLE media_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    mime_type VARCHAR(64) NOT NULL,
    file_size_bytes INT NOT NULL,
    duration_seconds FLOAT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 4. `safety_events` Table
Audit log for safety triggers and crisis interventions (sanitized, no PII).
```sql
CREATE TABLE safety_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NULL,
    trigger_type ENUM('crisis_self_harm', 'medical_advice_request', 'prompt_injection', 'malformed_file') NOT NULL,
    action_taken ENUM('crisis_helpline_injected', 'disclaimer_appended', 'blocked') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
