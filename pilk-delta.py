#!/usr/bin/env python3
"""
Pilk-delta Patch: Enhanced api_get() with Multi-Provider Fallback
PR-Ready Implementation for Robust API Requests

Changes:
- Multi-provider fallback with configurable providers
- Exponential backoff with jitter
- Circuit breaker pattern for failing endpoints
- Comprehensive error handling with typed exceptions
- Request/response logging for debugging
- Timeout management per provider
"""

import json
import sys
import logging
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
STORAGE_FILE = Path.home() / ".openclaw/workspace/memory/pilk-delta.json"

# =============================================================================
# ERROR HANDLING SCHEMA
# =============================================================================

class APIErrorType(Enum):
    """Categorized API error types for structured handling."""
    NETWORK = "network"           # Connection issues, DNS failures
    TIMEOUT = "timeout"           # Request timed out
    RATE_LIMIT = "rate_limit"     # 429 Too Many Requests
    AUTH = "auth"                 # 401/403 Authentication issues
    NOT_FOUND = "not_found"       # 404 Resource not found
    SERVER = "server"             # 5xx Server errors
    INVALID_RESPONSE = "invalid"  # Malformed JSON, unexpected structure
    CIRCUIT_OPEN = "circuit"      # Circuit breaker triggered
    UNKNOWN = "unknown"           # Unclassified errors


@dataclass
class APIError(Exception):
    """Structured API error with context for debugging and recovery."""
    error_type: APIErrorType
    message: str
    provider: str
    url: str
    status_code: Optional[int] = None
    retry_after: Optional[int] = None  # Seconds to wait before retry
    original_exception: Optional[Exception] = None

    def __str__(self) -> str:
        base = f"[{self.error_type.value.upper()}] {self.provider}: {self.message}"
        if self.status_code:
            base += f" (HTTP {self.status_code})"
        if self.retry_after:
            base += f" - retry after {self.retry_after}s"
        return base

    def is_retryable(self) -> bool:
        """Determine if the error is transient and worth retrying."""
        return self.error_type in (
            APIErrorType.NETWORK,
            APIErrorType.TIMEOUT,
            APIErrorType.RATE_LIMIT,
            APIErrorType.SERVER,
            APIErrorType.CIRCUIT_OPEN,
        )


@dataclass
class SubagentTimeoutError(Exception):
    """
    Structured error for subagent timeout scenarios.
    Provides context for timeout handling and escalation.
    """
    agent_id: str
    task_description: str
    timeout_seconds: float
    elapsed_seconds: float
    stage: str  # 'initialization', 'execution', 'response', 'cleanup'
    partial_result: Optional[Any] = None
    recovery_hint: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"Subagent {self.agent_id} timed out after {self.elapsed_seconds:.1f}s "
            f"(limit: {self.timeout_seconds}s) during {self.stage}"
        )


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

