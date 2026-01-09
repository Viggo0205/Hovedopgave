# Sequence Diagrams - Developer Skill Analysis MCP Server

This document contains sequence diagrams for the core user stories of the MCP server.

---

## User Story 7: Data Analysis Flow (Priority 4)
**As an MCP server**, I want to analyze incoming data from Jira and GitHub to extract technologies and their usage frequency, so that a competency score can be created for each developer.

### Sequence Diagram - Part 1: Data Fetching

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px', 'fontFamily':'arial'}}}%%
sequenceDiagram
    autonumber
    actor Client
    participant MCP as MCP Server
    participant GitHub as GitHub Service
    participant Jira as Jira Service

    Client->>MCP: analyze_developer()
    activate MCP
    
    par GitHub Data
        MCP->>GitHub: get_repositories()
        GitHub->>GitHub: Fetch repos + languages
        GitHub-->>MCP: Return data
    and Jira Data
        MCP->>Jira: get_issues()
        Jira->>Jira: Fetch assigned issues
        Jira-->>MCP: Return data
    end

    MCP->>MCP: Prepare for analysis
    deactivate MCP
```

### Sequence Diagram - Part 2: Analysis & Scoring

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px', 'fontFamily':'arial'}}}%%
sequenceDiagram
    autonumber
    participant MCP as MCP Server
    participant GitHub as GitHub Analyzer
    participant Jira as Jira Analyzer
    participant Skills as Skill Processor

    MCP->>GitHub: analyze_data()
    GitHub->>GitHub: Extract tech stack
    GitHub-->>MCP: Skills + metrics

    MCP->>Jira: analyze_data()
    Jira->>Jira: Extract tech stack
    Jira-->>MCP: Skills + metrics

    MCP->>Skills: process_all()
    Skills->>Skills: Merge sources
    Skills->>Skills: Calculate scores
    Skills-->>MCP: Final results
```

### Sequence Diagram - Part 3: Data Persistence

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px', 'fontFamily':'arial'}}}%%
sequenceDiagram
    autonumber
    participant MCP as MCP Server
    participant DB as Database
    actor Client

    MCP->>DB: save_skills()
    activate DB
    DB->>DB: Upsert developer
    DB->>DB: Upsert skills
    DB->>DB: Link records
    DB-->>MCP: Confirmation
    deactivate DB

    MCP-->>Client: Return analysis
```

### Key Components

1. **Parallel Data Fetching**: GitHub and Jira data are fetched simultaneously for efficiency
2. **Analyzers**: Separate analyzers process each data source independently
3. **Skill Processor**: Merges and normalizes data from both sources
4. **Competency Scoring**: Calculates proficiency based on activity frequency and recency
5. **Database Persistence**: Stores structured skill data with relationships

---

## User Story 12: Query Developer Skills (Priority 5)
**As a project leader**, I want to query the MCP server to get a list of developers with specific competencies, so that I can use the data in other systems.

### Sequence Diagram

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px', 'fontFamily':'arial'}}}%%
sequenceDiagram
    autonumber
    actor User as Project Leader
    participant MCP as MCP Server
    participant Service as Skill Service
    participant DB as Database

    User->>MCP: Query developers<br/>with skill X
    activate MCP
    
    MCP->>MCP: Validate input
    
    alt Invalid Input
        MCP-->>User: Error
    else Valid Input
        MCP->>Service: Find developers
        activate Service
        
        Service->>DB: Query by skill
        DB-->>Service: Raw results
        
        Service->>Service: Process data
        Service->>Service: Sanitize output
        Service-->>MCP: Clean results
        deactivate Service

        MCP-->>User: Developer list
    end
    deactivate MCP
```

### Key Components

1. **Input Validation**: Ensures skill names and proficiency levels are valid
2. **Filtered Query**: Database queries with skill and proficiency filters
3. **Data Aggregation**: Combines skill data from multiple sources
4. **Sanitization**: Removes sensitive information before export
5. **Structured Response**: Returns standardized JSON format

### Response Format Example

```json
{
  "skill": "Python",
  "min_level": "intermediate",
  "developers": [
    {
      "username": "john_doe",
      "skills": [
        {
          "name": "Python",
          "proficiency": "advanced",
          "competency_score": 85,
          "last_used": "2025-12-15"
        }
      ],
      "total_commits": 342,
      "total_issues": 28
    }
  ],
  "total_count": 5
}
```

---

## User Story 9: Calculate Competency Level (Priority 3)
**As an MCP server**, I want to calculate a competency level for each technology based on activity volume, so that competencies can be compared between developers.

### Sequence Diagram

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'fontSize':'16px', 'fontFamily':'arial'}}}%%
sequenceDiagram
    autonumber
    participant Processor as Skill Processor
    participant Scorer as Competency Scorer
    participant DB as Database

    Processor->>Scorer: Calculate score
    activate Scorer

    Scorer->>Scorer: Extract metrics
    Note over Scorer: Commits, issues,<br/>last used, projects

    Scorer->>Scorer: Frequency score
    Note over Scorer: (commits × 2) + issues

    Scorer->>Scorer: Recency score
    Note over Scorer: Apply time decay

    Scorer->>Scorer: Normalize (0-100)
    
    Scorer->>Scorer: Assign level
    Note over Scorer: Beginner/Intermediate<br/>Advanced/Expert

    Scorer-->>Processor: Final score + level
    deactivate Scorer

    Processor->>DB: Save results
```
**Recency Factor:**
- Last 3 months: 1.0
- 3-6 months: 0.9
- 6-12 months: 0.7
- 12-24 months: 0.4
- 24+ months: 0.2

**Proficiency Levels:**
- **Beginner** (0-30): Limited experience
- **Intermediate** (31-60): Regular use
- **Advanced** (61-85): Extensive experience
- **Expert** (86-100): Deep expertise

---

## Recommended VS Code Extensions

### Essential
1. **Mermaid Chart** (`bierner.markdown-mermaid`)
   - Official Mermaid preview in Markdown files
   - Live preview with auto-refresh
   - Export diagrams as SVG/PNG

2. **Markdown Preview Mermaid Support** (`bierner.markdown-mermaid`)
   - Integrates with VS Code's built-in Markdown preview
   - No additional setup required

### Enhanced Visualization
3. **Draw.io Integration** (`hediet.vscode-drawio`)
   - Advanced diagram editing
   - Export to multiple formats
   - Interactive editing

4. **PlantUML** (`jebbs.plantuml`)
   - Alternative diagram syntax
   - More detailed sequence diagrams
   - Professional styling options

### Installation Command
```bash
code --install-extension bierner.markdown-mermaid
code --install-extension hediet.vscode-drawio
```

---

## Viewing These Diagrams

1. **In VS Code**: Open this file and press `Ctrl+Shift+V` (Windows) or `Cmd+Shift+V` (Mac) for preview
2. **In GitHub**: Diagrams render automatically in Markdown files
3. **Export**: Use Mermaid Live Editor (mermaid.live) for high-quality exports

---

## Notes

- These diagrams represent the **happy path** flow
- Error handling and edge cases are simplified for clarity
- Actual implementation may include additional validation and retry logic
- Database transactions and connection pooling are abstracted
