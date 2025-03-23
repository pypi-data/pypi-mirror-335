import click
import os
import shutil
from pathlib import Path

@click.group()
def cli():
    """My Python Framework CLI"""
    pass

@cli.command()
@click.argument('name')
def create(name):
    """Create a new project"""
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)
    
    # Create basic structure
    (project_dir / 'components').mkdir()
    (project_dir / 'pages').mkdir()
    (project_dir / 'static').mkdir()
    
    # Create main.py
    with open(project_dir / 'main.py', 'w') as f:
        f.write('from my_python_framework import Component\n\n# Your app code here\n')

@cli.command()
@click.argument('name')
def generate(name):
    """Generate a new component"""
    component_path = Path('components') / f"{name}.pya"
    
    with open(component_path, 'w') as f:
        f.write('''<div class="component">
    <h2>{self.props.get("title", "Default Title")}</h2>
    {self.render_content()}
</div>''')

@cli.command()
def start():
    """Start development server"""
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            return app.send_static_file('index.html')
            
        app.run(debug=True)
    except ImportError:
        print("Flask not found. Install with: pip install flask")

@cli.command()
def build():
    """Build project for production"""
    build_dir = Path('build')
    build_dir.mkdir(exist_ok=True)
    
    # Copy static files
    static_dir = Path('static')
    if static_dir.exists():
        shutil.copytree(static_dir, build_dir / 'static', dirs_exist_ok=True)

if __name__ == '__main__':
    cli()