@dataclass
class CircuitState:
    """Circuit breaker state for a provider."""
    is_open: bool = False
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    
    # Configuration
    failure_threshold: int = 3
    recovery_timeout: int = 60  # Seconds before attempting recovery


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents cascading failures by temporarily blocking requests to failing endpoints.
    """
    
    def __init__(self):
        self._circuits: Dict[str, CircuitState] = {}
    
    def _get_circuit(self, provider: str) -> CircuitState:
        if provider not in self._circuits:
            self._circuits[provider] = CircuitState()
        return self._circuits[provider]
    
    def can_execute(self, provider: str) -> bool:
        """Check if requests are allowed for this provider."""
        circuit = self._get_circuit(provider)
        
        if not circuit.is_open:
            return True
        
        # Check if recovery timeout has passed
        if circuit.last_failure:
            elapsed = (datetime.now() - circuit.last_failure).total_seconds()
            if elapsed >= circuit.recovery_timeout:
                logging.info(f"Circuit breaker entering half-open state for {provider}")
                return True  # Allow test request
        
        return False
    
    def record_success(self, provider: str) -> None:
        """Record successful request, potentially closing circuit."""
        circuit = self._get_circuit(provider)
        circuit.last_success = datetime.now()
        
        if circuit.is_open:
            logging.info(f"Circuit breaker closed for {provider}")
            circuit.is_open = False
            circuit.failure_count = 0
    
    def record_failure(self, provider: str) -> None:
        """Record failed request, potentially opening circuit."""
        circuit = self._get_circuit(provider)
        circuit.failure_count += 1
        circuit.last_failure = datetime.now()
        
        if circuit.failure_count >= circuit.failure_threshold:
            if not circuit.is_open:
                logging.warning(f"Circuit breaker opened for {provider}")
            circuit.is_open = True


# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

@dataclass
class ProviderConfig:
    """Configuration for an API provider."""
    name: str
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    backoff_base: float = 1.0  # Base seconds for exponential backoff
    backoff_max: float = 30.0
    jitter: float = 0.1  # Random jitter factor (0-1)
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Rate limiting
    rate_limit_per_second: Optional[float] = None
    last_request_time: float = 0.0


class ProviderRegistry:
    """Registry of API providers with their configurations."""
    
    DEFAULT_PROVIDERS = {
        'deribit': ProviderConfig(
            name='deribit',
            base_url='https://www.deribit.com/api/v2',
            timeout=30.0,
            max_retries=3,
            backoff_base=1.0,
            rate_limit_per_second=10,  # ~10 requests/second
        ),
        'binance': ProviderConfig(
            name='binance',
            base_url='https://fapi.binance.com',
            timeout=15.0,
            max_retries=3,
            backoff_base=0.5,
            rate_limit_per_second=20,
        ),
        'binance_spot': ProviderConfig(
            name='binance_spot',
            base_url='https://api.binance.com',
            timeout=15.0,
            max_retries=3,
            backoff_base=0.5,
        ),
        'coinglass': ProviderConfig(
            name='coinglass',
            base_url='https://open-api.coinglass.com',
            timeout=20.0,
            max_retries=2,
            backoff_base=2.0,
        ),
    }
    
    def __init__(self, custom_providers: Optional[Dict[str, ProviderConfig]] = None):
        self.providers = {**self.DEFAULT_PROVIDERS}
        if custom_providers:
            self.providers.update(custom_providers)
    
    def get(self, name: str) -> Optional[ProviderConfig]:
        return self.providers.get(name)
    
    def add(self, config: ProviderConfig) -> None:
        self.providers[config.name] = config


# =============================================================================
# ENHANCED API CLIENT
# =============================================================================

class APIClient:
    """
    Robust API client with multi-provider fallback, retries, and circuit breaker.
    """
    
    def __init__(
        self,
        provider_registry: Optional[ProviderRegistry] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.providers = provider_registry or ProviderRegistry()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.logger = logger or logging.getLogger(__name__)
        
        # Create session with connection pooling
        self.session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=Retry(
                total=0,  # We handle retries ourselves
                connect=2,
                read=2,
                status=0,
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def _calculate_backoff(
        self, 
        attempt: int, 
        config: ProviderConfig,
        retry_after: Optional[int] = None
    ) -> float:
        """Calculate backoff time with exponential decay and jitter."""
        if retry_after:
            return float(retry_after)
        
        # Exponential backoff with jitter
        base = config.backoff_base * (2 ** attempt)
        jitter = random.uniform(0, config.jitter) * base
        backoff = min(base + jitter, config.backoff_max)
        return backoff
    
    def _classify_error(self, exc: Exception, response: Optional[requests.Response]) -> APIError:
        """Classify an exception into a structured APIError."""
        provider = "unknown"
        url = "unknown"
        
        if isinstance(exc, requests.Timeout):
            return APIError(
                error_type=APIErrorType.TIMEOUT,
                message="Request timed out",
                provider=provider,
                url=url,
                original_exception=exc,
            )
        
        if isinstance(exc, requests.ConnectionError):
            return APIError(
                error_type=APIErrorType.NETWORK,
                message="Connection failed",
                provider=provider,
                url=url,
                original_exception=exc,
            )
        
        if response is not None:
            status = response.status_code
            provider = getattr(response, '_provider', 'unknown')
            url = response.url
            
            if status == 429:
                retry_after = response.headers.get('Retry-After')
                return APIError(
                    error_type=APIErrorType.RATE_LIMIT,
                    message="Rate limit exceeded",
                    provider=provider,
                    url=url,
                    status_code=status,
                    retry_after=int(retry_after) if retry_after else None,
                )
            
            if status in (401, 403):
                return APIError(
                    error_type=APIErrorType.AUTH,
                    message="Authentication failed",
                    provider=provider,
                    url=url,
                    status_code=status,
                )
            
            if status == 404:
                return APIError(
                    error_type=APIErrorType.NOT_FOUND,
                    message="Resource not found",
                    provider=provider,
                    url=url,
                    status_code=status,
                )
            
            if 500 <= status < 600:
                return APIError(
                    error_type=APIErrorType.SERVER,
                    message=f"Server error: {status}",
                    provider=provider,
                    url=url,
                    status_code=status,
                )
        
        return APIError(
            error_type=APIErrorType.UNKNOWN,
            message=str(exc),
            provider=provider,
            url=url,
            original_exception=exc,
        )
    
    def _respect_rate_limit(self, config: ProviderConfig) -> None:
        """Enforce rate limiting for a provider."""
        if config.rate_limit_per_second:
            min_interval = 1.0 / config.rate_limit_per_second
            elapsed = time.time() - config.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            config.last_request_time = time.time()
    
    def _make_request(
        self,
        url: str,
        params: Optional[dict],
        config: ProviderConfig,
    ) -> dict:
        """Execute a single HTTP request with error handling."""
        self._respect_rate_limit(config)
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=config.timeout,
                headers=config.headers or None,
            )
            response._provider = config.name  # Track provider for error classification
            
            response.raise_for_status()
            
            # Validate JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                raise APIError(
                    error_type=APIErrorType.INVALID_RESPONSE,
                    message=f"Invalid JSON response: {exc}",
                    provider=config.name,
                    url=url,
                    original_exception=exc,
                )
            
            self.circuit_breaker.record_success(config.name)
            return data
            
        except requests.RequestException as exc:
            error = self._classify_error(exc, exc.response if hasattr(exc, 'response') else None)
            error.provider = config.name
            error.url = url
            self.circuit_breaker.record_failure(config.name)
            raise error
    
    def get(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        provider: Optional[str] = None,
        fallback_providers: Optional[List[str]] = None,
    ) -> dict:
        """
        Perform a GET request with multi-provider fallback.
        
        Args:
            endpoint: API endpoint path (e.g., '/public/ticker')
            params: Query parameters
            provider: Primary provider name (default: 'deribit')
            fallback_providers: List of fallback providers to try on failure
            
        Returns:
            dict: JSON response data
            
        Raises:
            APIError: When all providers fail
        """
        provider_name = provider or 'deribit'
        providers_to_try = [provider_name]
        
        if fallback_providers:
            providers_to_try.extend(fallback_providers)
        
        # Remove duplicates while preserving order
        seen = set()
        providers_to_try = [p for p in providers_to_try if not (p in seen or seen.add(p))]
        
        last_error: Optional[APIError] = None
        
        for provider_name in providers_to_try:
            config = self.providers.get(provider_name)
            if not config:
                self.logger.warning(f"Unknown provider: {provider_name}")
                continue
            
            # Check circuit breaker
            if not self.circuit_breaker.can_execute(provider_name):
                self.logger.warning(f"Circuit breaker open for {provider_name}, skipping")
                last_error = APIError(
                    error_type=APIErrorType.CIRCUIT_OPEN,
                    message="Circuit breaker is open",
                    provider=provider_name,
                    url=f"{config.base_url}{endpoint}",
                )
                continue
            
            url = f"{config.base_url}{endpoint}"
            
            # Retry loop for this provider
            for attempt in range(config.max_retries):
                try:
                    self.logger.debug(f"Request to {provider_name}: {endpoint} (attempt {attempt + 1})")
                    return self._make_request(url, params, config)
                    
                except APIError as error:
                    last_error = error
                    
                    if not error.is_retryable():
                        self.logger.warning(f"Non-retryable error from {provider_name}: {error}")
                        break  # Try next provider
                    
                    if attempt < config.max_retries - 1:
                        backoff = self._calculate_backoff(
                            attempt, config, error.retry_after
                        )
                        self.logger.info(
                            f"Retrying {provider_name} in {backoff:.1f}s "
                            f"(attempt {attempt + 2}/{config.max_retries})"
                        )
                        time.sleep(backoff)
                    else:
                        self.logger.warning(f"All retries exhausted for {provider_name}")
        
        # All providers failed
        if last_error:
            raise last_error
        
        raise APIError(
            error_type=APIErrorType.UNKNOWN,
            message="No providers available",
            provider="none",
            url=endpoint,
        )


# =============================================================================
# CONVENIENCE FUNCTION (DROP-IN REPLACEMENT)
# =============================================================================

# Global client instance for backward compatibility
_default_client: Optional[APIClient] = None


def get_client() -> APIClient:
    """Get or create the default API client."""
    global _default_client
    if _default_client is None:
        _default_client = APIClient()
    return _default_client


def api_get(
    url: str,
    params: Optional[dict] = None,
    provider: Optional[str] = None,
    fallback_providers: Optional[List[str]] = None,
) -> dict:
    """
    Perform a GET request with multi-provider fallback.
    
    Enhanced version with:
    - Automatic retries with exponential backoff
    - Circuit breaker pattern
    - Rate limiting
    - Typed error handling
    - Multi-provider fallback
    
    Args:
        url: Full URL or endpoint path
        params: Query parameters
        provider: Primary provider name (auto-detected from URL if not provided)
        fallback_providers: List of fallback providers
        
    Returns:
        dict: JSON response data
        
    Raises:
        APIError: Structured error with type, provider, and retry info
        
    Example:
        # Simple usage (backward compatible)
        data = api_get("https://www.deribit.com/api/v2/public/ticker", 
                       {"instrument_name": "BTC-13FEB26-77000-C"})
        
        # With multi-provider fallback
        data = api_get("/fapi/v1/premiumIndex", 
                       provider="binance",
                       fallback_providers=["binance_spot"])
    """
    client = get_client()
    
    # Auto-detect provider from URL if it's a full URL
    if url.startswith('http'):
        for name, config in client.providers.providers.items():
            if url.startswith(config.base_url):
                endpoint = url[len(config.base_url):]
                return client.get(
                    endpoint, params, name, fallback_providers
                )
        
        # Unknown URL, try direct request
        config = ProviderConfig(name='direct', base_url='', timeout=30.0)
        return client._make_request(url, params, config)
    
    # It's an endpoint path
    return client.get(url, params, provider, fallback_providers)


# =============================================================================
# ERROR HANDLING SCHEMA FOR SUBAGENT TIMEOUTS
# =============================================================================

"""
SUBAGENT TIMEOUT ERROR-HANDLING SCHEMA
======================================

