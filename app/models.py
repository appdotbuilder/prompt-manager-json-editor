from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class PromptCategory(SQLModel, table=True):
    __tablename__ = "prompt_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(default="", max_length=500)
    color: str = Field(default="#3B82F6", max_length=7)  # Hex color code
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    prompts: List["Prompt"] = Relationship(back_populates="category")


class Prompt(SQLModel, table=True):
    __tablename__ = "prompts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    content: str = Field(max_length=10000)  # The actual prompt text
    version: str = Field(default="1.0.0", max_length=20)
    is_active: bool = Field(default=True)
    is_template: bool = Field(default=False)  # Whether this prompt uses variables
    usage_count: int = Field(default=0)
    rating: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=3)  # 0.00 to 5.00

    # JSON configurations
    variables: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Template variables
    settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Model settings, temperature, etc.
    prompt_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Additional metadata
    tags: List[str] = Field(default=[], sa_column=Column(JSON))

    # Foreign keys
    category_id: Optional[int] = Field(default=None, foreign_key="prompt_categories.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)

    # Relationships
    category: Optional[PromptCategory] = Relationship(back_populates="prompts")
    executions: List["PromptExecution"] = Relationship(back_populates="prompt")


class PromptExecution(SQLModel, table=True):
    __tablename__ = "prompt_executions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompts.id")

    # Input/Output data
    input_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Variables used
    output_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Generated response

    # Execution details
    model_name: str = Field(default="", max_length=100)
    model_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    execution_time_ms: Optional[int] = Field(default=None)
    token_count: Optional[int] = Field(default=None)
    cost: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)

    # Status and feedback
    status: str = Field(default="completed", max_length=50)  # completed, failed, cancelled
    error_message: Optional[str] = Field(default=None, max_length=1000)
    user_rating: Optional[int] = Field(default=None, ge=1, le=5)
    user_feedback: Optional[str] = Field(default=None, max_length=2000)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    prompt: Prompt = Relationship(back_populates="executions")


# Non-persistent schemas (for validation, forms, API requests/responses)
class PromptCategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    color: str = Field(default="#3B82F6", max_length=7)


class PromptCategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default=None, max_length=7)


class PromptCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    content: str = Field(max_length=10000)
    version: str = Field(default="1.0.0", max_length=20)
    is_template: bool = Field(default=False)
    variables: Dict[str, Any] = Field(default={})
    settings: Dict[str, Any] = Field(default={})
    prompt_metadata: Dict[str, Any] = Field(default={})
    tags: List[str] = Field(default=[])
    category_id: Optional[int] = Field(default=None)


class PromptUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content: Optional[str] = Field(default=None, max_length=10000)
    version: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)
    is_template: Optional[bool] = Field(default=None)
    rating: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=3)
    variables: Optional[Dict[str, Any]] = Field(default=None)
    settings: Optional[Dict[str, Any]] = Field(default=None)
    prompt_metadata: Optional[Dict[str, Any]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class PromptExecutionCreate(SQLModel, table=False):
    prompt_id: int
    input_data: Dict[str, Any] = Field(default={})
    model_name: str = Field(default="", max_length=100)
    model_settings: Dict[str, Any] = Field(default={})


class PromptExecutionUpdate(SQLModel, table=False):
    output_data: Optional[Dict[str, Any]] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None)
    token_count: Optional[int] = Field(default=None)
    cost: Optional[Decimal] = Field(default=None, decimal_places=6, max_digits=10)
    status: Optional[str] = Field(default=None, max_length=50)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    user_rating: Optional[int] = Field(default=None, ge=1, le=5)
    user_feedback: Optional[str] = Field(default=None, max_length=2000)
    completed_at: Optional[datetime] = Field(default=None)


# Helper schemas for JSON editor and form handling
class PromptVariableDefinition(SQLModel, table=False):
    name: str = Field(max_length=100)
    type: str = Field(max_length=50)  # string, number, boolean, array, object
    description: str = Field(default="", max_length=500)
    default_value: Optional[Any] = Field(default=None)
    required: bool = Field(default=False)
    validation_rules: Dict[str, Any] = Field(default={})


class ModelSettings(SQLModel, table=False):
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    stop_sequences: List[str] = Field(default=[])
    system_message: Optional[str] = Field(default=None, max_length=2000)


class PromptStats(SQLModel, table=False):
    total_prompts: int
    active_prompts: int
    template_prompts: int
    total_executions: int
    avg_rating: Optional[Decimal]
    most_used_category: Optional[str]
    recent_executions: int  # Last 7 days
