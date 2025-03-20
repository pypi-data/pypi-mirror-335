# Code Generation Principles

I write clean, modular, and well-architected code following these core principles:

1. Project Structure
```
/src
  /core          # Core functionality and base classes
  /tasks         # Task-specific implementations  
  /utils         # Shared utilities
  /config        # Configuration files
  /prompts       # Templates and prompts (if needed)
```

2. Code Organization
- Clear separation of concerns
- Single responsibility principle
- Interface-based design
- Consistent file naming
- Logical component grouping

3. Class Implementation Pattern
```python
class ComponentName:
    def __init__(self):
        """Initialize with clear docstring."""
        self._setup_internal_state()
        
    @property 
    def name(self):
        """Properties with type hints."""
        return self._name

    def public_method(self, arg: Type) -> ReturnType:
        """
        Clear method documentation.
        
        Args:
            arg: Description
            
        Returns:
            Description
        """
        # Implementation
```

4. Error Handling
```python
def robust_method(self):
    try:
        # Core logic
    except SpecificError as e:
        # Specific handling
    except Exception as e:
        # Generic fallback
    finally:
        # Cleanup
```

5. Configuration Management
```python
# config.py
class Config:
    def __init__(self, **kwargs):
        self.param1 = kwargs.get('param1', default1)
        self.param2 = kwargs.get('param2', default2)
```

# Code Quality Standards

1. Documentation
- Clear module/class/method docstrings
- Usage examples in docstrings
- Type hints for public interfaces
- README with setup/usage instructions

2. Modularity
- Small, focused functions
- Clear interfaces
- Minimal dependencies
- Reusable components

3. Testing
- Unit tests for core functionality
- Integration tests for workflows
- Clear test organization
- Meaningful assertions

4. Error Handling
- Specific exception types
- Meaningful error messages
- Proper cleanup in finally blocks
- Logging for debugging

# Implementation Patterns

1. Base Classes
```python
class BaseComponent:
    """Base class with shared functionality."""
    
    def __init__(self):
        self._setup()
    
    @abstractmethod
    def _setup(self):
        """Setup required by subclasses."""
        pass
```

2. Factory Methods
```python
class ComponentFactory:
    @staticmethod
    def create(component_type: str) -> BaseComponent:
        """Create specific component instance."""
        if component_type == "type1":
            return Component1()
        elif component_type == "type2":
            return Component2()
```

3. Configuration Loading
```python
def load_config(path: str) -> Config:
    """Load configuration with validation."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(**data)
```

4. Utility Functions
```python
def process_data(data: List[Dict]) -> Dict[str, Any]:
    """
    Process data with clear type hints.
    
    Args:
        data: Input data structure
        
    Returns:
        Processed results
    """
    results = {}
    for item in data:
        # Processing logic
    return results
```

# Best Practices

1. Naming Conventions
- CamelCase for classes
- snake_case for functions/variables
- CAPS for constants
- Meaningful descriptive names

2. Code Organization
- Related code grouped together
- Clear file/module purpose
- Consistent import order
- Minimal circular dependencies

3. Comments and Documentation
- Explain why, not what
- Document non-obvious decisions
- Keep comments up to date
- Include examples

4. Code Style
- Consistent indentation
- Proper spacing
- Line length limits
- Clear block structure

5. Performance Considerations
- Efficient algorithms
- Resource management
- Caching when appropriate
- Optimization notes

When writing code, I will:
1. Follow consistent style and organization
2. Include proper documentation
3. Implement error handling
4. Consider edge cases
5. Focus on maintainability
6. Provide usage examples