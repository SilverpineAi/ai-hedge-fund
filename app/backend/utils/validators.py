"""
Validation utilities for data processing
"""

import re
from typing import List, Dict, Any, Tuple
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Returns:
        Tuple of (is_valid, normalized_email)
    """
    if not email or not email.strip():
        return False, ""
    
    try:
        # Validate and normalize email
        valid = validate_email(email.strip())
        return True, valid.email
    except EmailNotValidError:
        return False, email.strip()

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate and normalize phone number
    
    Returns:
        Tuple of (is_valid, normalized_phone)
    """
    if not phone or not phone.strip():
        return False, ""
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone.strip())
    
    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False, phone.strip()
    
    # Format as international number if it looks like US number
    if len(digits_only) == 10:
        formatted = f"+1{digits_only}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        formatted = f"+{digits_only}"
    else:
        formatted = f"+{digits_only}"
    
    return True, formatted

def validate_linkedin_url(url: str) -> Tuple[bool, str]:
    """
    Validate LinkedIn URL format
    
    Returns:
        Tuple of (is_valid, normalized_url)
    """
    if not url or not url.strip():
        return False, ""
    
    url = url.strip()
    
    # Add https:// if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Check if it's a LinkedIn URL
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?',
        r'https?://(?:www\.)?linkedin\.com/pub/[\w\-\.]+/[\w\-\.]+/[\w\-\.]+/[\w\-\.]+/?',
        r'https?://(?:www\.)?linkedin\.com/profile/view\?id=\d+',
    ]
    
    for pattern in linkedin_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return True, url
    
    return False, url

def validate_company_domain(domain: str) -> Tuple[bool, str]:
    """
    Validate company domain format
    
    Returns:
        Tuple of (is_valid, normalized_domain)
    """
    if not domain or not domain.strip():
        return False, ""
    
    domain = domain.strip().lower()
    
    # Remove protocol if present
    domain = re.sub(r'^https?://', '', domain)
    
    # Remove www. if present
    domain = re.sub(r'^www\.', '', domain)
    
    # Remove trailing slash
    domain = domain.rstrip('/')
    
    # Basic domain validation
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
    
    if re.match(domain_pattern, domain):
        return True, domain
    
    return False, domain

def validate_csv_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate CSV data and return validation results
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'valid_records': 0,
        'invalid_records': 0,
        'errors': [],
        'warnings': [],
        'field_stats': {
            'emails_found': 0,
            'emails_valid': 0,
            'phones_found': 0,
            'phones_valid': 0,
            'linkedin_found': 0,
            'linkedin_valid': 0,
            'domains_found': 0,
            'domains_valid': 0,
        }
    }
    
    required_fields = ['full_name']
    
    for i, record in enumerate(data):
        row_num = i + 2  # +2 because of header row and 0-based index
        record_valid = True
        
        # Check required fields
        for field in required_fields:
            if not record.get(field) or not str(record[field]).strip():
                results['errors'].append(f"Row {row_num}: Missing required field '{field}'")
                record_valid = False
        
        # Validate email if present
        if record.get('email'):
            results['field_stats']['emails_found'] += 1
            is_valid, normalized = validate_email_address(record['email'])
            if is_valid:
                results['field_stats']['emails_valid'] += 1
                record['email'] = normalized
            else:
                results['warnings'].append(f"Row {row_num}: Invalid email format '{record['email']}'")
        
        # Validate phone if present
        if record.get('phone'):
            results['field_stats']['phones_found'] += 1
            is_valid, normalized = validate_phone_number(record['phone'])
            if is_valid:
                results['field_stats']['phones_valid'] += 1
                record['phone'] = normalized
            else:
                results['warnings'].append(f"Row {row_num}: Invalid phone format '{record['phone']}'")
        
        # Validate LinkedIn URL if present
        if record.get('linkedin_url'):
            results['field_stats']['linkedin_found'] += 1
            is_valid, normalized = validate_linkedin_url(record['linkedin_url'])
            if is_valid:
                results['field_stats']['linkedin_valid'] += 1
                record['linkedin_url'] = normalized
            else:
                results['warnings'].append(f"Row {row_num}: Invalid LinkedIn URL '{record['linkedin_url']}'")
        
        # Validate company domain if present
        if record.get('company_domain'):
            results['field_stats']['domains_found'] += 1
            is_valid, normalized = validate_company_domain(record['company_domain'])
            if is_valid:
                results['field_stats']['domains_valid'] += 1
                record['company_domain'] = normalized
            else:
                results['warnings'].append(f"Row {row_num}: Invalid domain format '{record['company_domain']}'")
        
        if record_valid:
            results['valid_records'] += 1
        else:
            results['invalid_records'] += 1
    
    return results

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    """
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = f"{name[:250]}.{ext}" if ext else name[:255]
    
    return filename

def validate_file_upload(file_size: int, filename: str, allowed_types: List[str], max_size: int) -> List[str]:
    """
    Validate file upload parameters
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check file size
    if file_size > max_size:
        errors.append(f"File size ({file_size:,} bytes) exceeds maximum allowed size ({max_size:,} bytes)")
    
    # Check file type
    if filename:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_ext not in allowed_types:
            errors.append(f"File type '.{file_ext}' not allowed. Allowed types: {', '.join(allowed_types)}")
    else:
        errors.append("Filename is required")
    
    return errors