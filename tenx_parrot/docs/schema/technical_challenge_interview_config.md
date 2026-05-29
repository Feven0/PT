# Technical Challenge Interview Flow Configuration

This document contains the complete configuration for the Technical Challenge Interview Flow, which is designed to interview users based on their challenge submissions. The flow analyzes the user's submission and generates relevant questions to assess their understanding and implementation.

## 1. Conversation Purpose

```json
{
  "id": "challenge_interview_purpose",
  "name": "Challenge-Based Interview",
  "description": "Interview users based on their challenge submissions to assess understanding and implementation",
  "evaluation_metrics": {
    "technical_understanding": {
      "weight": 0.4,
      "threshold": 0.7,
      "components": [
        {
          "name": "concept_grasp",
          "weight": 0.4,
          "threshold": 0.7,
          "description": "Understanding of core concepts and principles"
        },
        {
          "name": "implementation_understanding",
          "weight": 0.3,
          "threshold": 0.7,
          "description": "Understanding of implementation details and choices"
        },
        {
          "name": "problem_solving",
          "weight": 0.3,
          "threshold": 0.7,
          "description": "Ability to solve problems and make tradeoffs"
        }
      ]
    },
    "communication": {
      "weight": 0.3,
      "threshold": 0.6,
      "components": [
        {
          "name": "clarity",
          "weight": 0.5,
          "threshold": 0.6,
          "description": "Clear and concise explanation of ideas"
        },
        {
          "name": "technical_depth",
          "weight": 0.5,
          "threshold": 0.6,
          "description": "Appropriate level of technical detail"
        }
      ]
    },
    "practical_application": {
      "weight": 0.3,
      "threshold": 0.7,
      "components": [
        {
          "name": "code_quality",
          "weight": 0.4,
          "threshold": 0.7,
          "description": "Code quality and best practices"
        },
        {
          "name": "best_practices",
          "weight": 0.3,
          "threshold": 0.7,
          "description": "Following industry best practices"
        },
        {
          "name": "scalability",
          "weight": 0.3,
          "threshold": 0.7,
          "description": "Consideration of scalability aspects"
        }
      ]
    }
  },
  "success_criteria": {
    "minimum_score": 0.7,
    "required_components": ["technical_understanding", "communication", "practical_application"],
    "time_constraints": {
      "max_duration": 3600,
      "warning_threshold": 3000
    }
  },
  "context_requirements": {
    "required_documents": ["challenge_description", "user_submission"],
    "optional_documents": ["reference_solutions", "learning_outcomes"],
    "document_validation": {
      "challenge_description": {
        "required_sections": ["overview", "requirements", "learning_outcomes"],
        "format": "markdown"
      },
      "user_submission": {
        "required_elements": ["code", "documentation"],
        "format": "mixed"
      }
    }
  }
}
```

## 2. AI Role Configuration

```json
{
  "id": "challenge_interviewer",
  "name": "Challenge Interviewer",
  "description": "AI interviewer specialized in conducting technical interviews based on challenge submissions",
  "behavior_configuration": {
    "role_type": "interviewer",
    "interaction_style": "professional",
    "response_patterns": {
      "questioning": {
        "style": "probing",
        "depth": "adaptive",
        "frequency": "balanced"
      },
      "feedback": {
        "style": "constructive",
        "focus": "improvement",
        "tone": "supportive"
      },
      "guidance": {
        "level": "minimal",
        "type": "hints",
        "frequency": "sparse"
      }
    },
    "adaptation_rules": {
      "difficulty_adjustment": {
        "based_on": "response_quality",
        "range": ["easy", "medium", "hard"],
        "sensitivity": 0.7
      },
      "hint_provision": {
        "strategy": "progressive",
        "max_hints": 3,
        "delay": 120
      },
      "time_management": {
        "strictness": "high",
        "warnings": [300, 60],
        "grace_period": 30
      }
    }
  },
  "personality_traits": {
    "professionalism": 0.9,
    "technical_expertise": 0.95,
    "empathy": 0.7,
    "patience": 0.8,
    "adaptability": 0.85
  },
  "knowledge_base": {
    "domains": ["software_development", "system_design", "algorithms"],
    "depth": "expert",
    "specializations": ["backend_development", "cloud_architecture"],
    "update_frequency": "weekly"
  },
  "expertise_areas": {
    "primary": ["system_design", "algorithms"],
    "secondary": ["software_architecture", "performance_optimization"],
    "tertiary": ["testing", "documentation"]
  },
  "interaction_style": {
    "tone": "professional",
    "formality": "high",
    "technical_level": "adaptive",
    "feedback_style": "detailed",
    "language_preference": "technical"
  }
}
```

