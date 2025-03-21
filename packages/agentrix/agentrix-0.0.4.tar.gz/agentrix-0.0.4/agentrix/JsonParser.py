import json
import re
from typing import Any, Dict, List, Optional, Type

class ValidationError(Exception):
    """Exception raised when validation fails for JSON data."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        self.message = message
        super().__init__(f"{message} (field: {field})" if field else message)

class Field:
    """Field descriptor with validation capabilities."""
    
    def __init__(self, field_type: Any, required: bool = True, default: Any = None):
        self.field_type = field_type
        self.required = required
        self.default = default
        self.name = None  # Will be set during class creation
        
    def validate(self, value: Any) -> Any:
        # Handle default for missing values
        if value is None:
            if self.required:
                raise ValidationError(f"Missing required field", self.name)
            return self.default
            
        # Basic type validation
        if self.field_type == str and not isinstance(value, str):
            raise ValidationError(f"Expected string but got {type(value).__name__}", self.name)
        elif self.field_type == int and not isinstance(value, (int, float)) or \
             (isinstance(value, float) and not value.is_integer()):
            raise ValidationError(f"Expected integer but got {type(value).__name__}", self.name)
        elif self.field_type == float and not isinstance(value, (int, float)):
            raise ValidationError(f"Expected float but got {type(value).__name__}", self.name)
        elif self.field_type == bool and not isinstance(value, bool):
            raise ValidationError(f"Expected boolean but got {type(value).__name__}", self.name)
        elif self.field_type == list and not isinstance(value, list):
            raise ValidationError(f"Expected list but got {type(value).__name__}", self.name)
        elif self.field_type == dict and not isinstance(value, dict):
            raise ValidationError(f"Expected dict but got {type(value).__name__}", self.name)
            
        return value

class ModelMeta(type):
    """Metaclass for JsonModel to handle field registration and validation."""
    
    def __new__(mcs, name, bases, namespace):
        fields = {}
        
        # Collect fields from the class definition
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
                
        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)

class JsonModel(metaclass=ModelMeta):
    """Base class for JSON object models with validation."""
    
    def __init__(self, **data):
        """Initialize model from dictionary data."""
        # Process all fields
        for name, field in self.__class__._fields.items():
            value = data.get(name)
            try:
                setattr(self, name, field.validate(value))
            except ValidationError as e:
                raise ValidationError(f"Validation error for field '{name}': {e.message}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JsonModel':
        """Create a model instance from a dictionary."""
        return cls(**data)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for name in self.__class__._fields:
            if hasattr(self, name):
                result[name] = getattr(self, name)
        return result
    
    def __repr__(self) -> str:
        attrs = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__class__._fields 
                          if hasattr(self, name))
        return f"{self.__class__.__name__}({attrs})"

class JsonOutputParser:
    """
    A parser for JSON output that validates and converts the output to a specified model.
    Can handle JSON embedded in markdown code blocks.
    """
    
    def __init__(self, model_cls: Type[JsonModel]):
        """
        Initialize the parser with the target model class.
        
        Args:
            model_cls: The model class to use for validation and parsing
        """
        self.model_cls = model_cls
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from potentially markdown-formatted text.
        Handles cases where JSON is wrapped in code blocks.
        
        Args:
            text: Text that may contain JSON, possibly in a markdown code block
            
        Returns:
            The extracted JSON string
        """
        # Pattern to match JSON content inside markdown code blocks
        # This handles ```json blocks and variations
        code_block_pattern = r'```(?:json)?\s*\n([\s\S]*?)\n```'
        match = re.search(code_block_pattern, text)
        
        if match:
            # Return the content inside the code block
            return match.group(1).strip()
        
        # If no code block is found, return the original text
        return text
    
    def parse(self, text: str) -> JsonModel:
        """
        Parse and validate JSON string according to the specified model.
        Can handle JSON embedded in markdown code blocks.
        
        Args:
            text: A string containing JSON data, possibly in a markdown code block
            
        Returns:
            An instance of the specified model
            
        Raises:
            ValueError: If the input is not valid JSON
            ValidationError: If the JSON data does not match the model schema
        """
        try:
            # First try to extract JSON if it's in a code block
            json_str = self._extract_json(text)
            
            # Parse JSON string to dictionary
            data = json.loads(json_str)
            
            # Validate and convert to model instance
            return self.model_cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    def parse_list(self, text: str) -> List[JsonModel]:
        """
        Parse and validate a JSON string containing a list of objects.
        Can handle JSON embedded in markdown code blocks.
        
        Args:
            text: A string containing JSON array data, possibly in a markdown code block
            
        Returns:
            A list of instances of the specified model
            
        Raises:
            ValueError: If the input is not valid JSON or not a list
            ValidationError: If any item does not match the model schema
        """
        try:
            # First try to extract JSON if it's in a code block
            json_str = self._extract_json(text)
            
            data = json.loads(json_str)
            if not isinstance(data, list):
                raise ValueError("Expected a JSON array but got a different structure")
            
            return [self.model_cls.from_dict(item) for item in data]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")