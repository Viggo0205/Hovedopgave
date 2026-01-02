# Rate Limiting & Circuit Breaker Implementation

## Overview
User Story 5 requires the MCP server to handle API calls to external services (GitHub, Jira) in a way that prevents overloading or bringing them down, ensuring stable and reliable integrations.

## Implementation Status: ✅ COMPLETE (GitHub)

### GitHub Service - Rate Limiting Features

#### 1. **Throttling** (Functional Requirement 1)
- **Implementation**: `asyncio-throttle` library
- **Default Rate**: 60 requests per minute (configurable via `GITHUB_REQUESTS_PER_MINUTE`)
- **Enforcement**: All API calls pass through `_api_call_with_retry()` wrapper with `async with self.throttler`
- **How it works**: 
  - Throttler maintains a sliding window of requests
  - Blocks execution if rate limit would be exceeded
  - Ensures we stay under GitHub's 5000 req/hour limit

**Configuration**:
```env
GITHUB_REQUESTS_PER_MINUTE=60  # Max requests per minute (default: 60)
GITHUB_RATE_LIMIT=5000          # GitHub API hourly limit (free tier)
```

#### 2. **HTTP 429 Handling** (Functional Requirement 2)
- **Exception Caught**: `RateLimitExceededException` and `GithubException` with status 429
- **Retry Logic**: Exponential backoff (5s, 10s, 20s)
- **Max Retries**: 3 attempts before failing
- **Backoff Formula**: `wait_time = (2 ** attempt) * 5` seconds
- **Implementation Location**: `src/services/github_service.py::_api_call_with_retry()`

**How it works**:
```python
# Attempt 1 fails → wait 5 seconds
# Attempt 2 fails → wait 10 seconds  
# Attempt 3 fails → raise exception and increment failure count
```

#### 3. **Degraded State / Circuit Breaker** (Functional Requirement 3)
- **Failure Threshold**: 3 consecutive failures (configurable via `GITHUB_MAX_FAILURES`)
- **Degraded Duration**: 300 seconds / 5 minutes (configurable via `GITHUB_DEGRADED_DURATION_SECONDS`)
- **State Tracking**: Class-level variables in `GitHubService`
  - `_degraded_state`: Boolean flag
  - `_degraded_until`: Unix timestamp for recovery time
  - `_failure_count`: Current consecutive failure count

**State Transitions**:
```
Normal → Failure #1 → Failure #2 → Failure #3 → DEGRADED (5 min)
                                                      ↓
                                               (after 5 min)
                                                      ↓
                                                  RECOVERED
```

**Configuration**:
```env
GITHUB_MAX_FAILURES=3                    # Failures before degraded (default: 3)
GITHUB_DEGRADED_DURATION_SECONDS=300     # Degraded duration in seconds (default: 300)
```

#### 4. **Integration Isolation** (Non-Functional Requirement 2)
- **Exception**: `GitHubServiceDegradedException` - specific to GitHub, doesn't affect Jira
- **Early Exit**: Degraded state checked before any API call
- **Graceful Handling**: Returns error dict with `"degraded": True` instead of crashing

**Example Response When Degraded**:
```json
{
  "error": "GitHub integration is temporarily unavailable",
  "username": "someuser",
  "degraded": true
}
```

## Non-Functional Requirements

### ✅ NFR 1: Maximum API Calls Per Hour
- **GitHub Free Tier Limit**: 5000 requests/hour
- **Our Rate**: 60 requests/minute = 3600 requests/hour
- **Safety Margin**: 28% under GitHub's limit
- **Enforcement**: Throttler blocks requests exceeding configured rate

### ✅ NFR 2: Integration Isolation
- **GitHub Failures**: Do NOT affect Jira service
- **Separate Services**: `GitHubService` and `JiraService` are independent
- **Degraded State**: Only blocks GitHub calls, Jira continues normally
- **Error Propagation**: `GitHubServiceDegradedException` caught in analyzer, doesn't crash server

## Architecture

### Components Modified

1. **`src/services/github_service.py`**
   - Added `Throttler` instance (60 req/min)
   - Added `_api_call_with_retry()` wrapper with exponential backoff
   - Added class-level degraded state tracking
   - Made all methods async and pass through retry wrapper
   - Added `GitHubServiceDegradedException` custom exception

