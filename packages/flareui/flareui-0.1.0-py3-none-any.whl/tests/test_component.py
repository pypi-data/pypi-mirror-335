import pytest
from flareui.core.component import Component

def test_component_creation():
    component = Component()
    assert isinstance(component, Component)
    assert component.children == []

import unittest
from flareui.core.component import Component

class TestComponent(unittest.TestCase):
    def test_component_initialization(self):
        comp = Component({"title": "Test"})
        self.assertEqual(comp.props["title"], "Test")
    
    def test_state_updates(self):
        comp = Component()
        comp.set_state({"count": 1})
        self.assertEqual(comp._state["count"], 1)