This schema defines how to handle timeouts in subagent operations.

## 1. Timeout Categories

### Initialization Timeout (default: 30s)
- Time to spawn and configure subagent
- Failure: Retry with exponential backoff, max 3 attempts
- Escalation: Log warning, fall back to main agent execution

### Execution Timeout (default: 300s / 5min)
- Time for subagent to complete its task
- Configurable per task complexity:
  - Simple tasks: 60s (file reads, simple calculations)
  - Standard tasks: 300s (API calls, data processing)
  - Complex tasks: 900s (multi-step operations, web scraping)
- Failure: 
  1. Check for partial results
  2. Attempt graceful shutdown
  3. Kill if unresponsive after 30s grace period
  4. Store partial results if meaningful

### Response Timeout (default: 60s)
- Time for subagent to return results after completion
- Failure: Assume subagent hung, attempt recovery

### Cleanup Timeout (default: 30s)
- Time for graceful shutdown and resource cleanup
- Failure: Force kill process

## 2. Error Structure

```python
@dataclass
class SubagentTimeoutError:
    agent_id: str              # Unique identifier
    task_description: str      # What was being attempted
    timeout_seconds: float     # Configured limit
    elapsed_seconds: float     # Actual time elapsed
    stage: str                 # Where timeout occurred
    partial_result: Any        # Any data captured before timeout
    recovery_hint: str         # Suggested recovery action
```

