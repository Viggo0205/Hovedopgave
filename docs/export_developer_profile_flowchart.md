# Export Developer Profile - Flowchart

Dette flowchart viser processen for `export_developer_profile` funktionen.

```mermaid
flowchart TD
    Start([Start: export_developer_profile]) --> Input[Input: username, output_path?, format]
    Input --> Init[Initialize GitHubService & GitHubAnalyzer]
    Init --> Analyze[Kald analyzer.analyze_developer username]
    Analyze --> AnalyzeSuccess{Analyse<br/>success?}
    
    AnalyzeSuccess -->|Ja| Structure[Strukturer export_data:<br/>- export_metadata<br/>- developer_profile]
    AnalyzeSuccess -->|Nej| Error1[Exception caught]
    
    Structure --> CheckPath{output_path<br/>provided?}
    
    CheckPath -->|Nej| CreateDefault[Opret ./exports/ directory<br/>Sæt path = ./exports/username_profile.json]
    CheckPath -->|Ja| EnsureParent[Sikr parent directory eksisterer]
    
    CreateDefault --> WriteFile[Skriv JSON til fil med:<br/>- indent=2<br/>- ensure_ascii=False]
    EnsureParent --> WriteFile
    
    WriteFile --> WriteSuccess{Fil skrevet<br/>success?}
    
    WriteSuccess -->|Ja| GetSize[Hent file size]
    WriteSuccess -->|Nej| Error2[Exception caught]
    
    GetSize --> ReturnSuccess[Return success response:<br/>- file_path<br/>- records_exported: 1<br/>- file_size_bytes<br/>- data_sanitized: True]
    
    Error1 --> ReturnError[Return error response:<br/>- success: False<br/>- error_message]
    Error2 --> ReturnError
    
    ReturnSuccess --> End([End])
    ReturnError --> End
    
    style Start fill:#90EE90,stroke:#2E7D32,stroke-width:3px,color:#000
    style End fill:#FFB6C1,stroke:#C62828,stroke-width:3px,color:#000
    style ReturnSuccess fill:#81C784,stroke:#2E7D32,stroke-width:2px,color:#000
    style ReturnError fill:#E57373,stroke:#C62828,stroke-width:2px,color:#000
    style WriteFile fill:#FFF59D,stroke:#F57C00,stroke-width:2px,color:#000
    style Structure fill:#FFF59D,stroke:#F57C00,stroke-width:2px,color:#000
```

## Nøglepunkter

1. **Input validering**: Modtager username (påkrævet) og optional output_path
2. **Analyse-fase**: Henter kompetencedata via GitHub analyzer
3. **Datastrukturering**: Bygger export_data med metadata og saniteret profil
4. **Path håndtering**: Auto-genererer standard path eller bruger custom path
5. **Fil-skrivning**: Gemmer JSON med formatting (indent + UTF-8)
6. **Response**: Returnerer success med file metadata eller error ved fejl

## Visualisering

Åbn denne fil i VS Code og tryk `Ctrl+Shift+V` for at se flowchartet i preview mode.
