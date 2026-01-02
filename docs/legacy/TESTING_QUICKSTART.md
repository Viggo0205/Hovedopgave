# Database Test Suite - Quick Start

## ✅ What Was Created

### Test Files (53 Total Tests)
1. **`tests/test_db_connection.py`** - 15 tests for connection pooling, queries, transactions
2. **`tests/test_db_repository.py`** - 27 tests for CRUD operations, datetime serialization
3. **`tests/test_db_integration.py`** - 11 tests for stored procedures, triggers, views

### Supporting Files
- **`tests/conftest.py`** - Pytest configuration with fixtures
- **`tests/__init__.py`** - Package initialization
- **`run_tests.bat`** - Windows batch script to run all tests
- **`docs/DATABASE_TESTING.md`** - Comprehensive testing documentation

## 🚀 Running Tests

### Quick Run (All Tests)
```bash
cd E:\Nymappe\Hovedopgave
run_tests.bat
```

### Manual Run
```powershell
cd E:\Nymappe\Hovedopgave
E:\Nymappe\python\python.exe -m pytest tests/ -v
```

### Run Specific Test File
```powershell
# Connection tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_connection.py -v

# Repository tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_repository.py -v

# Integration tests only
E:\Nymappe\python\python.exe -m pytest tests/test_db_integration.py -v
```

## 📋 Test Coverage

### Connection Tests (15 tests)
- Connection pooling
- Query execution (SELECT, INSERT, UPDATE)
- Transaction management (commit/rollback)
- Health checks
- Connection reuse

### Repository Tests (27 tests)
- User management (create, get, update)
- Competence operations (add, update, query)
- Analysis storage (save, retrieve, versioning)
- Datetime serialization
- Data validation

### Integration Tests (11 tests)
- Stored procedures validation
- Trigger functionality
- Auto-update features
- Database views
- Version management (max 2 versions)

## 🔧 Requirements

### Prerequisites
- ✅ **PostgreSQL 18** running on `localhost:5432`
- ✅ **User**: `postgres`, **Password**: `1234`
- ✅ **Python packages**: `pytest`, `pytest-asyncio` (installed)

### Test Database
- **Name**: `developer_skills_test`
- **Lifecycle**: Created before tests, dropped after
- **Schema**: Loaded from `src/db/schema.sql` + `src/db/auto_update_schema.sql`

## 📊 Expected Output

```
tests/test_db_connection.py::TestDatabaseConnection::test_connection_initialization PASSED
tests/test_db_connection.py::TestDatabaseConnection::test_get_connection PASSED
tests/test_db_connection.py::TestDatabaseConnection::test_execute_query_select PASSED
...
tests/test_db_repository.py::TestDatabaseRepository::test_save_analysis PASSED
tests/test_db_repository.py::TestDatabaseRepository::test_datetime_serialization_in_analysis PASSED
...
tests/test_db_integration.py::TestAutoUpdateFeatures::test_last_analyzed_at_trigger PASSED
tests/test_db_integration.py::TestDatabaseViews::test_v_update_status_view PASSED

========================= 53 passed in 15.23s =========================
```

## 🐛 Troubleshooting

### Database Connection Failed
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Start if stopped
Start-Service postgresql-x64-18
```

### Test Database Exists
PostgreSQL automatically handles this - drops and recreates on each run.

### Schema Loading Errors
Verify both schema files exist:
- `src/db/schema.sql`
- `src/db/auto_update_schema.sql`

## 📝 Test Structure

```
tests/
├── __init__.py                 # Package init
├── conftest.py                 # Fixtures & config
├── test_db_connection.py       # Connection layer tests
├── test_db_repository.py       # Repository layer tests
└── test_db_integration.py      # Database features tests
```

## 🎯 Key Features Tested

### ✅ Connection Management
- Connection pooling with min/max connections
- Automatic reconnection
- Connection health monitoring
- Transaction safety

### ✅ Data Operations
- CRUD operations for users and competences
- Analysis versioning (keeps latest 2 versions)
- Datetime serialization for JSON storage
- Query parameterization (SQL injection protection)

### ✅ Database Features
- Stored procedures (`get_or_create_user`, `save_analysis`)
- Triggers (`trg_update_last_analyzed`)
- Views (`user_competence_overview`, `v_update_status`)
- Auto-update functionality

### ✅ Data Integrity
- Transaction rollback on errors
- Foreign key constraints
- Unique constraints
- Version management

## 📚 Full Documentation

See **`docs/DATABASE_TESTING.md`** for:
- Detailed test descriptions
- Debugging commands
- CI/CD integration examples
- Test maintenance guidelines

## ✨ Next Steps

1. **Run tests**: `run_tests.bat`
2. **Review results**: Check for any failures
3. **Add new tests**: Follow patterns in existing test files
4. **Integrate CI/CD**: Use pytest in automated pipelines
