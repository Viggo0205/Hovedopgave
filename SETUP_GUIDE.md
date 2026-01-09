# Developer Skill Analyzer - Setup Guide

Sådan sætter du systemet op på en ny computer.

## Hvad du skal bruge

- **Python 3.11 eller nyere**
- **PostgreSQL 18 eller nyere** (skal køre)
- **uv** (`pip install uv`)
- **Git**

## Trin 1: Hent koden

```bash
git clone https://github.com/Viggo0205/Hovedopgave.git
cd Hovedopgave
```

## Trin 2: Installer Python pakker

```bash
uv sync
```

Det henter alle dependencies fra `pyproject.toml`.

## Trin 3: Lav din `.env` fil

Kopier `.env.example` til `.env`:

```bash
cp .env.example .env
```

Åbn `.env` og udfyld dine værdier:

```env
# GitHub Token (PÅKRÆVET - se nedenfor)
GITHUB_TOKEN=ghp_dinTokenHer
GITHUB_ACCESS_TOKEN=ghp_dinTokenHer

# Database (ret password til dit eget)
DATABASE_URL=postgresql://postgres:DitPassword@localhost:5432/developer_skills

# Resten kan være som den er
MOCK_MODE=false
LOG_LEVEL=INFO
```

### Hvordan får jeg en GitHub token?

1. Gå til https://github.com/settings/tokens
2. Klik "Generate new token" → "Generate new token (classic)"
3. Giv den et navn, fx "Developer Skill Analyzer"
4. Vælg disse permissions:
   - ✓ `public_repo`
   - ✓ `read:user`
   - ✓ `read:org`
5. Klik "Generate token"
6. Kopier token'en (du kan IKKE se den igen!)
7. Indsæt i både `GITHUB_TOKEN` og `GITHUB_ACCESS_TOKEN` felterne

**Vigtigt:** 
- Commit ALDRIG `.env` til git!
- Token'en er som et password - del den ikke!

## Trin 4: Setup database

**Vigtigt:** Åbn `setup_database_complete.py` og ret database password på linje 25:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '1234',  # <--- RET DETTE til dit PostgreSQL password
    'database': 'developer_skills'
}
```

Kør derefter setup scriptet:

```bash
python setup_database_complete.py
```

Scriptet gør følgende automatisk:
1. Opretter database `developer_skills`
2. Loader schema (tabeller, funktioner, views)
3. Tilføjer audit log funktionalitet
4. Verificerer at alt virker

Du får output der viser hvad der sker:
```
Developer Skill Analyzer - Complete Database Setup
[OK] Database 'developer_skills' created
[OK] Main schema (schema.sql) completed
[OK] Migration: add_audit_log_and_admin_tracking.sql completed
[OK] Found 12 tables
[OK] Found 17 stored functions
[OK] Database setup completed successfully!
```

## Trin 5: Test at det virker

### Kør alle tests

```bash
pytest tests/ -v
```

Hvis alt er godt ser du:
```
44 passed in 10.03s
```

### Kør specifikke tests

```bash
# Kun database connection tests
pytest tests/test_db_connection.py -v

# Kun repository tests  
pytest tests/test_db_repository.py -v

# Kun integration tests
pytest tests/test_db_integration.py -v