2. **`src/analyzers/github_analyzer.py`**
   - Updated to `await` async service calls
   - Added degraded state check before analysis
   - Returns error dict when service degraded
   - Catches `GitHubServiceDegradedException`

3. **`src/config.py`**
   - Added rate limiting configuration variables
   - Documented default values and purpose

4. **`pyproject.toml`**
   - Already included `asyncio-throttle>=1.0.0` dependency

## Usage Examples

### Normal Operation
```python
service = GitHubService()
analyzer = GitHubAnalyzer(service)

# All API calls automatically throttled and retried
result = await analyzer.analyze_developer("username")
```

### Degraded State
```python
# After 3 consecutive failures...
if GitHubService.is_degraded():
    print("GitHub integration unavailable for 5 minutes")
    # Service automatically recovers after degraded_duration expires
```

### Manual State Check
```python
# Check if service is healthy
if not GitHubService.is_degraded():
    result = await service.get_user_profile("username")
else:
    print("Service degraded, skipping GitHub analysis")
```

## Testing Recommendations

### Unit Tests (To Be Implemented)
```python
# tests/test_github_rate_limiting.py

async def test_throttling():
    """Verify requests are throttled to configured rate"""
    # Make 61 requests rapidly, verify 61st is delayed

async def test_429_retry():
    """Verify exponential backoff on rate limit errors"""
    # Mock RateLimitExceededException, verify retries with increasing delays

async def test_degraded_state():
    """Verify circuit breaker trips after max failures"""
    # Trigger 3 failures, verify service marked degraded

async def test_degraded_recovery():
    """Verify service recovers after degraded duration"""
    # Mark degraded, wait duration, verify state resets
```

### Integration Tests
```python
async def test_real_github_api_with_limits():
    """Test against real GitHub API respecting rate limits"""
    # Make controlled number of requests, verify no 429 errors
```

## Monitoring & Logging

### Log Messages
- **INFO**: `"GitHubService initialized with rate limit: 60 req/min"`
- **WARNING**: `"Rate limit exceeded (attempt 1/3). Waiting 5s before retry..."`
- **ERROR**: `"GitHub integration marked as DEGRADED for 300s after 3 failures"`
- **INFO**: `"GitHub integration recovered from degraded state"`

### Metrics to Track (Future Enhancement)
- Requests per minute (actual vs. limit)
- Retry attempts per hour
- Degraded state occurrences per day
- Average response time per endpoint

## Configuration Summary

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `GITHUB_REQUESTS_PER_MINUTE` | 60 | Throttle rate (requests/min) |
| `GITHUB_RATE_LIMIT` | 5000 | GitHub API hourly limit |
| `GITHUB_MAX_FAILURES` | 3 | Failures before degraded |
| `GITHUB_DEGRADED_DURATION_SECONDS` | 300 | Degraded state duration (5 min) |

## Future Enhancements

1. **Jira Rate Limiting**: Apply same pattern to `JiraService`
2. **Database State**: Store degraded state in PostgreSQL for multi-instance deployments
3. **Metrics Dashboard**: Track rate limit usage in real-time
4. **Adaptive Throttling**: Adjust rate based on remaining quota from GitHub API headers
5. **Alert System**: Notify admins when service enters degraded state

## Compliance with User Story 5

| Requirement | Status | Implementation |
|------------|--------|----------------|
| **FR1**: Throttling on GitHub/Jira calls | ✅ GitHub | `asyncio-throttle` with 60 req/min |
| **FR2**: Handle HTTP 429 with backoff | ✅ GitHub | Exponential backoff: 5s, 10s, 20s |
| **FR3**: Mark integration degraded after failures | ✅ GitHub | Circuit breaker after 3 failures |
| **NFR1**: Not exceed max API calls per hour | ✅ GitHub | 3600/hour < 5000/hour limit |
| **NFR2**: Failures don't affect other integrations | ✅ | Separate services, isolated exceptions |

## GitHub Implementation: ✅ **COMPLETE**
## Jira Implementation: ⚠️ **PENDING** (apply same pattern)
