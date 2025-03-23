from typing import Any, Dict, List, Union
from .dom import VirtualNode

class TemplateParser:
    @staticmethod
    def parse(template: str) -> VirtualNode:
        tokens = TemplateParser._tokenize(template)
        return TemplateParser._build_tree(tokens)
    
    @staticmethod
    def h(tag: str, props: Dict[str, Any] = None, *children: List[Any]) -> VirtualNode:
        """Helper function for creating elements (similar to React.createElement)"""
        return VirtualNode(
            tag=tag,
            props=props or {},
            children=[
                child if isinstance(child, VirtualNode)
                else VirtualNode('text', {'textContent': str(child)})
                for child in children if child is not None
            ]
        )
        
    @staticmethod
    def _tokenize(template: str) -> List[Dict[str, Any]]:
        tokens = []
        current = 0
        while current < len(template):
            if template[current] == '<':
                # Parse tag
                tag_end = template.find('>', current)
                tag_content = template[current+1:tag_end]
                if tag_content.startswith('/'):
                    tokens.append({'type': 'close', 'tag': tag_content[1:]})
                else:
                    attrs = {}
                    parts = tag_content.split()
                    tag = parts[0]
                    for attr in parts[1:]:
                        name, value = attr.split('=')
                        attrs[name] = value.strip('"\'')
                    tokens.append({'type': 'open', 'tag': tag, 'attrs': attrs})
                current = tag_end + 1
            elif template[current] == '{':
                # Parse expression
                expr_end = template.find('}', current)
                expr = template[current+1:expr_end].strip()
                tokens.append({'type': 'expr', 'content': expr})
                current = expr_end + 1
            else:
                # Parse text
                next_special = min(
                    (pos for pos in (
                        template.find('<', current),
                        template.find('{', current)
                    ) if pos != -1),
                    default=len(template)
                )
                text = template[current:next_special].strip()
                if text:
                    tokens.append({'type': 'text', 'content': text})
                current = next_special
        return tokens

    @staticmethod
    def _build_tree(tokens: List[Dict[str, Any]]) -> VirtualNode:
        stack = [VirtualNode('root', {})]
        for token in tokens:
            if token['type'] == 'open':
                node = VirtualNode(token['tag'], token.get('attrs', {}))
                stack[-1].children.append(node)
                stack.append(node)
            elif token['type'] == 'close':
                stack.pop()
            elif token['type'] in ('text', 'expr'):
                stack[-1].children.append(
                    VirtualNode('text', {'textContent': token['content']})
                )
        return stack[0].children[0]

    @staticmethod
    def parse_pyx(pyx_content: str) -> VirtualNode:
        """Parse PYX format (Python XML-like syntax)"""
        lines = [line.strip() for line in pyx_content.splitlines() if line.strip()]
        indentation = {0: []}
        current_indent = 0
        
        for line in lines:
            indent = len(line) - len(line.lstrip())
            content = line.lstrip()
            
            if content.startswith('<'):
                # Parse tag definition
                if ' ' in content:
                    tag, props = content[1:].split(' ', 1)
                    props = TemplateParser._parse_props(props)
                else:
                    tag = content[1:]
                    props = {}
                    
                node = VirtualNode(tag.rstrip('>'), props)
                indentation[indent] = node
                
                if indent < current_indent:
                    # Closing previous level
                    parent = indentation.get(indent - 2, indentation[0])
                    parent.children.append(node)
                else:
                    # New child at current level
                    parent = indentation.get(indent - 2, None)
                    if parent:
                        parent.children.append(node)
                        
                current_indent = indent
            else:
                # Text content or expression
                current_node = indentation[current_indent]
                if content.startswith('{'):
                    # Expression
                    expr = content[1:-1].strip()
                    current_node.children.append(
                        VirtualNode('expression', {'value': expr})
                    )
                else:
                    # Text
                    current_node.children.append(
                        VirtualNode('text', {'textContent': content})
                    )
        
        return indentation[0]

    @staticmethod
    def _parse_props(props_str: str) -> Dict[str, Any]:
        props = {}
        for prop in props_str.split():
            if '=' in prop:
                key, value = prop.split('=', 1)
                if key == 'through':
                    # Handle nested routes and parameters
                    route_info = value.strip('"\'').split(':')
                    module_path = route_info[0]
                    params = {}
                    if len(route_info) > 1:
                        params = {p.split('=')[0]: p.split('=')[1] 
                                for p in route_info[1].split(',')}
                    
                    module_name = module_path.replace('.py', '')
                    props['onClick'] = f"self.navigate_to('{module_name}', {params})"
                    props['className'] = f"{props.get('class', '')} route-link"
                    props['data-route'] = module_name
                    props['style'] = 'cursor: pointer;'
                    # Add metadata support
                    if len(route_info) > 2:
                        metadata = json.loads(route_info[2])
                        props['data-metadata'] = metadata
                        router = get_router()
                        router.set_metadata(module_name, metadata)
                elif key == 'to':  # Simplified routing (like: to="home")
                    module_name = value.strip('"\'')
                    props['onClick'] = f"self.navigate_to('{module_name}')"
                    props['className'] = 'route-link'
                elif key == 'model':  # Two-way binding (like: model="name")
                    var_name = value.strip('"\'')
                    props['value'] = f"self.state.{var_name}"
                    props['onChange'] = f"self.set_state('{var_name}', $value)"
                elif key == 'on':  # Event shorthand (like: on="click:handle_click")
                    event, handler = value.strip('"\'').split(':')
                    props[f'on{event.capitalize()}'] = f"self.{handler}"
                elif key == 'if':  # Conditional rendering (like: if="is_logged_in")
                    props['_condition'] = value.strip('"\'')
                elif key == 'for':  # Loop shorthand (like: for="item in items")
                    var, items = value.strip('"\'').split(' in ')
                    props['_iterator'] = {'var': var, 'items': items}
                elif value.startswith('{'):
                    props[key] = value[1:-1].strip()
                else:
                    props[key] = value.strip('"\'')
        return props

    @staticmethod
    def parse_pya(content: str) -> Dict[str, Any]:
        sections = {
            'imports': [],
            'state': {},
            'computed': {},
            'handlers': {},
            'effects': [],
            'template': []
        }
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Smart imports
            if line.startswith('use '):
                # use Button, Card from components
                parts = line[4:].split(' from ')
                components = [c.strip() for c in parts[0].split(',')]
                module = parts[1].strip()
                for comp in components:
                    sections['imports'].append(f"from {module} import {comp}")
                
            # Enhanced state declaration
            elif line.startswith('let '):
                # let count = 0, name = "", items = []
                vars = line[4:].split(',')
                for var in vars:
                    name, value = var.split('=', 1)
                    sections['state'][name.strip()] = eval(value.strip())
                    
            # Reactive computed properties
            elif line.startswith('@watch'):
                # @watch(count, name)
                deps = line[7:-1].split(',')
                sections['computed'][next_line] = deps
                
            # Side effects
            elif line.startswith('@effect'):
                # @effect(mount) or @effect(count)
                trigger = line[8:-1] if '(' in line else 'mount'
                sections['effects'].append({
                    'trigger': trigger,
                    'code': next_line
                })
                
            # Event handlers with auto-binding
            elif line.startswith('on '):
                # on click(event) -> handle_click
                event, handler = line[3:].split('->')
                sections['handlers'][event.strip()] = handler.strip()
                
            # Store integration
            elif line.startswith('store '):
                # store auth = useAuthStore()
                name = line[6:].split('=')[0].strip()
                sections['state'][name] = f"use_store('{name}')"
                
            else:
                sections['template'].append(line)
                
        return sections

    @staticmethod
    def _parse_props(props_str: str) -> Dict[str, Any]:
        props = {}
        in_string = False
        buffer = []
        
        for char in props_str:
            if char in ('"', "'") and not in_string:
                in_string = True
            elif char in ('"', "'") and in_string:
                in_string = False
                
            if char.isspace() and not in_string:
                if buffer:
                    prop = ''.join(buffer)
                    if '=' in prop:
                        key, value = prop.split('=', 1)
                        props[key.strip()] = TemplateParser._parse_value(value.strip())
                    buffer = []
            else:
                buffer.append(char)
        
        return props

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse property values with smart type detection"""
        value = value.strip('\'"')
        
        # Boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
            
        # Numbers
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
            
        # Python expressions
        if value.startswith('{') and value.endswith('}'):
            return value[1:-1].strip()
            
        # Default to string
        return value

        if key == 'bind':  # Two-way binding shorthand
            # bind:value="name"
            prop, var = value.split('=')
            props[prop] = f"self.state.{var}"
            props[f"on{prop.capitalize()}Change"] = f"self.set_state('{var}', $value)"
        elif key.startswith('@'):  # Event binding shorthand
            # @click="increment"
            event = key[1:]
            props[f"on{event.capitalize()}"] = f"self.{value}"
        elif key.startswith(':'):  # Dynamic props
            # :class="{'active': isActive}"
            prop = key[1:]
            props[prop] = value
        # ...existing code...
