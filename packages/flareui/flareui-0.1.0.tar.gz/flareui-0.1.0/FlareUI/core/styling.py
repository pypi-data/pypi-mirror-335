from typing import Dict, Any, Union

class StyleSheet:
    def __init__(self):
        self._styles: Dict[str, Dict[str, Any]] = {}
        
    def create(self, styles: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        self._styles.update(styles)
        return {k: f'style-{k}' for k in styles.keys()}
        
    def get_styles(self, class_name: str) -> Dict[str, Any]:
        return self._styles.get(class_name, {})
        
    def combine(self, *class_names: str) -> Dict[str, Any]:
        combined = {}
        for name in class_names:
            combined.update(self.get_styles(name))
        return combined
