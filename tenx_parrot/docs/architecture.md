# Backend Architecture

## Overview

The TenX iPersona backend is built on a modular architecture that emphasizes maintainability, scalability, and reliability. This document outlines the key architectural components and their interactions.

## Core Components

```mermaid
graph TD
    A[Application Core] --> B[Middleware Layer]
    A --> C[Service Layer]
    A --> D[Infrastructure Layer]
    A --> E[Data Layer]
    
    B --> B1[UnifiedMiddleware]
    B --> B2[Request Context]
    B --> B3[Error Handling]
    
    C --> C1[Interview Service]
    C --> C2[LLM Service]
    C --> C3[Speech Service]
    
    D --> D1[Storage Client]
    D --> D2[Cache Manager]
    D --> D3[Alert Manager]
    
    E --> E1[Redis Cache]
    E --> E2[Weaviate]
    E --> E3[Strapi CMS]
```

## Middleware Architecture

The middleware layer provides a unified approach to request processing and cross-cutting concerns:

```mermaid
graph LR
    A[Request] --> B[UnifiedMiddleware]
    B --> C[Context]
    C --> D[Validation]
    D --> E[Rate Limiting]
    E --> F[Authentication]
    F --> G[Handler]
    G --> H[Response]
```

### UnifiedMiddleware Features

1. **Request Context**
   - Request ID generation
   - Timing tracking
   - Correlation IDs
   - Request metadata

2. **Validation**
   - Content length checks
   - Content type validation
   - JSON schema validation
   - Field size limits

3. **Rate Limiting**
   - Request rate tracking
   - Quota enforcement
   - Client identification
   - Rate limit headers

4. **Authentication**
   - Token validation
   - Permission checks
   - Role-based access
   - Session management

5. **Error Handling**
   - Error standardization
   - Status code mapping
   - Error context
   - Recovery actions

## Service Layer

The service layer implements core business logic:

1. **Interview Service**
   - Interview flow management
   - Question generation
   - Response processing
   - State management

2. **LLM Service**
   - Model integration
   - Prompt management
   - Response generation
   - Context handling

3. **Speech Service**
   - Text-to-speech
   - Speech-to-text
   - Audio processing
   - Stream management

## Infrastructure Layer

The infrastructure layer provides core functionality:

1. **Storage Client**
   - Data persistence
   - Query handling
   - Circuit breaking
   - Connection pooling

2. **Cache Manager**
   - Data caching
   - TTL management
   - Cache invalidation
   - Cache statistics

3. **Alert Manager**
   - Alert generation
   - Severity tracking
   - Recovery actions
   - Alert history

## Data Layer

The data layer manages persistent storage:

1. **Redis Cache**
   - Fast data access
   - Session storage
   - Rate limiting
   - Pub/sub messaging

2. **Weaviate**
   - Vector storage
   - Semantic search
   - Data indexing
   - Query optimization

3. **Strapi CMS**
   - Content management
   - API generation
   - Data modeling
   - Access control

## Error Handling

The application implements a standardized error handling approach:

```mermaid
graph TD
    A[Error] --> B{Error Type}
    B --> C[Application]
    B --> D[Validation]
    B --> E[Authentication]
    B --> F[Service]
    
    C --> G[Handler]
    D --> G
    E --> G
    F --> G
    
    G --> H[Response]
    G --> I[Logging]
    G --> J[Metrics]
```

## Resource Management

The application ensures proper resource management:

1. **Connection Pooling**
   - Database connections
   - HTTP clients
   - Cache connections
   - Service clients

2. **Cleanup Procedures**
   - Request cleanup
   - Cache invalidation
   - File cleanup
   - Memory management

3. **Health Monitoring**
   - Service health
   - Resource usage
   - Error rates
   - Performance metrics 