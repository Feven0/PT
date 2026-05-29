# Testing Components Guide

## Overview

The testing components provide a comprehensive framework for testing the backend system at various levels, including unit tests, integration tests, performance tests, and end-to-end tests. These components ensure code quality, reliability, and performance.

## Architecture

```mermaid
graph TB
    Tests[Test Suite] --> Unit[Unit Tests]
    Tests --> Integration[Integration Tests]
    Tests --> Performance[Performance Tests]
    Tests --> E2E[End-to-End Tests]
    
    subgraph Test Layer
        Unit
        Integration
        Performance
        E2E
        Fixtures[Test Fixtures]
        Mocks[Mock Objects]
    end
    
    subgraph Tools
        Runner[Test Runner]
        Coverage[Coverage Tool]
        Report[Report Generator]
    end
    
    subgraph Resources
        Database[Test Database]
        Cache[Test Cache]
        Queue[Test Queue]
    end
```

## Components

### 1. Test Configuration

Configuration for test environment and resources.

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os

class TestConfig(BaseModel):
    """Test configuration."""
    
    # Database settings
    database_url: str = Field(
        default="postgresql://test:test@localhost:5432/test_db",
        description="Test database URL"
    )
    
    # Cache settings
    cache_url: str = Field(
        default="redis://localhost:6379/1",
        description="Test cache URL"
    )
    
    # Queue settings
    queue_url: str = Field(
        default="memory://",
        description="Test queue URL"
    )
    
    # API settings
    api_url: str = Field(
        default="http://localhost:8000",
        description="Test API URL"
    )
    
    # External service mocks
    mock_openai: bool = Field(
        default=True,
        description="Mock OpenAI service"
    )
    mock_assembly_ai: bool = Field(
        default=True,
        description="Mock AssemblyAI service"
    )
    mock_strapi: bool = Field(
        default=True,
        description="Mock Strapi service"
    )
    
    # Test data
    test_data_path: str = Field(
        default="tests/data",
        description="Path to test data files"
    )
    
    @classmethod
    def from_env(cls) -> "TestConfig":
        """Create config from environment variables."""
        return cls(
            database_url=os.getenv(
                "TEST_DATABASE_URL",
                cls.__fields__["database_url"].default
            ),
            cache_url=os.getenv(
                "TEST_CACHE_URL",
                cls.__fields__["cache_url"].default
            ),
            queue_url=os.getenv(
                "TEST_QUEUE_URL",
                cls.__fields__["queue_url"].default
            ),
            api_url=os.getenv(
                "TEST_API_URL",
                cls.__fields__["api_url"].default
            )
        )
```

### 2. Test Fixtures

Pytest fixtures for test resources.

```python
import pytest
import asyncio
from typing import AsyncGenerator, Generator
import aioredis
import asyncpg

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_config() -> TestConfig:
    """Get test configuration."""
    return TestConfig.from_env()

@pytest.fixture(scope="session")
async def database_pool(
    test_config: TestConfig
) -> AsyncGenerator[asyncpg.Pool, None]:
    """Create database connection pool."""
    # Create pool
    pool = await asyncpg.create_pool(
        test_config.database_url,
        min_size=1,
        max_size=5
    )
    
    try:
        # Initialize schema
        async with pool.acquire() as conn:
            with open("tests/schema.sql") as f:
                await conn.execute(f.read())
                
        yield pool
        
    finally:
        await pool.close()

@pytest.fixture(scope="session")
async def redis_client(
    test_config: TestConfig
) -> AsyncGenerator[aioredis.Redis, None]:
    """Create Redis client."""
    client = await aioredis.create_redis_pool(
        test_config.cache_url
    )
    
    try:
        yield client
    finally:
        client.close()
        await client.wait_closed()

@pytest.fixture(scope="session")
async def test_app(
    test_config: TestConfig,
    database_pool: asyncpg.Pool,
    redis_client: aioredis.Redis
) -> FastAPI:
    """Create test application."""
    # Create container
    container = Container()
    
    # Configure container
    container.config.from_dict({
        "database": {
            "url": test_config.database_url
        },
        "cache": {
            "url": test_config.cache_url
        },
        "queue": {
            "url": test_config.queue_url
        }
    })
    
    # Create app
    app = create_app(container)
    
    # Configure test client
    app.dependency_overrides[get_db_pool] = lambda: database_pool
    app.dependency_overrides[get_redis_client] = lambda: redis_client
    
    return app

@pytest.fixture(scope="function")
async def test_client(
    test_app: FastAPI
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        app=test_app,
        base_url="http://test"
    ) as client:
        yield client
