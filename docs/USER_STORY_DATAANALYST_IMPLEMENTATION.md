# User Story Implementation: Dataanalytiker JSON Export

## User Story
**Som dataanalytiker vil jeg kunne hente kompetencedata for en udvikler som JSON via et API, så jeg kan foretage videre analyser i eksterne værktøjer.**

## Implementation Status: ✅ COMPLETED

---

## Funktionelle Krav - Coverage

### FK-D1.1: GET-endpoint med JSON format ✅
**Status:** Implementeret

**Løsning:**
- MCP tool: `analyze_github_developer(username)` - Returnerer komplet profil som JSON
- MCP tool: `export_developer_profile(username, output_path)` - Eksporterer til fil

**Placering:** `src/server.py` (linje 17-82 og 190-260)

**Eksempel brug via Claude:**
```
User: "Analyser udvikler 'johndoe' og gem som JSON"
Claude → Kalder export_developer_profile → Returnerer fil sti
```

---

### FK-D1.2: Maskering af følsomme personoplysninger ✅
**Status:** Implementeret

**Løsning:**
- Data sanitizer modul der automatisk fjerner alle PII felter
- Følgende felter fjernes:
  - `email`, `emailAddress`, `email_address`
  - `phone`, `phoneNumber`, `phone_number`  
  - `address`, `personalEmail`, `privateEmail`
- Virker rekursivt på nested objekter og lister

**Placering:** `src/shared/data_sanitizer.py`

**Integration:**
- `src/services/github_service.py` - Alle endpoints saniteres
- `src/services/jira_service.py` - Alle endpoints saniteres

**Test coverage:** `test_sanitization.py` - 7 tests, alle bestået ✅

---

## Non-Funktionelle Krav - Coverage

### NFK-D1.1: Velstruktureret JSON schema ✅
**Status:** Implementeret

**Løsning:**
1. **Pydantic response models** (`src/models/api_responses.py`):
   - `DeveloperProfileResponse` - Standardiseret profil struktur
   - `ExportResponse` - Export operation metadata
   - Type validation og consistent field naming

2. **JSON Schema dokumentation** (`docs/developer_profile_schema.json`):
   - JSON Schema Draft 7 compliant
   - Fuld field documentation
   - Examples og validation rules
   - Eksplicit markering af PII exclusion

**Eksempel struktur:**
```json
{
  "username": "johndoe",
  "display_name": "John Doe",
  "language_skills": {
    "Python": {
      "level": "expert",
      "lines_of_code": 50000,
      "percentage_of_work": 45.5
    }
  },
  "total_repositories": 25,
  "analysis_date": "2025-12-08T10:30:00"
}
```

---

## Implementerede Komponenter

### 1. Data Sanitizer (`src/shared/data_sanitizer.py`)
**Funktioner:**
- `sanitize_developer_profile(data)` - Fjern PII fra enkelt profil
- `sanitize_list(data_list)` - Sanitize liste af profiler
- `mask_email(email)` - Masker email til logging (j***@example.com)
- `get_sensitive_field_summary(data)` - Audit logging af PII felter

**Features:**
- Rekursiv sanitization af nested strukturer
- Liste håndtering
- Performance optimeret
- Type-safe

### 2. API Response Models (`src/models/api_responses.py`)
**Models:**
- `DeveloperProfileResponse` - Hovedmodel for udvikler profil
- `LanguageSkill` - Sprog kompetence struktur
- `ExpertiseArea` - Ekspertise område struktur
- `ExportResponse` - Export operation resultat

**Features:**
- Pydantic validation
- Type hints
- JSON schema generation support
- Example data in model config

### 3. Export Tool (`src/server.py`)
**MCP Tool: `export_developer_profile`**

**Parameters:**
- `username: str` - GitHub username (required)
- `output_path: Optional[str]` - Custom fil sti (default: ./exports/{username}_profile.json)
- `format: str` - Format type (default: "json")

**Returns:**
```json
{
  "success": true,
  "file_path": "/absolute/path/to/file.json",
  "records_exported": 1,
  "file_size_bytes": 2048,
  "format": "json",
  "timestamp": "2025-12-08T10:30:00",
  "data_sanitized": true
}
```

### 4. Service Layer Integration
**GitHub Service (`src/services/github_service.py`):**
- ✅ `get_user_profile()` - Sanitized
- ✅ `get_organization_members()` - Sanitized
- ✅ `get_repository_contributors()` - Sanitized

**Jira Service (`src/services/jira_service.py`):**
- ✅ `get_user_profile()` - Sanitized
- ✅ `get_user_issues()` - Sanitized (emails → display names)
- ✅ `get_user_projects()` - Sanitized (lead email → lead name)

---

## Testing

### Test Suite: `test_sanitization.py`
**7 Tests - Alle bestået ✅**

1. ✅ Email removal from simple objects
2. ✅ Nested email removal
3. ✅ List sanitization
4. ✅ Email masking for logging
5. ✅ Sensitive field detection and counting
6. ✅ GitHub member structure
7. ✅ Jira issue structure

