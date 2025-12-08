"""Language categorization constants for GitHub analysis."""

# Programming language categories used for skill analysis and expertise areas
LANGUAGE_CATEGORIES = {
    "Programming Languages": ["Python", "Java", "JavaScript", "C#", "C++", "Go", "Ruby", "PHP", "Swift", "Kotlin"],
    "Web Frontend": ["HTML", "CSS", "TypeScript", "Vue", "React", "Angular"],
    "Backend/Server": ["Node.js", "Django", "Flask", "Spring", "ASP.NET"],
    "Mobile Development": ["Swift", "Kotlin", "Dart", "React Native", "Flutter"],
    "Data/Analytics": ["R", "MATLAB", "Jupyter Notebook", "SQL"]
}


def get_language_categories():
    """Get the language categories dictionary."""
    return LANGUAGE_CATEGORIES


def get_all_supported_languages():
    """Get a flat list of all supported languages."""
    languages = []
    for category_languages in LANGUAGE_CATEGORIES.values():
        languages.extend(category_languages)
    return sorted(set(languages))  # Remove duplicates and sort


def get_category_for_language(language: str):
    """Find which category a language belongs to."""
    for category, languages in LANGUAGE_CATEGORIES.items():
        if any(lang.lower() in language.lower() or language.lower() in lang.lower() 
               for lang in languages):
            return category
    return "Other Technologies"