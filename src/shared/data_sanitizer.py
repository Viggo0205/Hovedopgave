"""
Data sanitization utilities for removing sensitive personal information.

This module ensures compliance with data protection requirements by removing
or masking sensitive fields before data is exposed via API responses.
"""

from typing import Any, Dict, List, Set


# Sensitive fields that should be removed from API responses
SENSITIVE_FIELDS: Set[str] = {
    'email',
    'emailAddress',
    'email_address',
    'phone',
    'phoneNumber',
    'phone_number',
    'address',
    'personalEmail',
    'personal_email',
    'privateEmail',
    'private_email',
}


def sanitize_developer_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive personal information from developer profile data.
    
    This function recursively removes fields containing personal identifiable
    information (PII) such as email addresses and phone numbers, while preserving
    all non-sensitive data needed for skill analysis.
    
    Args:
        data: Dictionary containing developer profile data
        
    Returns:
        Sanitized dictionary with sensitive fields removed
        
    Examples:
        >>> profile = {"username": "john", "email": "john@example.com", "repos": 10}
        >>> sanitize_developer_profile(profile)
        {"username": "john", "repos": 10}
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        # Skip sensitive fields entirely
        if key in SENSITIVE_FIELDS:
            continue
        
        # Recursively sanitize nested dictionaries
        if isinstance(value, dict):
            sanitized[key] = sanitize_developer_profile(value)
        
        # Recursively sanitize lists of dictionaries
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_developer_profile(item) if isinstance(item, dict) else item
                for item in value
            ]
        
        # Keep all other values
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sanitize a list of developer profiles or data objects.
    
    Args:
        data_list: List of dictionaries to sanitize
        
    Returns:
        List of sanitized dictionaries
    """
    return [sanitize_developer_profile(item) for item in data_list]


def mask_email(email: str) -> str:
    """
    Mask an email address for logging or display purposes.
    
    Args:
        email: Email address to mask
        
    Returns:
        Masked email (e.g., "j***@example.com")
        
    Examples:
        >>> mask_email("john.doe@example.com")
        "j***@example.com"
    """
    if not email or '@' not in email:
        return "***@***.***"
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 1:
        masked_local = "*"
    else:
        masked_local = local[0] + "***"
    
    return f"{masked_local}@{domain}"


def get_sensitive_field_summary(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Analyze data to count how many sensitive fields would be removed.
    
    Useful for logging and auditing data sanitization operations.
    
    Args:
        data: Dictionary to analyze
        
    Returns:
        Dictionary mapping field names to count of occurrences
    """
    summary = {}
    
    def count_sensitive_fields(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                if key in SENSITIVE_FIELDS:
                    summary[key] = summary.get(key, 0) + 1
                
                count_sensitive_fields(value, current_path)
        
        elif isinstance(obj, list):
            for item in obj:
                count_sensitive_fields(item, path)
    
    count_sensitive_fields(data)
    return summary