**Coverage:**
- Email fjernelse på alle niveauer
- Nested object handling
- List processing
- Real-world data structures (GitHub + Jira)

---

## Data Flow

```
┌─────────────────┐
│  MCP Client     │
│  (Claude/GPT)   │
└────────┬────────┘
         │
         │ 1. Call tool
         ▼
┌─────────────────────────────────────┐
│  MCP Server                         │
│  - analyze_github_developer()       │
│  - export_developer_profile()       │
└────────┬────────────────────────────┘
         │
         │ 2. Fetch data
         ▼
┌─────────────────────────────────────┐
│  Service Layer                      │
│  - GitHubService                    │
│  - JiraService                      │
└────────┬────────────────────────────┘
         │
         │ 3. Sanitize
         ▼
┌─────────────────────────────────────┐
│  Data Sanitizer                     │
│  - Remove email, phone, etc.        │
│  - Recursive processing             │
└────────┬────────────────────────────┘
         │
         │ 4. Validate & Structure
         ▼
┌─────────────────────────────────────┐
│  Response Models                    │
│  - DeveloperProfileResponse         │
│  - Pydantic validation              │
└────────┬────────────────────────────┘
         │
         │ 5. Return/Export
         ▼
┌─────────────────────────────────────┐
│  JSON Output                        │
│  - Sanitized data                   │
│  - No PII                           │
│  - Schema compliant                 │
└─────────────────────────────────────┘
```

---

## Files Created/Modified

### New Files:
1. ✅ `src/shared/data_sanitizer.py` - Data sanitization utilities
2. ✅ `src/models/api_responses.py` - Standardized response models
3. ✅ `test_sanitization.py` - Test suite
4. ✅ `docs/developer_profile_schema.json` - JSON Schema documentation

### Modified Files:
1. ✅ `src/services/github_service.py` - Added sanitization
2. ✅ `src/services/jira_service.py` - Added sanitization + changed email→name
3. ✅ `src/server.py` - Added export_developer_profile tool

---

## GDPR Compliance

### Data Protection Measures:
1. ✅ **No email addresses** in exported data
2. ✅ **No phone numbers** in exported data
3. ✅ **No physical addresses** in exported data
4. ✅ **Automated sanitization** - ikke muligt at "glemme"
5. ✅ **Audit logging** - kan tracke hvilke PII felter der blev fjernet
6. ✅ **Email masking** til logs (j***@example.com)

### Non-sensitive Data Included:
- ✅ Username (public identifier)
- ✅ Display name (public)
- ✅ Company name (public)
- ✅ Bio (public)
- ✅ Repository statistics (public)
- ✅ Programming languages (derived data)
- ✅ Skill assessments (derived data)

---

## Usage Examples

### Via Claude Desktop:

**Example 1: Analyze and view:**
```
User: "Analyser GitHub udvikler 'torvalds'"
Claude: [Calls analyze_github_developer]
Claude: "Linus Torvalds er expert i C med 1.2M lines of code..."
```

**Example 2: Export to file:**
```
User: "Eksporter profil for 'gvanrossum' til JSON fil"
Claude: [Calls export_developer_profile]
Claude: "Profil eksporteret til ./exports/gvanrossum_profile.json"
```

**Example 3: Custom path:**
```
User: "Gem 'johndoe' profil i C:/analyser/developers/"
Claude: [Calls export_developer_profile with path]
Claude: "Gemt til C:/analyser/developers/johndoe_profile.json"
```

---

## Requirements Checklist

### Funktionelle Krav:
- ✅ FK-D1.1: GET-endpoint returnerer JSON
- ✅ FK-D1.2: Følsomme data maskeres/fjernes

### Non-Funktionelle Krav:
- ✅ NFK-D1.1: Velstruktureret JSON schema
- ✅ Konsistent field naming
- ✅ Type validation (Pydantic)
- ✅ JSON Schema documentation
- ✅ ISO 8601 timestamps

---

## Next Steps (Optional Improvements)

### Hvis I vil udvide:
1. **Batch export** - Eksporter flere udviklere på én gang
2. **CSV export** - Alternative format
3. **Filtering** - Vælg hvilke felter der skal med
4. **Aggregation** - Team-niveau analyser
5. **Delta exports** - Kun ændringer siden sidste export
6. **API versioning** - Schema version field

---

## Summary

✅ **User Story er FULDT implementeret**

**Coverage:**
- JSON API endpoint via MCP tools
- Automatisk data sanitization
- PII fjernes konsekvent
- Velstruktureret schema med dokumentation
- Test coverage
- GDPR compliant

**Dataanalytikere kan nu:**
1. Hente sanitized kompetencedata via MCP tools
2. Eksportere til JSON filer
3. Integrere i eksterne værktøjer
4. Stole på konsistent data struktur
5. Være sikre på ingen PII lækage
