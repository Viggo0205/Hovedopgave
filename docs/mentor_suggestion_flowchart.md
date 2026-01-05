# Suggest Mentors - Flowchart

Dette flowchart viser processen for `suggest_mentors` funktionen (User Story 20).

**Status:** ❌ IKKE IMPLEMENTERET ENDNU

```mermaid
flowchart TD
    Start([Start: suggest_mentors]) --> Input[Input: technology, min_score?, department?]
    Input --> ValidateInput{Teknologi<br/>angivet?}
    
    ValidateInput -->|Nej| ErrorInput[Return error:<br/>Teknologi påkrævet]
    ValidateInput -->|Ja| LoadProfiles[Load alle developer profiles<br/>fra database]
    
    LoadProfiles --> LoadSuccess{Profiler<br/>loaded?}
    LoadSuccess -->|Nej| ErrorLoad[Return error:<br/>Ingen profiler fundet]
    LoadSuccess -->|Ja| FilterTech[Filtrer: Udviklere med<br/>kompetence i teknologien]
    
    FilterTech --> HasDepartment{Department<br/>filter angivet?}
    HasDepartment -->|Ja| FilterDept[Filtrer: Samme afdeling]
    HasDepartment -->|Nej| SetMinScore
    
    FilterDept --> SetMinScore[Sæt min_score<br/>Default: 0.7 hvis ikke angivet]
    SetMinScore --> FilterScore[Filtrer: score >= min_score<br/>for den specifikke teknologi]
    
    FilterScore --> SortCandidates[Sortér kandidater efter:<br/>1. Skill score DESC<br/>2. Confidence score DESC<br/>3. Experience months DESC]
    
    SortCandidates --> AddMetadata[Tilføj metadata til hver kandidat:<br/>- skill_level<br/>- confidence_score<br/>- experience_months<br/>- related_skills<br/>- availability_indicator]
    
    AddMetadata --> CheckResults{Mentorer<br/>fundet?}
    
    CheckResults -->|Nej| NoMentors[Return:<br/>- success: True<br/>- mentors: []<br/>- message: Ingen kvalificerede mentorer]
    CheckResults -->|Ja| LimitResults[Begræns til top 10 mentorer]
    
    LimitResults --> AddDisclaimer[Tilføj disclaimer:<br/>"Dette er automatiske forslag<br/>baseret på kompetencedata.<br/>Endelig beslutning kræver<br/>menneskelig vurdering"]
    
    AddDisclaimer --> ReturnSuccess[Return success response:<br/>- technology<br/>- mentors liste<br/>- filter_criteria<br/>- total_candidates<br/>- disclaimer<br/>- generated_at]
    
    ErrorInput --> End([End])
    ErrorLoad --> End
    NoMentors --> End
    ReturnSuccess --> End
    
    style Start fill:#90EE90,stroke:#2E7D32,stroke-width:3px,color:#000
    style End fill:#FFB6C1,stroke:#C62828,stroke-width:3px,color:#000
    style ReturnSuccess fill:#81C784,stroke:#2E7D32,stroke-width:2px,color:#000
    style ErrorInput fill:#E57373,stroke:#C62828,stroke-width:2px,color:#000
    style ErrorLoad fill:#E57373,stroke:#C62828,stroke-width:2px,color:#000
    style NoMentors fill:#FFF59D,stroke:#F57C00,stroke-width:2px,color:#000
    style AddDisclaimer fill:#FFE082,stroke:#F57C00,stroke-width:2px,color:#000
    style SortCandidates fill:#FFF59D,stroke:#F57C00,stroke-width:2px,color:#000
```

## Nøglepunkter

1. **Input validering**: Teknologi er påkrævet, min_score og department er optional
2. **Database query**: Henter alle developer profiles med skill assessment data
3. **Filtrering**: Multi-level filtering baseret på teknologi, score og department
4. **Sortering**: Multi-criteria sortering for at finde de bedste mentorer
5. **Metadata enrichment**: Tilføjer relevant information til hver mentor-kandidat
6. **Disclaimer**: Klar kommunikation om at det er automatiske forslag
7. **Response**: Returnerer struktureret liste eller tom liste hvis ingen match

## User Story

**Som** MCP-server  
**vil jeg** kunne foreslå potentielle mentorer i organisationen baseret på høje kompetencescores  
**så** vidensdeling kan styrkes.

## Funktionelle Krav

### 1. Identificere udviklere med høje scores
- [x] System kan hente og analysere kompetencescores
- [ ] **NYT**: System kan filtrere efter specifik teknologi
- [ ] **NYT**: System kan filtrere efter minimum score threshold

### 2. Sortere og returnere mentorforslag
- [ ] **NYT**: Sortering efter multiple kriterier (score, confidence, erfaring)
- [ ] **NYT**: Returnere struktureret liste med mentordetaljer
- [ ] **NYT**: Inkludere relevante metadata for hver kandidat

### 3. Simple filtre (afdeling etc.)
- [ ] **NYT**: Department/afdeling filter
- [ ] **NYT**: Availability status (hvis tilgængeligt i data)
- [ ] **NYT**: Andre organisatoriske filtre

---

## Non-Funktionelle Krav

### 1. Performance
- Genbruger eksisterende skill scores fra database
- Ingen tung beregning ved hver forespørgsel
- Skal kunne håndtere 100+ developer profiles uden delay

### 2. Etisk disclaimer
- **VIGTIGT**: Klar disclaimer at det er automatiske forslag
- Undgå misbrug ved at præcisere at det ikke er automatiske beslutninger
- Mennesker skal træffe endelige mentorbeslutninger

---

## Eksempel Response

```json
{
  "success": true,
  "technology": "Python",
  "filter_criteria": {
    "min_score": 0.7,
    "department": "Engineering",
    "time_range_months": 12
  },
  "total_candidates": 15,
  "mentors": [
    {
      "username": "alice_dev",
      "display_name": "Alice Developer",
      "skill_level": "expert",
      "score": 0.95,
      "confidence": 0.92,
      "experience_months": 36,
      "related_skills": ["Django", "Flask", "FastAPI"],
      "department": "Engineering",
      "availability_indicator": "active",
      "profile_last_updated": "2026-01-01T10:00:00Z"
    },
    {
      "username": "bob_senior",
      "display_name": "Bob Senior",
      "skill_level": "advanced",
      "score": 0.88,
      "confidence": 0.85,
      "experience_months": 24,
      "related_skills": ["Python", "AWS", "Docker"],
      "department": "Engineering",
      "availability_indicator": "active",
      "profile_last_updated": "2025-12-28T15:30:00Z"
    }
  ],
  "disclaimer": "Dette er automatiske forslag baseret på kompetencedata. Endelig beslutning om mentor-match kræver menneskelig vurdering af personlig egnethed, tilgængelighed og interesse.",
  "generated_at": "2026-01-04T12:00:00Z"
}
```

## Visualisering

Åbn denne fil i VS Code og tryk `Ctrl+Shift+V` for at se flowchartet i preview mode.
