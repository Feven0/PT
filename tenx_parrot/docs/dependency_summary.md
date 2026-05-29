# Dependency Injection Summary

## Overview

This document outlines the dependency injection structure and component relationships in the iPersona backend application. The dependency container manages the lifecycle and dependencies of all core components, infrastructure clients, repositories, and business services.

## Dependency Graph

```mermaid
flowchart LR
    %% Color definitions
    classDef configNode fill:#ffffff,stroke:#FF6B6B,stroke-width:2px,color:#000000
    classDef coreNode fill:#ffffff,stroke:#4CAF50,stroke-width:2px,color:#000000
    classDef infraNode fill:#ffffff,stroke:#2196F3,stroke-width:2px,color:#000000
    classDef repoNode fill:#ffffff,stroke:#9C27B0,stroke-width:2px,color:#000000
    classDef serviceNode fill:#ffffff,stroke:#FFC107,stroke-width:2px,color:#000000
    
    %% Main Config Node
    Config[AppConfig]:::configNode
    
    subgraph Core["Core Components"]
        Logger[BackendLogger]:::coreNode
        Metrics[MetricsCollector]:::coreNode
        Alert[AlertManager]:::coreNode
        Recovery[RecoveryManager]:::coreNode
        Cache[CacheManager]:::coreNode
    end
    
    subgraph Infra["Infrastructure"]
        Strapi[StrapiClient]:::infraNode
        Weaviate[WeaviateClient]:::infraNode
        Storage[StorageClient]:::infraNode
    end
    
    subgraph Repos["Repositories"]
        UserRepo[UserRepository]:::repoNode
        SessionRepo[SessionRepository]:::repoNode
        InterviewRepo[InterviewRepository]:::repoNode
    end
    
    subgraph Services["Business Services"]
        Chat[ChatService]:::serviceNode
        Interview[InterviewService]:::serviceNode
        StorageS[StorageService]:::serviceNode
        UIUX[UIUXService]:::serviceNode
        WebRTC[WebRTCService]:::serviceNode
        WebSocket[WebSocketService]:::serviceNode
        Analysis[AnalysisService]:::serviceNode
    end
    
    %% Core Dependencies
    Config --> Core
    Config --> Infra
    
    %% Infrastructure Dependencies
    Storage --> UserRepo
    Storage --> SessionRepo
    Storage --> InterviewRepo
    
    %% Service Dependencies
    UserRepo --> Chat
    Cache --> Chat
    Metrics --> Chat
    
    InterviewRepo --> Interview
    SessionRepo --> Interview
    Cache --> Interview
    Metrics --> Interview
    
    Strapi --> StorageS
    Weaviate --> StorageS
    Metrics --> StorageS
    
    Cache --> UIUX
    Metrics --> UIUX
    
    Cache --> WebRTC
    Metrics --> WebRTC
    
    Alert --> WebSocket
    SessionRepo --> WebSocket
    Metrics --> WebSocket
    
    StorageS --> Analysis
    Cache --> Analysis
    Metrics --> Analysis

    %% Style the subgraphs - transparent backgrounds
    style Core fill:none,stroke:#4CAF50,stroke-width:2px
    style Infra fill:none,stroke:#2196F3,stroke-width:2px
    style Repos fill:none,stroke:#9C27B0,stroke-width:2px
    style Services fill:none,stroke:#FFC107,stroke-width:2px
```