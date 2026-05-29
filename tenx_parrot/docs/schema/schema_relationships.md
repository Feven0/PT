# Detailed Schema Relationships

This document provides comprehensive visual representations of all schema entities and their relationships using Mermaid diagrams.

## Individual Schema Entities

### ConversationFlowConfiguration

```mermaid
classDiagram
    class ConversationFlowConfiguration {
        +String id
        +String name
        +String description
        +String manager_class
        +String ai_role_id
        +String modality_id
        +String purpose_id
        +Boolean is_template
        +JSON metadata
    }
```

### FlowConfigurationComponent

```mermaid
classDiagram
    class FlowConfigurationComponent {
        +String id
        +String flow_configuration_id
        +String component_type
        +JSON component_configuration
        +String context_document_id
        +JSON relationships
    }
```

### ContextDocumentType

```mermaid
classDiagram
    class ContextDocumentType {
        +String id
        +String name
        +JSON schema
        +JSON metadata
    }
```

### ContextDocument

```mermaid
classDiagram
    class ContextDocument {
        +String id
        +String document_type_id
        +JSON content
        +JSON metadata
    }
```

### ConversationModality

```mermaid
classDiagram
    class ConversationModality {
        +String id
        +String name
        +String description
        +String[] supported_media_types
        +Boolean is_streaming
        +JSON metadata
    }
```

### ConversationPurpose

```mermaid
classDiagram
    class ConversationPurpose {
        +String id
        +String name
        +String description
        +JSON flow_steps
        +JSON evaluation_metrics
        +JSON[] prompt_ids
        +JSON metadata
    }
```

### AIRole

```mermaid
classDiagram
    class AIRole {
        +String id
        +String name
        +String description
        +String persona_template_id
        +JSON skill
        +JSON behaviour_configuration
        +JSON response_templates
        +JSON role_specific_rubrics
        +JSON metadata
    }
```

### AIPersonaTemplate

```mermaid
classDiagram
    class AIPersonaTemplate {
        +String id
        +String name
        +String description
        +JSON personality_traits
        +JSON communication_style
        +JSON knowledge_base
        +JSON response_patterns
        +JSON metadata
    }
```

### ConversationSession

```mermaid
classDiagram
    class ConversationSession {
        +String id
        +String slug
        +String status
        +String flow_config_id
        +String context_document_id
        +String stream_id
        +JSON session_configuration
        +DateTime started_at
        +DateTime ended_at
        +JSON generation_context
        +JSON analysis_context
        +JSON metadata
    }
```

### ConversationMessage

```mermaid
classDiagram
    class ConversationMessage {
        +String id
        +String session_id
        +JSON attributes
        +JSON metadata
    }
```

### MessageAnalysis

```mermaid
classDiagram
    class MessageAnalysis {
        +String id
        +String message_id
        +String analysis_type
        +String analysis_model
        +String analyzer_model
        +JSON analysis_configuration
        +JSON analysis_results
        +JSON metric_scores
        +JSON improvement_suggestions
        +JSON metadata
    }
```

### SessionObserver

```mermaid
classDiagram
    class SessionObserver {
        +String id
        +String session_id
        +JSON observation_configuration
        +JSON collected_metrics
        +JSON metadata
    }
```

## Complete Entity Relationships

```mermaid
erDiagram
    ConversationFlowConfiguration ||--o{ FlowConfigurationComponent : "has components"
    ConversationFlowConfiguration ||--o{ ConversationSession : "has sessions"
    ConversationModality ||--o{ ConversationFlowConfiguration : "used by"
    ConversationPurpose ||--o{ ConversationFlowConfiguration : "used by"
    AIRole ||--o{ ConversationFlowConfiguration : "used by"
    AIPersonaTemplate ||--o{ AIRole : "used by"
    
    ContextDocumentType ||--o{ ContextDocument : "defines"
    ContextDocument ||--o{ FlowConfigurationComponent : "referenced by"
    ContextDocument ||--o{ ConversationSession : "provides context for"
    
    ConversationSession ||--o{ ConversationMessage : "contains"
    ConversationSession ||--o{ SessionObserver : "observed by"
    
    ConversationMessage ||--o{ MessageAnalysis : "analyzed by"
```

