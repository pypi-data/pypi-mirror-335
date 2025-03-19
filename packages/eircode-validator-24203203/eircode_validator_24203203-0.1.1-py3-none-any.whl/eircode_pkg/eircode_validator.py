import re
from typing import Union, Tuple

class EircodeValidator:
    """
    Validator for Irish postal codes (Eircodes).
    
    An Eircode is a unique 7-character identifier that helps to find any address in Ireland.
    Format: A65 F4E2 (with or without space)
    - First character: Always a letter
    - Second and third characters: Numbers or letters
    - Space (optional)
    - Last four characters: Numbers and letters
    """
    
    def __init__(self, allow_empty: bool = True):
        """
        Initialize the validator.
        
        Args:
            allow_empty: If True, empty/None values are considered valid
        """
        self.allow_empty = allow_empty
        
        # Compile regex patterns for performance
        self._routing_key_pattern = re.compile(r'^[A-Z][A-Z0-9]{2}$')
        self._unique_id_pattern = re.compile(r'^[A-Z0-9]{4}$')

    def validate(self, eircode: Union[str, None]) -> Tuple[bool, str]:
        """
        Validate an Eircode.
        
        Args:
            eircode: The Eircode to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message will be empty
        """
        # Handle empty values
        if not eircode:
            return (True, "") if self.allow_empty else (False, "Eircode is required")
            
        # Remove spaces and convert to uppercase
        eircode = eircode.replace(" ", "").upper()
        
        # Check length
        if len(eircode) != 7:
            return False, "Eircode must be 7 characters (excluding space)"
            
        # Split into routing key and unique identifier
        routing_key = eircode[:3]
        unique_id = eircode[3:]
        
        # Validate routing key (first 3 characters)
        if not self._routing_key_pattern.match(routing_key):
            return False, "Invalid routing key format - must be letter followed by two letters/numbers"
            
        # Validate unique identifier (last 4 characters)
        if not self._unique_id_pattern.match(unique_id):
            return False, "Invalid unique identifier format - must be letters or numbers"
            
        return True, ""

    @staticmethod
    def format(eircode: str) -> str:
        """
        Format an Eircode with proper spacing.
        
        Args:
            eircode: The Eircode to format
            
        Returns:
            Formatted Eircode (e.g., "A65 F4E2")
        """
        if not eircode:
            return ""
            
        eircode = eircode.replace(" ", "").upper()
        return f"{eircode[:3]} {eircode[3:]}" if len(eircode) >= 4 else eircode