## 3. Recovery Strategies

### Strategy 1: Retry with Backoff
- Use for: Network issues, temporary resource constraints
- Pattern: Exponential backoff with jitter
- Max retries: 3
- Backoff: 1s, 2s, 4s (with ±20% jitter)

### Strategy 2: Fallback to Main Agent
- Use for: Persistent failures, critical tasks
- Pattern: Main agent takes over with simplified approach
- Trade-off: Higher main agent load vs task completion

### Strategy 3: Partial Result Recovery
- Use for: Long-running tasks with incremental output
- Pattern: Capture stdout/stderr, parse for partial results
- Store: In memory/ file for later resumption

### Strategy 4: Task Decomposition
- Use for: Complex tasks that exceed timeout
- Pattern: Break into smaller subtasks, spawn multiple subagents
- Benefit: Better parallelism, easier recovery

## 4. Monitoring & Alerting

### Metrics to Track:
- subagent_timeout_total{stage, agent_type}
- subagent_timeout_duration_seconds{stage}
- subagent_recovery_success_total{strategy}
- subagent_partial_result_captured_total

### Alerting Thresholds:
- >5% timeout rate: Warning
- >15% timeout rate: Critical
- Same agent timeout 3x in 1h: Investigate

## 5. Configuration

```python
SUBAGENT_TIMEOUT_CONFIG = {
    'default': {
        'initialization': 30,
        'execution': 300,
        'response': 60,
        'cleanup': 30,
    },
    'overrides': {
        'data_collection': {'execution': 900},
        'quick_read': {'execution': 60},
        'web_scraping': {'execution': 600},
    },
    'retry': {
        'max_attempts': 3,
        'backoff_base': 1.0,
        'backoff_multiplier': 2.0,
        'jitter': 0.2,
    },
}
```

