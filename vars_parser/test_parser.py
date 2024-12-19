from datetime import datetime
from typing import Dict, Any
from .expression import Expression
from .condition import Condition
from .data_object import DataObject
from .operators import ObjectOperator, ExpressionOperator, ConditionOperator

def test_parser():
    # Test data
    state = {
        "movies": [
            {
                "title": "Movie 1",
                "status": "active",
                "release_date": "2023-10-15",
                "rating": 4.5,
                "tags": ["action", "drama"]
            },
            {
                "title": "Movie 2",
                "status": "canceled",
                "release_date": "2022-09-01",
                "rating": 3.8,
                "tags": ["comedy"]
            },
            {
                "title": "Movie 3",
                "status": "active",
                "release_date": "2023-05-01",
                "rating": 4.2,
                "tags": ["drama"]
            }
        ],
        "user": {
            "profile": {
                "firstname": "John",
                "lastname": "Doe"
            },
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
    }

    DataObject.potential_sources['state'] = state

    # Test cases
    test_cases = [
        # Simple data object access
        {
            "name": "Simple state access",
            "expression": "state.movies",
            "expected_length": 3
        },
        # Nested data object access
        {
            "name": "Nested state access",
            "expression": "state.user.profile.firstname",
            "expected_value": "John"
        },
        # Single condition
        {
            "name": "Single condition",
            "expression": "state.movies WHERE status == active",
            "expected_length": 2
        },
        # Multiple conditions with AND
        {
            "name": "Multiple conditions (AND)",
            "expression": "state.movies WHERE status == active AND rating > 4.0",
            "expected_length": 2
        },
        # Contains operator
        {
            "name": "Contains operator",
            "expression": "state.movies WHERE tags CONTAINS drama",
            "expected_length": 2
        },
        # Object operator (concatenation)
        {
            "name": "String concatenation",
            "expression": "state.user.profile.firstname + state.user.profile.lastname",
            "expected_value": "John Doe"
        }
    ]

    # Run tests
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Expression: {test_case['expression']}")
        
        try:
            # Parse and evaluate expression
            expression = Expression(test_case['expression'])
            result = expression.evaluate()
            
            # Verify result
            if 'expected_length' in test_case:
                assert isinstance(result, list), "Expected list result"
                assert len(result) == test_case['expected_length'], \
                    f"Expected length {test_case['expected_length']}, got {len(result)}"
                print(f"Result (length={len(result)}): {result}")
            
            elif 'expected_value' in test_case:
                assert result == test_case['expected_value'], \
                    f"Expected value {test_case['expected_value']}, got {result}"
                print(f"Result: {result}")
            
            print("✅ Test passed")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise

    # Test individual components
    print("\nTesting individual components:")
    
    # Test DataObject
    print("\nTesting DataObject:")
    data_obj = DataObject("state.movies")
    assert data_obj.parsed, "DataObject parsing failed"
    assert data_obj.source == "state", "Wrong source"
    assert data_obj.path == "movies", "Wrong path"
    print("✅ DataObject tests passed")
    
    # Test Condition
    print("\nTesting Condition:")
    condition = Condition("WHERE status == active")
    assert condition.parsed, "Condition parsing failed"
    assert condition.attribute.name == "status", "Wrong attribute"
    assert condition.operator.symbol == "==", "Wrong operator"
    assert condition.value.processed == "active", "Wrong value"
    print("✅ Condition tests passed")
    
    # Test Operators
    print("\nTesting Operators:")
    
    # Test ConditionOperator
    cond_op = ConditionOperator("==")
    assert cond_op.evaluate(5, 5), "Condition operator failed"
    assert not cond_op.evaluate(5, 6), "Condition operator failed"
    
    # Test ExpressionOperator
    expr_op = ExpressionOperator("AND", 0)
    assert expr_op.evaluate(True, True), "Expression operator failed"
    assert not expr_op.evaluate(True, False), "Expression operator failed"
    
    # Test ObjectOperator
    obj_op = ObjectOperator("+ ", 0)
    assert obj_op.evaluate("Hello", "World") == "Hello World", "Object operator failed"
    assert obj_op.evaluate(1, 2) == 3, "Object operator failed"
    
    print("✅ Operator tests passed")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_parser()
