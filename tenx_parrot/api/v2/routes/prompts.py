"""Prompt management API routes."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from core.types.prompt import (
    PromptSet,
    LLMModelConfig,
    PromptType
)
from core.types.interview import InterviewFlow
from repositories.prompt import PromptRepository
from ..dependencies import get_prompt_repository

router = APIRouter(
    prefix="/prompts",
    tags=["prompts"]
)

# Request/Response Models
class PromptSetCreate(BaseModel):
    """Prompt set creation request."""
    name: str
    description: str
    system_prompt: str
    user_prompts: List[dict]
    interview_flow: Optional[InterviewFlow] = None
    llm_config: Optional[LLMModelConfig] = None
    metadata: Optional[dict] = None

class PromptSetUpdate(BaseModel):
    """Prompt set update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompts: Optional[List[dict]] = None
    interview_flow: Optional[InterviewFlow] = None
    llm_config: Optional[LLMModelConfig] = None
    metadata: Optional[dict] = None

class InterviewFlowCreate(BaseModel):
    """Interview flow creation request."""
    name: str
    description: str
    steps: List[dict]
    metadata: Optional[dict] = None

class InterviewFlowUpdate(BaseModel):
    """Interview flow update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[dict]] = None
    metadata: Optional[dict] = None

class LLMModelConfigUpdate(BaseModel):
    """Model configuration update request."""
    model_name: Optional[str] = None
    provider: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[dict] = None

# Endpoints
@router.post("/prompt-sets", response_model=PromptSet)
async def create_prompt_set(
    prompt_set: PromptSetCreate,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> PromptSet:
    """Create a new prompt set."""
    try:
        return await repo.create_prompt_set(
            name=prompt_set.name,
            description=prompt_set.description,
            system_prompt=prompt_set.system_prompt,
            user_prompts=prompt_set.user_prompts,
            interview_flow=prompt_set.interview_flow,
            llm_config=prompt_set.llm_config,
            metadata=prompt_set.metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create prompt set: {str(e)}"
        )

@router.get("/prompt-sets", response_model=List[PromptSet])
async def list_prompt_sets(
    limit: int = 100,
    offset: int = 0,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> List[PromptSet]:
    """List all prompt sets."""
    try:
        return await repo.list_prompt_sets(
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to list prompt sets: {str(e)}"
        )

@router.get("/prompt-sets/{prompt_set_id}", response_model=PromptSet)
async def get_prompt_set(
    prompt_set_id: str,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> PromptSet:
    """Get a specific prompt set."""
    prompt_set = await repo.get_prompt_set(prompt_set_id)
    if not prompt_set:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt set {prompt_set_id} not found"
        )
    return prompt_set

@router.put("/prompt-sets/{prompt_set_id}", response_model=PromptSet)
async def update_prompt_set(
    prompt_set_id: str,
    updates: PromptSetUpdate,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> PromptSet:
    """Update a prompt set."""
    try:
        # Convert to dict and remove None values
        update_data = updates.dict(exclude_unset=True)
        prompt_set = await repo.update_prompt_set(prompt_set_id, update_data)
        if not prompt_set:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt set {prompt_set_id} not found"
            )
        return prompt_set
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update prompt set: {str(e)}"
        )

@router.delete("/prompt-sets/{prompt_set_id}")
async def delete_prompt_set(
    prompt_set_id: str,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> dict:
    """Delete a prompt set."""
    success = await repo.delete_prompt_set(prompt_set_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt set {prompt_set_id} not found"
        )
    return {"status": "success", "message": "Prompt set deleted"}

@router.get("/prompt-sets/{prompt_set_id}/interview-flow", response_model=InterviewFlow)
async def get_interview_flow(
    prompt_set_id: str,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> InterviewFlow:
    """Get interview flow for a prompt set."""
    flow = await repo.get_interview_flow(prompt_set_id)
    if not flow:
        raise HTTPException(
            status_code=404,
            detail=f"Interview flow not found for prompt set {prompt_set_id}"
        )
    return flow

@router.put("/prompt-sets/{prompt_set_id}/interview-flow", response_model=InterviewFlow)
async def update_interview_flow(
    prompt_set_id: str,
    flow: InterviewFlowUpdate,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> InterviewFlow:
    """Update interview flow for a prompt set."""
    try:
        # Get existing flow
        existing_flow = await repo.get_interview_flow(prompt_set_id)
        if not existing_flow:
            raise HTTPException(
                status_code=404,
                detail=f"Interview flow not found for prompt set {prompt_set_id}"
            )
            
        # Update flow with new values
        update_data = flow.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_flow, key, value)
            
        # Save updated flow
        success = await repo.update_interview_flow(prompt_set_id, existing_flow)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to update interview flow"
            )
            
        return existing_flow
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update interview flow: {str(e)}"
        )

@router.get("/prompt-sets/{prompt_set_id}/model-config", response_model=LLMModelConfig)
async def get_llm_config(
    prompt_set_id: str,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> LLMModelConfig:
    """Get model configuration for a prompt set."""
    config = await repo.get_llm_config(prompt_set_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Model configuration not found for prompt set {prompt_set_id}"
        )
    return config

@router.put("/prompt-sets/{prompt_set_id}/model-config", response_model=LLMModelConfig)
async def update_llm_config(
    prompt_set_id: str,
    config: LLMModelConfigUpdate,
    repo: PromptRepository = Depends(get_prompt_repository)
) -> LLMModelConfig:
    """Update model configuration for a prompt set."""
    try:
        # Get existing config
        existing_config = await repo.get_llm_config(prompt_set_id)
        if not existing_config:
            raise HTTPException(
                status_code=404,
                detail=f"Model configuration not found for prompt set {prompt_set_id}"
            )
            
        # Update config with new values
        update_data = config.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_config, key, value)
            
        # Save updated config
        success = await repo.update_llm_config(prompt_set_id, existing_config)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to update model configuration"
            )
            
        return existing_config
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update model configuration: {str(e)}"
        ) 