```

### 3. Mock Objects

Mock implementations for external services.

```python
class MockOpenAIClient:
    """Mock OpenAI client."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._responses: Dict[str, str] = {}
        
    def add_response(self, prompt: str, response: str) -> None:
        """Add mock response."""
        self._responses[prompt] = response
        
    async def generate_text(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """Generate mock text response."""
        if prompt in self._responses:
            return self._responses[prompt]
            
        # Generate deterministic response
        return f"Mock response for: {prompt}"

class MockAssemblyAIClient:
    """Mock AssemblyAI client."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._transcripts: Dict[str, str] = {}
        
    def add_transcript(
        self,
        audio_url: str,
        transcript: str
    ) -> None:
        """Add mock transcript."""
        self._transcripts[audio_url] = transcript
        
    async def transcribe_audio(
        self,
        audio_url: str,
        **kwargs: Any
    ) -> str:
        """Generate mock transcript."""
        if audio_url in self._transcripts:
            return self._transcripts[audio_url]
            
        # Generate deterministic transcript
        return f"Mock transcript for: {audio_url}"

class MockStrapiClient:
    """Mock Strapi client."""
    
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._data: Dict[str, Dict[str, Any]] = {}
        
    def add_data(
        self,
        collection: str,
        id: str,
        data: Dict[str, Any]
    ) -> None:
        """Add mock data."""
        if collection not in self._data:
            self._data[collection] = {}
        self._data[collection][id] = data
        
    async def get_entry(
        self,
        collection: str,
        id: str
    ) -> Optional[Dict[str, Any]]:
        """Get mock entry."""
        return self._data.get(collection, {}).get(id)
        
    async def create_entry(
        self,
        collection: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create mock entry."""
        id = str(uuid.uuid4())
        entry = {"id": id, **data}
        
        if collection not in self._data:
            self._data[collection] = {}
        self._data[collection][id] = entry
        
        return entry
```

### 4. Test Cases

Example test implementations.

```python
class TestInterviewService:
    """Test interview service."""
    
    @pytest.fixture(scope="class")
    def mock_openai(self) -> MockOpenAIClient:
        """Create mock OpenAI client."""
        client = MockOpenAIClient({})
        client.add_response(
            "Analyze interview response: Test answer",
            "Mock analysis: Positive response"
        )
        return client
        
    @pytest.fixture(scope="class")
    def mock_assembly_ai(self) -> MockAssemblyAIClient:
        """Create mock AssemblyAI client."""
        client = MockAssemblyAIClient({})
        client.add_transcript(
            "test.wav",
            "Mock transcript: Test answer"
        )
        return client
        
    @pytest.mark.asyncio
    async def test_create_interview(
        self,
        database_pool: asyncpg.Pool,
        redis_client: aioredis.Redis,
        mock_openai: MockOpenAIClient,
        mock_assembly_ai: MockAssemblyAIClient
    ):
        """Test interview creation."""
        # Create service
        service = InterviewService(
            database=DatabaseService(database_pool),
            cache=CacheService(redis_client),
            openai=mock_openai,
            assembly_ai=mock_assembly_ai,
            metrics=MockMetricsCollector(),
            logger=MockLogger()
        )
        
        # Create interview
        interview = await service.create_interview(
            user_id=uuid.uuid4(),
            questions=["Test question"],
            language="en"
        )
        
        # Verify interview
        assert interview.id is not None
        assert interview.status == "created"
        assert len(interview.questions) == 1
        
    @pytest.mark.asyncio
    async def test_process_answer(
        self,
        database_pool: asyncpg.Pool,
        redis_client: aioredis.Redis,
        mock_openai: MockOpenAIClient,
        mock_assembly_ai: MockAssemblyAIClient
    ):
        """Test answer processing."""
        # Create service
        service = InterviewService(
            database=DatabaseService(database_pool),
            cache=CacheService(redis_client),
            openai=mock_openai,
            assembly_ai=mock_assembly_ai,
            metrics=MockMetricsCollector(),
            logger=MockLogger()
        )
        
        # Create interview
        interview = await service.create_interview(
            user_id=uuid.uuid4(),
            questions=["Test question"],
            language="en"
        )
        
        # Process answer
        result = await service.process_answer(
            interview_id=interview.id,
            question_index=0,
            audio_url="test.wav"
        )
        
        # Verify result
        assert result.answer == "Mock transcript: Test answer"
        assert result.analysis == "Mock analysis: Positive response"
```

### 5. Performance Tests

Load and stress testing implementations.

```python
class TestPerformance:
    """Performance test suite."""
    
    @pytest.mark.performance
    async def test_interview_creation_load(
        self,
        test_client: AsyncClient
    ):
        """Test interview creation under load."""
        # Configure test
        num_requests = 100
        concurrent_requests = 10
        
        # Create tasks
        tasks = []
        for _ in range(num_requests):
            task = asyncio.create_task(
                self._create_interview(test_client)
            )
            tasks.append(task)
            
            if len(tasks) >= concurrent_requests:
                # Wait for batch to complete
                await asyncio.gather(*tasks)
                tasks = []
                
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
            
    async def _create_interview(
        self,
        client: AsyncClient
    ) -> None:
        """Create interview and measure performance."""
        start_time = time.time()
        
        # Send request
        response = await client.post(
            "/api/interviews",
            json={
                "user_id": str(uuid.uuid4()),
                "questions": ["Test question"],
                "language": "en"
            }
        )
        
        # Record metrics
        duration = time.time() - start_time
        assert response.status_code == 201
        assert duration < 0.5  # Max 500ms
        
    @pytest.mark.performance
    async def test_cache_performance(
        self,
        redis_client: aioredis.Redis
    ):
        """Test cache performance."""
        # Configure test
        num_operations = 1000
        key_prefix = "test:perf"
        value_size = 1024  # 1KB
        
        # Generate test data
        test_data = "x" * value_size
        
        # Measure set performance
        start_time = time.time()
        for i in range(num_operations):
            await redis_client.set(
                f"{key_prefix}:{i}",
                test_data
            )
        set_duration = time.time() - start_time
        
        # Measure get performance
        start_time = time.time()
        for i in range(num_operations):
            await redis_client.get(f"{key_prefix}:{i}")
        get_duration = time.time() - start_time
        
        # Verify performance
        assert set_duration < 2.0  # Max 2 seconds
        assert get_duration < 1.0  # Max 1 second
```

### 6. End-to-End Tests

Complete flow testing implementations.

```python
class TestEndToEnd:
    """End-to-end test suite."""
    
    @pytest.mark.e2e
    async def test_interview_flow(
        self,
        test_client: AsyncClient
    ):
        """Test complete interview flow."""
        # Create user
        user_response = await test_client.post(
            "/api/users",
            json={
                "email": "test@example.com",
                "name": "Test User"
            }
        )
        assert user_response.status_code == 201
        user_data = user_response.json()
        
        # Create interview
        interview_response = await test_client.post(
            "/api/interviews",
            json={
                "user_id": user_data["id"],
                "questions": ["Q1", "Q2"],
                "language": "en"
            }
        )
        assert interview_response.status_code == 201
        interview_data = interview_response.json()
        
        # Create session
        session_response = await test_client.post(
            "/api/sessions",
            json={
                "interview_id": interview_data["id"],
                "user_id": user_data["id"]
            }
        )
        assert session_response.status_code == 201
        session_data = session_response.json()
        
        # Submit answers
        for i, question in enumerate(interview_data["questions"]):
            answer_response = await test_client.post(
                f"/api/sessions/{session_data['id']}/answers",
                json={
                    "question_index": i,
                    "audio_url": f"test_{i}.wav"
                }
            )
            assert answer_response.status_code == 200
            
        # Get results
        results_response = await test_client.get(
            f"/api/interviews/{interview_data['id']}"
        )
        assert results_response.status_code == 200
        results_data = results_response.json()
        
        # Verify results
        assert results_data["status"] == "completed"
        assert len(results_data["answers"]) == 2
        assert results_data["analysis"] is not None
```

## Integration

### 1. Test Runner

Configuration for pytest test runner.

```python
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    e2e: End-to-end tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
```

### 2. Coverage Configuration

Configuration for coverage reporting.

```python
# .coveragerc
[run]
source = tenx_ipersona/backend
omit =
    tests/*
    */__init__.py
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError

[html]
directory = coverage_html
```

### 3. Test Utilities

Helper functions for testing.

```python
async def create_test_data(
    database_pool: asyncpg.Pool,
    data_file: str
) -> None:
    """Load test data from file."""
    async with database_pool.acquire() as conn:
        # Read data file
        with open(data_file) as f:
            data = json.load(f)
            
        # Insert data
        for table, rows in data.items():
            for row in rows:
                columns = ", ".join(row.keys())
                values = ", ".join(f"${i+1}" for i in range(len(row)))
                query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
                await conn.execute(query, *row.values())

def generate_test_audio(
    duration: float,
    sample_rate: int = 44100
) -> bytes:
    """Generate test audio data."""
    num_samples = int(duration * sample_rate)
    samples = np.random.uniform(-1, 1, num_samples)
    return samples.tobytes()

async def wait_for_condition(
    condition: Callable[[], Awaitable[bool]],
    timeout: float = 5.0,
    interval: float = 0.1
) -> None:
    """Wait for condition to be true."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition():
            return
        await asyncio.sleep(interval)
    raise TimeoutError("Condition not met")
``` 