## Detailed Relationship Descriptions

### One-to-Many Relationships

1. **ConversationFlowConfiguration to FlowConfigurationComponent**
   - One flow configuration can have many components
   - Each component belongs to exactly one flow configuration

2. **ConversationFlowConfiguration to ConversationSession**
   - One flow configuration can be used by many conversation sessions
   - Each session uses exactly one flow configuration

3. **ConversationModality to ConversationFlowConfiguration**
   - One modality can be used by many flow configurations
   - Each flow configuration uses exactly one modality

4. **ConversationPurpose to ConversationFlowConfiguration**
   - One purpose can be used by many flow configurations
   - Each flow configuration has exactly one purpose

5. **AIRole to ConversationFlowConfiguration**
   - One AI role can be used by many flow configurations
   - Each flow configuration uses exactly one AI role

6. **AIPersonaTemplate to AIRole**
   - One persona template can be used by many AI roles
   - Each AI role uses exactly one persona template

7. **ContextDocumentType to ContextDocument**
   - One document type can define many context documents
   - Each context document has exactly one document type

8. **ContextDocument to FlowConfigurationComponent**
   - One context document can be referenced by many flow components
   - Each component can reference exactly one context document

9. **ContextDocument to ConversationSession**
   - One context document can provide context for many sessions
   - Each session can have exactly one context document

10. **ConversationSession to ConversationMessage**
    - One session can contain many messages
    - Each message belongs to exactly one session

11. **ConversationSession to SessionObserver**
    - One session can have many observers
    - Each observer is linked to exactly one session

12. **ConversationMessage to MessageAnalysis**
    - One message can have many analyses
    - Each analysis is for exactly one message

## Component Relationships and Dependencies

```mermaid
flowchart TD
    ConversationFlowConfiguration --> AIRole
    ConversationFlowConfiguration --> ConversationModality
    ConversationFlowConfiguration --> ConversationPurpose
    
    AIRole --> AIPersonaTemplate
    
    FlowConfigurationComponent --> ConversationFlowConfiguration
    FlowConfigurationComponent --> ContextDocument
    
    ContextDocument --> ContextDocumentType
    
    ConversationSession --> ConversationFlowConfiguration
    ConversationSession --> ContextDocument
    
    ConversationMessage --> ConversationSession
    
    MessageAnalysis --> ConversationMessage
    
    SessionObserver --> ConversationSession
```

## Data Flow Overview

```mermaid
sequenceDiagram
    participant User
    participant Session as ConversationSession
    participant FlowConfig as ConversationFlowConfiguration
    participant Message as ConversationMessage
    participant Analysis as MessageAnalysis
    participant Observer as SessionObserver
    participant Context as ContextDocument
    
    User->>+Session: Start Session
    Session->>+FlowConfig: Load Configuration
    FlowConfig->>-Session: Configuration Loaded
    Session->>+Context: Load Context
    Context->>-Session: Context Loaded
    Session->>-User: Session Ready
    
    User->>+Message: Send Message
    Message->>Session: Store Message
    Message->>+Analysis: Analyze Message
    Analysis->>-Message: Analysis Complete
    Session->>+Observer: Update Metrics
    Observer->>-Session: Metrics Updated
    Session->>-User: Response
```

This comprehensive schema design supports the complex requirements of a conversation system with:
- Templates and custom configurations
- Multiple modalities (text, audio)
- Various purposes (interviews, counseling, assessment)
- Different AI roles (interviewer, counselor, tutor)
- Context-aware conversations
- Detailed message analysis
- Session observation and metrics 