## 3. Conversation Modality

```json
{
  "id": "challenge_interview_modality",
  "name": "Challenge Interview",
  "description": "Modality for conducting technical interviews based on challenge submissions",
  "supported_media_types": {
    "text": {
      "formats": ["plain", "markdown", "code"],
      "max_length": 5000,
      "allowed_attachments": ["code_snippets", "diagrams"],
      "validation_rules": {
        "markdown": true,
        "code_blocks": true,
        "links": true
      }
    },
    "code": {
      "languages": ["python", "java", "javascript"],
      "max_file_size": 100000,
      "validation_rules": {
        "syntax_check": true,
        "style_check": true,
        "complexity_limit": 20
      }
    },
    "diagrams": {
      "formats": ["mermaid", "plantuml"],
      "max_size": 50000,
      "validation_rules": {
        "syntax_check": true,
        "complexity_limit": 15
      }
    }
  },
  "interaction_rules": {
    "turn_based": true,
    "time_limits": {
      "per_turn": 300,
      "total": 3600,
      "extensions": {
        "allowed": true,
        "max_extensions": 2,
        "extension_duration": 300
      }
    },
    "content_validation": {
      "code_submission": {
        "required": true,
        "validation_level": "strict"
      },
      "diagram_submission": {
        "required": false,
        "validation_level": "moderate"
      },
      "text_explanation": {
        "required": true,
        "min_length": 50,
        "max_length": 2000
      }
    },
    "interaction_flow": {
      "max_questions": 5,
      "min_questions": 3,
      "question_types": ["concept", "implementation", "problem_solving"],
      "follow_up_allowed": true
    }
  }
}
```

## 4. Flow Configuration Components

### 4.1 Context Analyzer Component

```json
{
  "id": "context_analyzer_1",
  "name": "Challenge Context Analyzer",
  "component_type": "analyzer",
  "configuration": {
    "analysis_types": {
      "submission_quality": {
        "metrics": ["code_quality", "documentation", "completeness"],
        "weights": [0.4, 0.3, 0.3],
        "thresholds": {
          "code_quality": 0.7,
          "documentation": 0.6,
          "completeness": 0.8
        }
      },
      "technical_depth": {
        "metrics": ["complexity", "innovation", "best_practices"],
        "weights": [0.4, 0.3, 0.3],
        "thresholds": {
          "complexity": 0.7,
          "innovation": 0.6,
          "best_practices": 0.7
        }
      }
    },
    "context_extraction": {
      "challenge_description": {
        "extract": ["learning_outcomes", "requirements", "constraints"],
        "format": "structured"
      },
      "user_submission": {
        "extract": ["implementation_details", "design_choices", "tradeoffs"],
        "format": "structured"
      }
    },
    "output_format": {
      "type": "structured",
      "sections": ["summary", "strengths", "weaknesses", "question_areas"]
    }
  }
}
```

### 4.2 Question Generator Component

