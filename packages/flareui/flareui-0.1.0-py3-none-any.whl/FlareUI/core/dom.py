from typing import Dict, List, Any, Optional, Union

class VirtualNode:
    def __init__(
        self,
        tag: str,
        props: Dict[str, Any] = None,
        children: List['VirtualNode'] = None
    ):
        self.tag = tag
        self.props = props or {}
        self.children = children or []
        self.key = props.get('key') if props else None

    def diff(self, old_node: Optional['VirtualNode']) -> List[Dict[str, Any]]:
        patches = []
        if not old_node:
            patches.append({'type': 'CREATE', 'node': self})
        elif self.tag != old_node.tag:
            patches.append({'type': 'REPLACE', 'old': old_node, 'new': self})
        else:
            # Props diff
            prop_patches = self._diff_props(old_node.props)
            if prop_patches:
                patches.append({'type': 'PROPS', 'patches': prop_patches})
            
            # Children diff
            child_patches = self._diff_children(old_node.children)
            patches.extend(child_patches)
            
        return patches

    def _diff_props(self, old_props: Dict[str, Any]) -> Dict[str, Any]:
        patches = {}
        # Check for removed or changed props
        for key, value in old_props.items():
            if key not in self.props:
                patches[key] = None
            elif self.props[key] != value:
                patches[key] = self.props[key]
        
        # Check for new props
        for key, value in self.props.items():
            if key not in old_props:
                patches[key] = value
                
        return patches

    def _diff_children(self, old_children: List['VirtualNode']) -> List[Dict[str, Any]]:
        patches = []
        max_len = max(len(self.children), len(old_children))
        
        for i in range(max_len):
            if i >= len(old_children):
                # New child added
                patches.append({
                    'type': 'CREATE',
                    'node': self.children[i],
                    'index': i
                })
            elif i >= len(self.children):
                # Child removed
                patches.append({
                    'type': 'REMOVE',
                    'index': i
                })
            else:
                # Compare existing children
                child_patches = self.children[i].diff(old_children[i])
                if child_patches:
                    patches.append({
                        'type': 'UPDATE',
                        'patches': child_patches,
                        'index': i
                    })
        
        return patches
