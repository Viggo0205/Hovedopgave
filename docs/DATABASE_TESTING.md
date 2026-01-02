# Database Testing Guide

## Overview
Comprehensive pytest-based unit and integration tests for the database layer.

## Test Structure

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── test_db_connection.py          # DatabaseConnection tests (15 tests)
├── test_db_repository.py          # DatabaseRepository tests (27 tests)
└── test_db_integration.py         # Stored procedures and triggers (11 tests)
```

## Prerequisites

1. **PostgreSQL** must be running on `localhost:5432`
2. **Credentials**: User `postgres` with password `1234`
3. **Python packages**: Install pytest
   ```bash
   E:\Nymappe\python\python.exe -m pip install pytest pytest-asyncio
   ```

## Running Tests

### All Tests
```bash
# Windows
run_tests.bat

# Or manually
cd E:\Nymappe\Hovedopgave
E:\Nymappe\python\python.exe -m pytest tests/ -v
```

### Specific Test Files
```bash
# Connection tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py -v

# Repository tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_repository.py -v

# Integration tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_integration.py -v
```

### Specific Test Classes
```bash
# Test connection pooling
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py::TestDatabaseConnection -v

# Test repository CRUD operations
E:\Nymappe\python\python.exe -m pytest tests/test_db_repository.py::TestDatabaseRepository -v
```

### Specific Test Functions
```bash
# Test single function
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py::TestDatabaseConnection::test_health_check_healthy -v
```

## Test Database

- **Database Name**: `developer_skills_test`
- **Lifecycle**: 
  - Created before test session
  - Schema loaded from `src/db/schema.sql` and `src/db/auto_update_schema.sql`
  - Dropped after test session
- **Isolation**: Each test gets a clean database (all tables truncated)

## Test Coverage

### test_db_connection.py (15 tests)
Tests for `DatabaseConnection` class:

- ✅ Connection initialization
- ✅ Connection pool management
- ✅ Get/return connections
- ✅ Execute queries (SELECT, INSERT, UPDATE)
- ✅ Query with parameters
- ✅ Transaction commit/rollback
- ✅ Health check (healthy/unhealthy)
- ✅ Connection reuse
- ✅ Close all connections

### test_db_repository.py (27 tests)
Tests for `DatabaseRepository` class:

**Datetime Serialization:**
- ✅ Serialize datetime objects
- ✅ Serialize dicts with datetime
- ✅ Serialize lists with datetime
- ✅ Serialize nested structures

**Repository Operations:**
- ✅ Add competence
- ✅ Get or create user (new/existing)
- ✅ Update user competence
- ✅ Save analysis (version management)
- ✅ Get latest analysis
- ✅ Get all analyses (max 2 versions)
- ✅ Get user competence overview
- ✅ Get all competences
- ✅ Get user by identifier (GitHub/Jira)
- ✅ Datetime serialization in analysis

### test_db_integration.py (11 tests)
Tests for database stored procedures and triggers:

**Stored Procedures:**
- ✅ `get_or_create_user()` - Create/retrieve user
- ✅ `add_competence()` - Add new competence
- ✅ `update_user_competence()` - Update skill levels
- ✅ `save_analysis()` - Save with version management
- ✅ `get_latest_analysis()` - Retrieve latest analysis

**Auto-Update Features:**
- ✅ `trg_update_last_analyzed` - Trigger on analysis insert
- ✅ `get_users_for_update()` - Filter users needing updates
- ✅ `auto_update_enabled` flag filtering

**Database Views:**
- ✅ `user_competence_overview` - Joined user/competence data
- ✅ `v_update_status` - Update status monitoring

## Fixtures

### Session-Scoped
- `test_db_config`: Test database credentials
- `test_connection_string`: PostgreSQL connection string
- `setup_test_database`: Creates/drops test database

### Function-Scoped
- `db_connection`: Fresh `DatabaseConnection` instance
- `db_repository`: Fresh `DatabaseRepository` instance
- `clean_database`: Truncates all tables before test

## Example Test Output

```
tests/test_db_connection.py::TestDatabaseConnection::test_connection_initialization PASSED
tests/test_db_connection.py::TestDatabaseConnection::test_get_connection PASSED
tests/test_db_connection.py::TestDatabaseConnection::test_execute_query_select PASSED
...
tests/test_db_repository.py::TestDatabaseRepository::test_save_analysis PASSED
tests/test_db_repository.py::TestDatabaseRepository::test_get_latest_analysis PASSED
...
tests/test_db_integration.py::TestStoredProcedures::test_save_analysis_procedure PASSED
tests/test_db_integration.py::TestAutoUpdateFeatures::test_last_analyzed_at_trigger PASSED

============================================ 53 passed in 12.34s ============================================
```

## Debugging Failed Tests

### Verbose Output
```bash
E:\Nymappe\python\python.exe -m pytest tests/ -vv
```

### Show Print Statements
```bash
E:\Nymappe\python\python.exe -m pytest tests/ -v -s
```

### Stop on First Failure
```bash
E:\Nymappe\python\python.exe -m pytest tests/ -v -x
```

### Show Full Traceback
```bash
E:\Nymappe\python\python.exe -m pytest tests/ -v --tb=long
```

## Common Issues

### Database Connection Failed
- Check PostgreSQL is running: `Get-Service postgresql*`
- Verify credentials in `conftest.py`
- Ensure port 5432 is accessible

### Test Database Already Exists
- Manually drop: `DROP DATABASE developer_skills_test;`
- Or let pytest handle it (runs in teardown)

### Schema Errors
- Verify `src/db/schema.sql` is valid
- Check `src/db/auto_update_schema.sql` is present
- Ensure all dependencies are in correct order

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Database Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_PASSWORD: 1234
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install pytest pytest-asyncio psycopg2-binary
      - name: Run tests
        run: pytest tests/ -v
```

## Test Maintenance

### Adding New Tests
1. Create test function with descriptive name
2. Use appropriate fixtures (`db_connection`, `db_repository`, `clean_database`)
3. Follow AAA pattern: Arrange, Act, Assert
4. Add docstring explaining what's being tested

### Example Test Template
```python
def test_new_feature(self, db_repository, clean_database):
    """Test description here."""
    # Arrange
    user_id = db_repository.get_or_create_user(github_username='testuser')
    
    # Act
    result = db_repository.some_new_method(user_id)
    
    # Assert
    assert result is not None
    assert result['field'] == 'expected_value'
```

## Total Test Count: **53 Tests**

- Connection Tests: 15
- Repository Tests: 27
- Integration Tests: 11