```json
{
  "id": "question_generator_1",
  "name": "Challenge Question Generator",
  "component_type": "generator",
  "configuration": {
    "generation_parameters": {
      "temperature": 0.7,
      "max_tokens": 500,
      "top_p": 0.9,
      "frequency_penalty": 0.5,
      "presence_penalty": 0.5
    },
    "question_types": {
      "concept_understanding": {
        "weight": 0.3,
        "difficulty_levels": ["easy", "medium", "hard"],
        "focus_areas": ["core_concepts", "implementation_details"],
        "time_limit": 300,
        "validation": {
          "clarity": 0.8,
          "relevance": 0.9,
          "technical_depth": 0.7
        }
      },
      "implementation_analysis": {
        "weight": 0.4,
        "difficulty_levels": ["easy", "medium", "hard"],
        "focus_areas": ["code_quality", "design_choices"],
        "time_limit": 600,
        "validation": {
          "specificity": 0.8,
          "technical_accuracy": 0.9,
          "relevance": 0.8
        }
      },
      "problem_solving": {
        "weight": 0.3,
        "difficulty_levels": ["easy", "medium", "hard"],
        "focus_areas": ["optimization", "tradeoffs"],
        "time_limit": 600,
        "validation": {
          "complexity": 0.7,
          "relevance": 0.8,
          "solvability": 0.8
        }
      }
    },
    "context_usage": {
      "challenge_description": {
        "required": true,
        "usage": ["learning_outcomes", "evaluation_criteria"],
        "weight": 0.4
      },
      "user_submission": {
        "required": true,
        "usage": ["implementation_details", "design_choices"],
        "weight": 0.4
      },
      "analysis_results": {
        "required": true,
        "usage": ["question_areas", "difficulty_adjustment"],
        "weight": 0.2
      }
    },
    "question_distribution": {
      "total_questions": {
        "min": 3,
        "max": 5,
        "default": 4
      },
      "type_mix": {
        "concept_understanding": {
          "min": 1,
          "max": 2,
          "default": 1
        },
        "implementation_analysis": {
          "min": 1,
          "max": 2,
          "default": 2
        },
        "problem_solving": {
          "min": 1,
          "max": 2,
          "default": 1
        }
      },
      "difficulty_progression": {
        "start": "medium",
        "progression": "adaptive",
        "based_on": ["response_quality", "time_taken"],
        "adjustment_sensitivity": 0.7
      }
    },
    "question_ordering": {
      "strategy": "mixed",
      "rules": [
        "start_with_concept_questions",
        "alternate_question_types",
        "adapt_based_on_performance",
        "maintain_engagement"
      ],
      "constraints": {
        "max_similar_type": 2,
        "min_type_variety": 2,
        "difficulty_spacing": "gradual"
      }
    }
  }
}
```

### 4.3 Evaluator Component

```json
{
  "id": "evaluator_1",
  "name": "Challenge Response Evaluator",
  "component_type": "evaluator",
  "configuration": {
    "evaluation_metrics": {
      "technical_understanding": {
        "weight": 0.4,
        "components": [
          {
            "name": "concept_grasp",
            "weight": 0.4,
            "evaluation_criteria": {
              "accuracy": 0.7,
              "depth": 0.7,
              "relevance": 0.8
            }
          },
          {
            "name": "implementation_understanding",
            "weight": 0.3,
            "evaluation_criteria": {
              "correctness": 0.8,
              "completeness": 0.7,
              "efficiency": 0.7
            }
          },
          {
            "name": "problem_solving",
            "weight": 0.3,
            "evaluation_criteria": {
              "approach": 0.7,
              "solution_quality": 0.8,
              "optimization": 0.7
            }
          }
        ]
      },
      "communication": {
        "weight": 0.3,
        "components": [
          {
            "name": "clarity",
            "weight": 0.5,
            "evaluation_criteria": {
              "organization": 0.7,
              "precision": 0.8,
              "conciseness": 0.7
            }
          },
          {
            "name": "technical_depth",
            "weight": 0.5,
            "evaluation_criteria": {
              "terminology": 0.8,
              "explanation_depth": 0.7,
              "relevance": 0.8
            }
          }
        ]
      },
      "practical_application": {
        "weight": 0.3,
        "components": [
          {
            "name": "code_quality",
            "weight": 0.4,
            "evaluation_criteria": {
              "readability": 0.8,
              "maintainability": 0.7,
              "efficiency": 0.7
            }
          },
          {
            "name": "best_practices",
            "weight": 0.3,
            "evaluation_criteria": {
              "standards_compliance": 0.8,
              "design_patterns": 0.7,
              "error_handling": 0.7
            }
          },
          {
            "name": "scalability",
            "weight": 0.3,
            "evaluation_criteria": {
              "performance": 0.7,
              "resource_usage": 0.7,
              "extensibility": 0.8
            }
          }
        ]
      }
    },
    "scoring_rules": {
      "aggregation_method": "weighted_sum",
      "normalization": "min_max",
      "rounding": 2,
      "thresholds": {
        "pass": 0.7,
        "warning": 0.6,
        "fail": 0.5
      }
    },
    "feedback_generation": {
      "style": "constructive",
      "focus_areas": ["strengths", "improvements"],
      "technical_depth": "detailed",
      "format": "structured",
      "sections": [
        "overview",
        "technical_analysis",
        "suggestions",
        "next_steps"
      ]
    }
  }
}
```

## 5. Flow Configuration