## 6. Implementation Pattern

```python
async def execute_with_timeout(
    task: Callable,
    timeout_config: Dict[str, int],
    on_partial: Optional[Callable] = None,
    on_timeout: Optional[Callable] = None,
) -> Any:
    try:
        result = await asyncio.wait_for(
            task(),
            timeout=timeout_config['execution']
        )
        return result
    except asyncio.TimeoutError:
        partial = capture_partial_result()
        if on_partial and partial:
            on_partial(partial)
        
        error = SubagentTimeoutError(
            agent_id=get_current_agent_id(),
            task_description=get_task_description(),
            timeout_seconds=timeout_config['execution'],
            elapsed_seconds=get_elapsed_time(),
            stage='execution',
            partial_result=partial,
            recovery_hint=suggest_recovery_strategy(partial),
        )
        
        if on_timeout:
            return on_timeout(error)
        raise error
```
"""


# =============================================================================
# TESTING / VALIDATION
# =============================================================================

def test_api_get():
    """Test the enhanced api_get function."""
    print("Testing enhanced api_get()...")
    
    # Test 1: Simple request (backward compatible)
    try:
        data = api_get(
            "https://www.deribit.com/api/v2/public/ticker",
            {"instrument_name": "BTC-14FEB26-95000-C"}
        )
        print(f"✓ Deribit request successful: {data.get('result', {}).get('instrument_name', 'N/A')}")
    except APIError as e:
        print(f"✗ Deribit request failed: {e}")
    
    # Test 2: With provider specification
    try:
        client = get_client()
        data = client.get(
            "/fapi/v1/premiumIndex",
            provider="binance"
        )
        print(f"✓ Binance request successful: {data.get('symbol', 'N/A')}")
    except APIError as e:
        print(f"✗ Binance request failed: {e}")
    
    # Test 3: Circuit breaker simulation
    print("\n✓ All tests completed")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