# Én specifik test
pytest tests/test_db_connection.py::TestDatabaseConnection::test_health_check_healthy -v
```

### Test struktur

```
tests/
├── test_db_connection.py    # DatabaseConnection tests (12 tests)
├── test_db_repository.py    # DatabaseRepository tests (21 tests)
└── test_db_integration.py   # Stored procedures + triggers (11 tests)
```

**Bemærk:** Tests bruger en separat `developer_skills_test` database som oprettes automatisk.

## Trin 6: Tilslut Claude Desktop

Kør setup script:

```bash
python scripts/utilities/setup_claude_desktop.py
```

Dette script finder automatisk Claude Desktop's config-fil (virker på Windows, Mac og Linux), laver backup af din eksisterende config, og tilføjer Developer Skill Analyzer serveren.

Du får output som:
```
✅ Found uv at: C:\Users\...\uv.exe
✅ Backed up existing config
✅ Claude Desktop config updated
🎉 Setup complete! Genstart Claude Desktop.
```

## Trin 7: Start serveren

### Windows:
```bash
scripts\start_mcp_server.bat
```

### Linux/Mac:
```bash
uv run src/server.py
```

Nu kan du bruge MCP tools fra Claude Desktop!

---

## Ekstra Tool Tests

Projektet har to ekstra test-filer i roden til at teste specifikke funktioner:

```bash
python test_remove_developer.py  # Test remove developer tool
python test_language_tool.py     # Test language extraction
```

---

## Hvad gør Claude Desktop Setup Scriptet?

Efter refaktoreringen skulle systemet sættes op på en anden computer, så der blev lavet et setup script til at gøre det nemmere.

### Hvordan virker det?

**1. OS-Detection**

Scriptet finder automatisk hvor Claude Desktop gemmer sin config:

```python
def get_claude_config_path():
    if sys.platform == "win32":
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
```

Dette betyder scriptet virker på alle platforme.

**2. UV Dependency Manager**

Scriptet bruger `uv` til at starte serveren fordi det:
- Automatisk håndterer virtual environments
- Loader dependencies baseret på `pyproject.toml`
- Gør startup processen simpel

Alternativet ville være at hardcode Python paths og manuelt aktivere virtual environments, hvilket er mere kompliceret.

**3. Backup og Merge**

Scriptet laver backup af din eksisterende config og merger den nye server ind uden at slette andre MCP-servere du måtte have:

```python
def merge_configs(existing_config, new_server_config):
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["developer-skill-analyzer"] = 
        new_server_config["mcpServers"]["developer-skill-analyzer"]
    
    return existing_config
```

**Bemærk:** Environment variables inkluderes **ikke** i config-filen. MCP serveren loader selv credentials fra `.env` filen, hvilket holder secrets ude af git og konfigurationsfiler.

---

## Fil Struktur

```
Hovedopgave/
├── setup_database_complete.py   # Database setup (kør én gang)
├── test_remove_developer.py     # Tool test
├── test_language_tool.py        # Tool test
├── SETUP_GUIDE.md               # Denne guide
├── pyproject.toml               # Dependencies
├── .env                         # Dine credentials (lav selv)
│
├── src/                         # Kildekode
│   ├── server.py                # MCP server entry point
│   ├── config.py                # Configuration
│   ├── analyzers/               # GitHub/Jira analyzers
│   ├── services/                # API services
│   ├── db/                      # Database layer
│   │   ├── schema.sql          # Main schema
│   │   ├── connection.py       # Connection pool
│   │   └── repository.py       # Data access
│   ├── models/                  # Data models
│   └── shared/                  # Utilities
│
├── tests/                       # 44 pytest tests
│   ├── test_db_connection.py
│   ├── test_db_integration.py
│   └── test_db_repository.py
│
├── scripts/                     # Utility scripts
│   ├── start_mcp_server.bat    # Start server (Windows)
│   └── utilities/
│       └── setup_claude_desktop.py
│
└── migrations/                  # Database migrations
    └── add_audit_log_and_admin_tracking.sql
```

---

## Nyttige Database Queries

Hvis du vil se data direkte i databasen:

### Se alle brugere og deres skills
```sql
SELECT * FROM user_competence_overview;
```

### Se en brugers seneste analyse
```sql
SELECT * FROM get_latest_analysis(user_id);
-- Eksempel: SELECT * FROM get_latest_analysis(1);
```

### Se alle competences efter kategori
```sql
SELECT category, name, description 
FROM competence 
ORDER BY category, name;
```

### Backup database
```powershell
# Full backup
pg_dump -U postgres developer_skills > backup.sql

# Gendan backup
psql -U postgres -d developer_skills < backup.sql
```

---

## Troubleshooting

### Database forbinder ikke
```bash
# Check PostgreSQL kører
Get-Service postgresql-x64-18

# Test connection
psql -U postgres -d developer_skills -c "SELECT version();"
```

### MCP server starter ikke
```bash
# Check uv
uv --version

# Geninstaller dependencies
uv sync

# Check .env fil findes
type .env
```

### Tests fejler
```bash
# Se hvilke tests fejler
pytest tests/ -v

# Kør én test ad gangen
pytest tests/test_db_connection.py -v
```

---

## Færdig!

Efter setup kan du:

- ✅ Køre `pytest tests/` uden fejl
- ✅ Starte MCP serveren
- ✅ Se serveren i Claude Desktop
- ✅ Kalde tools fra Claude (fx `analyze_github_developer`)
- ✅ Se data i PostgreSQL

God fornøjelse! 🎉