```json
{
  "id": "challenge_interview_flow_1",
  "name": "Challenge-Based Interview Flow",
  "description": "Flow for interviewing users based on their challenge submissions",
  "is_template": true,
  "manager_class": "ChallengeInterviewManager",
  "purpose_id": "challenge_interview_purpose",
  "ai_role_id": "challenge_interviewer",
  "modality_id": "challenge_interview_modality",
  "flow_steps": {
    "steps": [
      {
        "id": "intro",
        "type": "message",
        "content": "Welcome to your challenge-based interview. I'll ask you questions about your submission and the concepts involved.",
        "next_step": "context_analysis",
        "conditions": {
          "required_context": ["challenge_description", "user_submission"]
        },
        "metadata": {
          "format": "markdown",
          "variables": ["user_name", "challenge_name"]
        }
      },
      {
        "id": "context_analysis",
        "type": "analysis",
        "component_refs": ["context_analyzer_1"],
        "next_step": "question_generation",
        "analysis_rules": {
          "metrics": ["submission_quality", "technical_depth"],
          "thresholds": {
            "submission_quality": 0.6,
            "technical_depth": 0.6
          }
        },
        "timeout": 300
      },
      {
        "id": "question_generation",
        "type": "dynamic_generation",
        "component_refs": ["question_generator_1"],
        "next_step": "user_response",
        "generation_rules": {
          "type": "question",
          "context_sources": ["challenge_description", "user_submission", "analysis_results"],
          "parameters": {
            "temperature": 0.7,
            "max_tokens": 500
          }
        },
        "timeout": 300
      },
      {
        "id": "user_response",
        "type": "input",
        "validation": {
          "type": "mixed",
          "text": {
            "min_length": 50,
            "max_length": 2000
          },
          "code": {
            "languages": ["python", "java", "javascript"],
            "max_file_size": 100000
          }
        },
        "next_step": "evaluation",
        "fallback": "timeout_handling",
        "retry_attempts": 2,
        "timeout": 600
      },
      {
        "id": "evaluation",
        "type": "analysis",
        "component_refs": ["evaluator_1"],
        "next_step": "feedback",
        "analysis_rules": {
          "metrics": ["technical_understanding", "communication", "practical_application"],
          "thresholds": {
            "technical_understanding": 0.7,
            "communication": 0.6,
            "practical_application": 0.7
          }
        },
        "timeout": 300
      },
      {
        "id": "feedback",
        "type": "feedback",
        "component_refs": ["evaluator_1"],
        "next_step": "decision",
        "feedback_rules": {
          "style": "constructive",
          "focus_areas": ["strengths", "improvements"],
          "technical_depth": "detailed"
        },
        "timeout": 300
      },
      {
        "id": "decision",
        "type": "decision",
        "conditions": [
          {
            "metric": "technical_understanding",
            "operator": ">=",
            "value": 0.7,
            "next_step": "next_question"
          },
          {
            "metric": "technical_understanding",
            "operator": "<",
            "value": 0.7,
            "next_step": "clarification"
          }
        ],
        "default_step": "completion",
        "timeout": 60
      },
      {
        "id": "clarification",
        "type": "dynamic_generation",
        "component_refs": ["question_generator_1"],
        "next_step": "user_response",
        "generation_rules": {
          "type": "clarification",
          "context_sources": ["user_response", "evaluation_results"],
          "parameters": {
            "temperature": 0.7,
            "max_tokens": 300
          }
        },
        "timeout": 300
      },
      {
        "id": "next_question",
        "type": "decision",
        "conditions": [
          {
            "metric": "questions_asked",
            "operator": "<",
            "value": 5,
            "next_step": "question_generation"
          }
        ],
        "default_step": "completion",
        "timeout": 60
      }
    ],
    "transitions": {
      "intro": ["context_analysis"],
      "context_analysis": ["question_generation"],
      "question_generation": ["user_response"],
      "user_response": ["evaluation", "timeout_handling"],
      "evaluation": ["feedback"],
      "feedback": ["decision"],
      "decision": ["next_question", "clarification", "completion"],
      "clarification": ["user_response"],
      "next_question": ["question_generation", "completion"]
    },
    "timeout_handling": {
      "max_attempts": 2,
      "grace_period": 300,
      "fallback_action": "proceed_to_evaluation",
      "notifications": {
        "warning_threshold": 60,
        "final_warning": 30
      }
    }
  }
}
```

