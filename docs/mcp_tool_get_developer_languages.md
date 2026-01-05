# MCP Tool: get_developer_languages

## Beskrivelse
En MCP-tool der henter alle programmeringssprog fra en developers GitHub-profil, organiseret efter kategorier og med identifikation af top programmeringssprog.

## Arkitektur

### Lag-struktur (følger projektets arkitektur)

1. **MCP Tool Layer** (`src/server.py`)
   - `get_developer_languages(username)` - MCP endpoint
   - Håndterer kun HTTP/MCP requests og responses
   - Kalder analyzer for business logic

2. **Analyzer Layer** (`src/analyzers/github_analyzer.py`)
   - `get_languages_by_category(username)` - Business logic
   - Processerer og organiserer sprog-data
   - Kategoriserer sprog efter LANGUAGE_CATEGORIES
   - Identificerer top programmeringssprog

3. **Service Layer** (`src/services/github_service.py`)
   - `get_user_profile(username)` - API kald
   - `get_user_repositories(username)` - API kald
   - `get_language_data(repositories)` - Data aggregering
   - Håndterer al kommunikation med GitHub API

4. **Shared/Constants** (`src/shared/language_categories.py`)
   - `LANGUAGE_CATEGORIES` - Sprog kategorier
   - `get_category_for_language(language)` - Kategori lookup

## Brug

### Fra MCP Client (Claude Desktop)
```json
{
  "tool": "get_developer_languages",
  "arguments": {
    "username": "Viggo0205"
  }
}
```

### Fra Python kode
```python
from services.github_service import GitHubService
from analyzers.github_analyzer import GitHubAnalyzer

github_service = GitHubService()
analyzer = GitHubAnalyzer(github_service)

result = analyzer.get_languages_by_category("Viggo0205")
```

## Output Format

```json
{
  "username": "Viggo0205",
  "top_programming_languages": [
    {
      "language": "C#",
      "rank": "Primært programmeringssprog",
      "total_lines": 3612872,
      "level": "Expert",
      "repositories": 25
    },
    {
      "language": "Java",
      "rank": "Sekundært sprog",
      "total_lines": 174237,
      "level": "Expert",
      "repositories": 1
    }
  ],
  "languages_by_category": {
    "Programming Languages": [...],
    "Web Frontend": [...],
    "Backend/Server": [...],
    "Mobile Development": [...],
    "Data/Analytics": [...],
    "Other Technologies": [...]
  },
  "total_languages": 13,
  "total_repositories": 41,
  "analysis_date": "2026-01-05T..."
}
```

## Kategorier

Sprog organiseres i følgende kategorier:

1. **Programming Languages**: Python, Java, JavaScript, C#, C++, Go, Ruby, PHP, Swift, Kotlin
2. **Web Frontend**: HTML, CSS, TypeScript, Vue, React, Angular
3. **Backend/Server**: Node.js, Django, Flask, Spring, ASP.NET
4. **Mobile Development**: Swift, Kotlin, Dart, React Native, Flutter
5. **Data/Analytics**: R, MATLAB, Jupyter Notebook, SQL
6. **Other Technologies**: Sprog der ikke passer i ovenstående kategorier

## Top Programmeringssprog

Top 3 programmeringssprog (kun fra "Programming Languages" kategorien) rangeres som:
1. Primært programmeringssprog
2. Sekundært sprog
3. Tredje mest anvendte sprog

Rangering baseret på antal kodelinjer skrevet.

## Test

Kør test scriptet:
```bash
python test_language_tool.py
```

## Dependencies
- GitHub API token i `.env` fil
- `PyGithub` bibliotek
- MCP server (FastMCP)
