#from inventory.src.models import Category, Type, Subtype, Item, String

def assertIsInstance(obj: object, cls: type):
	assert isinstance(obj, cls), f"Expected instance of {cls}, got {type(obj)}"

def assertIn(member: str, container: str):
	assert member in container, f"Expected {member} in {container}"

def assertEqual(a: object, b: object):
    assert a == b, f"Expected {a} to equal {b}"

def assertTrue(expr: bool):
    assert expr, f"Expected expression to be True"
    
def assertFalse(expr: bool):
    assert not expr, "Expected expression to be False"