## 6. Context Documents

### 6.1 Challenge Description

```json
{
  "id": "challenge_description_1",
  "type": "challenge_description",
  "content": {
    "title": "System Design Challenge: Scalable Web Service",
    "overview": "Design and implement a scalable web service for handling user authentication and profile management.",
    "requirements": [
      "Implement user registration and login functionality",
      "Design a scalable database schema",
      "Implement proper security measures",
      "Handle concurrent user access",
      "Provide API documentation"
    ],
    "learning_outcomes": [
      "Understanding of scalable system design",
      "Knowledge of authentication best practices",
      "Experience with concurrent programming",
      "Ability to design efficient database schemas"
    ],
    "constraints": [
      "Must use Python or Java",
      "Must implement proper error handling",
      "Must include unit tests",
      "Must document design decisions"
    ],
    "evaluation_criteria": {
      "technical": {
        "weight": 0.6,
        "components": ["scalability", "security", "performance"]
      },
      "documentation": {
        "weight": 0.2,
        "components": ["clarity", "completeness"]
      },
      "code_quality": {
        "weight": 0.2,
        "components": ["readability", "maintainability"]
      }
    }
  },
  "metadata": {
    "difficulty": "intermediate",
    "estimated_time": "4-6 hours",
    "required_skills": ["system_design", "backend_development", "database_design"],
    "tags": ["scalability", "authentication", "concurrency"]
  }
}
```

### 6.2 User Submission

```json
{
  "id": "user_submission_1",
  "type": "user_submission",
  "content": {
    "implementation": {
      "language": "Python",
      "framework": "FastAPI",
      "database": "PostgreSQL",
      "architecture": "Microservices",
      "key_components": [
        "Authentication Service",
        "User Profile Service",
        "Database Service"
      ]
    },
    "code_quality": {
      "testing_coverage": 0.85,
      "documentation": "comprehensive",
      "error_handling": "robust"
    },
    "design_decisions": [
      {
        "aspect": "Database Schema",
        "decision": "Used PostgreSQL with proper indexing",
        "rationale": "Better for complex queries and data integrity"
      },
      {
        "aspect": "Authentication",
        "decision": "Implemented JWT with refresh tokens",
        "rationale": "Stateless and scalable approach"
      }
    ],
    "tradeoffs": [
      {
        "aspect": "Scalability",
        "tradeoff": "Chose eventual consistency over strong consistency",
        "rationale": "Better performance for high concurrency"
      }
    ]
  },
  "metadata": {
    "submission_time": "2024-03-15T14:30:00Z",
    "time_taken": "5 hours",
    "tools_used": ["VS Code", "Postman", "pgAdmin"],
    "version": "1.0.0"
  }
}
```

## Implementation Notes

1. **Flow Execution**:
   - The flow starts with context analysis of the user's submission
   - Questions are generated based on the submission and challenge context
   - Each response is evaluated against multiple metrics
   - The flow adapts based on user performance

2. **Component Interaction**:
   - Context Analyzer processes the submission and challenge
   - Question Generator creates relevant questions
   - Evaluator assesses responses and provides feedback
   - Components share context through the flow configuration

3. **Evaluation Process**:
   - Technical understanding is weighted highest (0.4)
   - Communication and practical application are equally weighted (0.3 each)
   - Each metric has specific components and thresholds
   - Feedback is generated based on evaluation results

4. **Adaptation Rules**:
   - Question difficulty adjusts based on response quality
   - Clarification is provided when understanding is below threshold
   - Flow progresses based on evaluation metrics
   - Timeouts are handled gracefully with retry options

5. **Context Management**:
   - Challenge description provides learning outcomes and requirements
   - User submission contains implementation details
   - Context is shared between components
   - Analysis results influence question generation

## Key Design Considerations

1. **Flexibility**:
   - Components can be swapped or modified
   - Metrics and thresholds are configurable
   - Question types and distribution are adjustable
   - Time limits can be modified per step

2. **Scalability**:
   - Components are independent and reusable
   - Flow can handle different types of challenges
   - Evaluation metrics can be extended
   - Context management is modular

3. **Maintainability**:
   - Clear separation of concerns
   - Well-defined interfaces between components
   - Comprehensive documentation
   - Modular configuration

4. **User Experience**:
   - Adaptive difficulty levels
   - Constructive feedback
   - Clear progression
   - Graceful timeout handling 