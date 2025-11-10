"""
PII Scrubbing System
Removes personally identifiable information from logs, exports, and databases
Complies with GDPR, Indonesia PDP Law 27/2022, and other privacy regulations
"""
import re
import logging
import json
from typing import Any, Dict, List, Optional
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PIIPattern:
    """PII pattern for detection and scrubbing"""
    name: str
    pattern: str
    replacement: str
    description: str


class PIIScrubber:
    """
    Scrub PII from logs, exports, and data
    
    Features:
    - Email address redaction
    - Phone number redaction  
    - IP address redaction (optional)
    - Custom PII patterns
    - Reversible anonymization (hash-based)
    """
    
    def __init__(self, enable_hashing: bool = True):
        """
        Initialize PII scrubber
        
        Args:
            enable_hashing: Use hash-based anonymization (reversible with salt)
        """
        self.enable_hashing = enable_hashing
        self.hash_salt = self._get_or_create_salt()
        
        # Define PII patterns
        self.patterns = [
            PIIPattern(
                name="email",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                replacement="[EMAIL_REDACTED]",
                description="Email addresses"
            ),
            PIIPattern(
                name="phone",
                pattern=r'\b(?:\+?62|0)[0-9]{9,12}\b',
                replacement="[PHONE_REDACTED]",
                description="Indonesian phone numbers"
            ),
            PIIPattern(
                name="ip_address",
                pattern=r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                replacement="[IP_REDACTED]",
                description="IP addresses"
            ),
            PIIPattern(
                name="nik",
                pattern=r'\b[0-9]{16}\b',
                replacement="[NIK_REDACTED]",
                description="Indonesian NIK (ID number)"
            ),
            PIIPattern(
                name="credit_card",
                pattern=r'\b[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b',
                replacement="[CARD_REDACTED]",
                description="Credit card numbers"
            )
        ]
        
        # Compile regex patterns
        self.compiled_patterns = {
            p.name: re.compile(p.pattern)
            for p in self.patterns
        }
        
        logger.info(f"PII scrubber initialized with {len(self.patterns)} patterns")
    
    def _get_or_create_salt(self) -> str:
        """Get or create salt for hashing"""
        salt_file = "./config/.pii_salt"
        
        if os.path.exists(salt_file):
            with open(salt_file, 'r') as f:
                return f.read().strip()
        
        # Generate new salt
        import secrets
        salt = secrets.token_hex(32)
        
        os.makedirs(os.path.dirname(salt_file), exist_ok=True)
        with open(salt_file, 'w') as f:
            f.write(salt)
        
        os.chmod(salt_file, 0o600)
        
        logger.info("Created new PII anonymization salt")
        
        return salt
    
    def _hash_pii(self, pii_value: str) -> str:
        """Create consistent hash of PII value"""
        combined = f"{self.hash_salt}:{pii_value}"
        hash_obj = hashlib.sha256(combined.encode())
        return hash_obj.hexdigest()[:16]
    
    def scrub_text(self, text: str, anonymize: bool = False) -> str:
        """
        Scrub PII from text
        
        Args:
            text: Input text
            anonymize: Use hash-based anonymization instead of removal
            
        Returns:
            Scrubbed text
        """
        result = text
        
        for pattern_name, regex in self.compiled_patterns.items():
            if anonymize and self.enable_hashing:
                # Replace with hash
                def replace_with_hash(match):
                    pii_value = match.group(0)
                    hash_value = self._hash_pii(pii_value)
                    return f"[{pattern_name.upper()}_{hash_value}]"
                
                result = regex.sub(replace_with_hash, result)
            else:
                # Simple redaction
                pattern = next(p for p in self.patterns if p.name == pattern_name)
                result = regex.sub(pattern.replacement, result)
        
        return result
    
    def scrub_dict(self, data: Dict, keys_to_scrub: Optional[List[str]] = None) -> Dict:
        """
        Scrub PII from dictionary
        
        Args:
            data: Input dictionary
            keys_to_scrub: Optional list of keys to scrub (if None, scrubs all string values)
            
        Returns:
            Dictionary with PII scrubbed
        """
        if keys_to_scrub is None:
            # Default keys that often contain PII
            keys_to_scrub = [
                "email", "phone", "mobile", "address", "name",
                "first_name", "last_name", "full_name",
                "nik", "identity", "passport", "license"
            ]
        
        result = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                if key.lower() in [k.lower() for k in keys_to_scrub]:
                    # Scrub this field
                    result[key] = self.scrub_text(value, anonymize=True)
                else:
                    # Check for PII patterns in any string
                    result[key] = self.scrub_text(value, anonymize=False)
            
            elif isinstance(value, dict):
                # Recursively scrub nested dicts
                result[key] = self.scrub_dict(value, keys_to_scrub)
            
            elif isinstance(value, list):
                # Scrub list items
                result[key] = [
                    self.scrub_dict(item, keys_to_scrub) if isinstance(item, dict)
                    else self.scrub_text(item, anonymize=False) if isinstance(item, str)
                    else item
                    for item in value
                ]
            
            else:
                # Pass through non-string values
                result[key] = value
        
        return result
    
    def scrub_log_line(self, log_line: str) -> str:
        """Scrub PII from log line"""
        return self.scrub_text(log_line, anonymize=False)
    
    def create_export_safe_copy(self, data: Dict) -> Dict:
        """
        Create export-safe copy of data with all PII removed
        
        Args:
            data: Original data
            
        Returns:
            Export-safe copy
        """
        return self.scrub_dict(data)
    
    def get_pii_stats(self, text: str) -> Dict[str, int]:
        """Get count of PII instances found in text"""
        stats = {}
        
        for pattern_name, regex in self.compiled_patterns.items():
            matches = regex.findall(text)
            if matches:
                stats[pattern_name] = len(matches)
        
        return stats


# Global instance
pii_scrubber = PIIScrubber()



















