import re
from typing import Union, Tuple

class EircodeValidator:
    """
    Validator for Irish postal codes (Eircodes).
    
    An Eircode is a unique 7-character identifier that helps to find any address in Ireland.
    Format: A65 F4E2 (with or without space)
    - First character: Always a letter (A-Z)
    - Second and third characters: Numbers (0-9) only
    - Space (optional)
    - Last four characters: Letters (A-Z) and numbers (0-9)
    """
    
    def __init__(self, allow_empty: bool = True):
        """
        Initialize the validator.
        
        Args:
            allow_empty: If True, empty/None values are considered valid
        """
        self.allow_empty = allow_empty
        
        # Compile regex patterns for performance
        # First char must be letter, followed by two numbers
        self._routing_key_pattern = re.compile(r'^[A-Z][0-9][0-9]$')
        # Last four chars can be any mix of letters and numbers
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
        # Handle None
        if eircode is None:
            return (True, "") if self.allow_empty else (False, "Eircode is required")
            
        # Handle empty or whitespace strings
        if isinstance(eircode, str):
            if not eircode.strip():
                return (True, "") if self.allow_empty else (False, "Eircode is required")
            
            # Remove spaces and convert to uppercase
            eircode = eircode.strip().replace(" ", "").upper()
            
            # Check length
            if len(eircode) != 7:
                return False, "Eircode must be 7 characters (excluding space)"
                
            # Split into routing key and unique identifier
            routing_key = eircode[:3]
            unique_id = eircode[3:]
            
            # Validate routing key (first letter followed by two numbers)
            if not self._routing_key_pattern.match(routing_key):
                return False, "Invalid routing key format - must be letter followed by two numbers"
                
            # Validate unique identifier (last 4 characters)
            if not self._unique_id_pattern.match(unique_id):
                return False, "Invalid unique identifier format - must be letters or numbers"
                
            return True, ""
        
        return False, "Eircode must be a string"

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
            
        eircode = eircode.strip().replace(" ", "").upper()
        return f"{eircode[:3]} {eircode[3:]}" if len(eircode) >= 4 else eircode