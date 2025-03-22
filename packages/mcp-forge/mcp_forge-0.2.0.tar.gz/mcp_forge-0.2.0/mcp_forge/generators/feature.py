"""Feature generator for adding new features to existing MCP servers."""

import re
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def split_words(name: str) -> list[str]:
    """Split a string into words based on case changes or delimiters."""
    # First, handle explicit delimiters
    result = []
    for part in re.split(r"[-_\s]", name):
        if not part:
            continue

        # Then handle camelCase and PascalCase
        if re.search(r"[A-Z]", part):
            # Split by capital letters, but keep the capital letter with its word
            words = re.findall(r"[A-Z]?[a-z0-9]+", part)
            result.extend([w for w in words if w])
        else:
            result.append(part)

    return result


def to_camel_case(name: str) -> str:
    """Convert a string to camelCase."""
    # Remove "Tool" suffix if it exists
    name = remove_tool_suffix(name)
    words = split_words(name)
    if not words:
        return ""

    # First word lowercase, rest capitalized
    return words[0].lower() + "".join(word[0].upper() + word[1:].lower() for word in words[1:])


def to_pascal_case(name: str) -> str:
    """Convert a string to PascalCase."""
    # Remove "Tool" suffix if it exists
    name = remove_tool_suffix(name)
    words = split_words(name)
    if not words:
        return ""

    # All words capitalized
    return "".join(word[0].upper() + word[1:].lower() for word in words)


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case."""
    # Remove "Tool" suffix if it exists
    name = remove_tool_suffix(name)
    words = split_words(name)
    if not words:
        return ""

    # All words lowercase with underscores
    return "_".join(word.lower() for word in words)


def to_display_name(name: str) -> str:
    """Convert a string to a readable display name with spaces."""
    # Remove "Tool" suffix if it exists
    name = remove_tool_suffix(name)
    words = split_words(name)
    if not words:
        return ""

    # Capitalize first letter of each word and join with spaces
    return " ".join(word[0].upper() + word[1:].lower() for word in words)


def remove_tool_suffix(name: str) -> str:
    """Remove 'Tool' suffix if it exists (case insensitive)."""
    if name.lower().endswith("tool"):
        return name[:-4]
    return name


@dataclass
class FeatureConfig:
    """Configuration for a new MCP server feature."""

    name: str
    display_name: str
    description: str
    tool_name: str
    class_name: str
    file_name: str

    @classmethod
    def from_inputs(cls, name: str) -> "FeatureConfig":
        """Create config from user inputs."""
        # Clean and convert name to proper case
        clean_name = remove_tool_suffix(name)
        pascal_name = to_pascal_case(clean_name)
        display_name = to_display_name(clean_name)

        # Tool API name in PascalCase to match class name convention
        tool_name = pascal_name

        # Class name with Tool suffix in PascalCase
        class_name = f"{pascal_name}Tool"

        # File name in snake_case
        file_name = to_snake_case(clean_name)

        # Get a basic description (optional)
        description = Prompt.ask("[bold]Enter tool description[/bold]", default=f"Tool for {display_name}")

        return cls(
            name=pascal_name,
            display_name=display_name,
            description=description,
            tool_name=tool_name,
            class_name=class_name,
            file_name=file_name,
        )


def find_mcp_root() -> Path | None:
    """Find the root directory of an MCP server project."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            # Get package name from directory structure
            package_name = None
            for d in current.iterdir():
                if (
                    d.is_dir()
                    and not d.name.startswith(".")
                    and d.name != "__pycache__"
                    and (d / "server_stdio.py").exists()
                    and (d / "tools").exists()
                    and (d / "services").exists()
                ):
                    package_name = d.name
                    break

            if package_name:
                return current
        current = current.parent
    return None


def get_package_name(project_root: Path) -> str:
    """Get the package name from the project root directory."""
    for d in project_root.iterdir():
        if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__" and (d / "server_stdio.py").exists():
            return d.name
    raise ValueError("Could not determine package name")


def create_tool_file(env: Environment, config: FeatureConfig, project_root: Path, package_name: str) -> Path:
    """Create the new tool file."""
    tool_dir = project_root / package_name / "tools"
    tool_file = tool_dir / f"{config.file_name}.py"

    if tool_file.exists():
        raise ValueError(f"Tool {config.name} already exists")

    # Use the template to generate the tool file
    template = env.get_template("tool.py.j2")
    template_context = {
        "config": config,
    }
    tool_content = template.render(**template_context)

    with open(tool_file, "w", encoding="utf-8") as f:
        f.write(tool_content)

    return tool_file


def update_init_file(env: Environment, config: FeatureConfig, project_root: Path, package_name: str) -> None:
    """Update the tools/__init__.py file to include the new tool."""
    tool_dir = project_root / package_name / "tools"
    init_file = tool_dir / "__init__.py"

    if init_file.exists():
        with open(init_file, encoding="utf-8") as f:
            current_content = f.read()
    else:
        current_content = '"""Tool exports."""\n'

    # Parse existing imports and __all__ list
    import_lines = []
    all_line = ""

    for line in current_content.splitlines():
        if line.startswith("from ."):
            import_lines.append(line)
        elif line.startswith("__all__"):
            all_line = line

    # Add the new import if not already present
    new_import = f"from .{config.file_name} import {config.class_name}"
    if new_import not in import_lines:
        import_lines.append(new_import)

    # Sort imports alphabetically
    import_lines.sort()

    # Update or create the __all__ list
    if all_line:
        # Extract current list
        all_items = eval(all_line.split("=")[1].strip())
        # Add new tool if not already in list
        if config.class_name not in all_items:
            all_items.append(config.class_name)
        # Sort alphabetically
        all_items.sort()
        # Format as string
        all_line = f"__all__ = {all_items}"
    else:
        # Create new __all__ list
        all_line = f'__all__ = ["{config.class_name}"]'

    # Use template for updating init.py
    init_template = env.get_template("init_update.py.j2")
    init_context = {"import_lines": import_lines, "all_line": all_line}
    init_content = init_template.render(**init_context)

    with open(init_file, "w", encoding="utf-8") as f:
        f.write(init_content)


def extract_imports_and_tools(file_content: str, package_name: str) -> tuple[list[str], list[str], list[str]]:
    """Extract imports and tool references from a file."""
    import_lines = []
    tool_imports = []
    existing_tools = []

    # Extract imports
    for line in file_content.splitlines():
        if line.startswith("import ") or line.startswith("from "):
            import_lines.append(line)
            if line.startswith(f"from {package_name}.tools import") or line.startswith("from .tools import"):
                # Extract tool imports
                tools_part = line.split("import ")[1]
                for tool in tools_part.split(","):
                    clean_tool = tool.strip()
                    if clean_tool:
                        tool_imports.append(clean_tool)

    # Extract existing tools
    tools_pattern = r"def get_available_tools\(\).*?return \[(.*?)\]"
    tools_match = re.search(tools_pattern, file_content, re.DOTALL)
    if tools_match:
        tools_list = tools_match.group(1)
        for line in tools_list.splitlines():
            if "(" in line and ")" in line:
                tool_name = line.split("(")[0].strip()
                if tool_name and tool_name not in ["#"]:
                    existing_tools.append(tool_name)

    return import_lines, tool_imports, existing_tools


def update_imports(import_lines: list[str], tool_imports: list[str], config: FeatureConfig, package_name: str) -> list[str]:
    """Update import lines to include the new tool class."""
    if config.class_name not in tool_imports:
        # Add the new import
        has_tools_import = False
        for i, line in enumerate(import_lines):
            if line.startswith(f"from {package_name}.tools import") or line.startswith("from .tools import"):
                has_tools_import = True
                parts = line.split("import ")
                imports = [imp.strip() for imp in parts[1].split(",")]
                if config.class_name not in imports:
                    imports.append(config.class_name)
                imports.sort()
                import_lines[i] = f"{parts[0]}import {', '.join(imports)}"
                break

        if not has_tools_import:
            import_lines.append(f"from {package_name}.tools import {config.class_name}")
            import_lines.sort()

    return import_lines


def update_server_stdio(env: Environment, config: FeatureConfig, project_root: Path, package_name: str) -> None:
    """Update server_stdio.py to register the new tool."""
    server_file = project_root / package_name / "server_stdio.py"
    if not server_file.exists():
        raise ValueError("server_stdio.py not found")

    with open(server_file, encoding="utf-8") as f:
        server_content = f.read()

    # Parse existing imports and tools
    import_lines, tool_imports, existing_tools = extract_imports_and_tools(server_content, package_name)

    # Update imports
    import_lines = update_imports(import_lines, tool_imports, config, package_name)

    # Update tools list
    if config.class_name not in existing_tools:
        existing_tools.append(config.class_name)
    existing_tools.sort()

    # Use template for server_stdio.py update
    stdio_template = env.get_template("server_stdio_update.py.j2")
    stdio_context = {"config": {"project_name": package_name}, "import_lines": import_lines, "tools": existing_tools}
    server_content = stdio_template.render(**stdio_context)

    with open(server_file, "w", encoding="utf-8") as f:
        f.write(server_content)


def update_server_sse(env: Environment, config: FeatureConfig, project_root: Path, package_name: str) -> None:
    """Update server_sse.py if it exists."""
    server_sse_file = project_root / package_name / "server_sse.py"
    if not server_sse_file.exists():
        return  # Skip if file doesn't exist

    with open(server_sse_file, encoding="utf-8") as f:
        sse_content = f.read()

    # Parse existing imports and tools
    sse_import_lines, sse_tool_imports, sse_existing_tools = extract_imports_and_tools(sse_content, package_name)

    # Update imports
    sse_import_lines = update_imports(sse_import_lines, sse_tool_imports, config, package_name)

    # Update tools list
    if config.class_name not in sse_existing_tools:
        sse_existing_tools.append(config.class_name)
    sse_existing_tools.sort()

    # Get import section and tools section content directly
    new_imports = "\n".join(sse_import_lines)
    new_tools_list = "\n".join([f"        {tool}()," for tool in sse_existing_tools])

    # Replace just the import section and get_available_tools section
    # Keep the rest of the file intact
    import_section_pattern = r"(.*?)(import .*?)(?=\n\n)"
    import_match = re.search(import_section_pattern, sse_content, re.DOTALL)

    tools_section_pattern = r"def get_available_tools\(\).*?return \[(.*?)\]"
    tools_match = re.search(tools_section_pattern, sse_content, re.DOTALL)

    # Get function definition and return part
    func_def = 'def get_available_tools() -> list[Tool]:\n    """Get list of all available tools."""\n    return ['
    func_end = "    ]"

    if import_match and tools_match:
        # Replace imports
        sse_content = re.sub(import_section_pattern, f"\\1{new_imports}", sse_content, flags=re.DOTALL)

        # Replace tools list
        sse_content = re.sub(tools_section_pattern, f"{func_def}\n{new_tools_list}\n{func_end}", sse_content, flags=re.DOTALL)

        with open(server_sse_file, "w", encoding="utf-8") as f:
            f.write(sse_content)


def update_test_client(env: Environment, config: FeatureConfig, project_root: Path) -> None:
    """Update test_client.py to include the new tool if the file exists."""
    test_client_file = project_root / "test_client.py"
    if not test_client_file.exists():
        return  # Skip if file doesn't exist

    with open(test_client_file, encoding="utf-8") as f:
        test_client_content = f.read()

    # Find the test cases section
    test_cases_start = test_client_content.find("test_cases = [")
    if test_cases_start == -1:
        return  # Skip if test cases section not found

    # Extract existing test cases
    test_cases_pattern = r"test_cases = \[(.*?)\]"
    test_cases_match = re.search(test_cases_pattern, test_client_content, re.DOTALL)

    if not test_cases_match:
        return  # Skip if test cases pattern not found

    test_cases_content = test_cases_match.group(1)
    test_cases = []

    # Parse existing test cases
    for raw_line in test_cases_content.splitlines():
        clean_line = raw_line.strip()
        if clean_line and not clean_line.startswith("#") and "(" in clean_line:
            test_cases.append(clean_line.rstrip(","))

    # Add new test case if not already present
    new_test_case = f'    ("{config.tool_name}", {{\n        "query_text": "test input"\n    }})'
    if not any(config.tool_name in tc for tc in test_cases):
        test_cases.append(new_test_case)

    # Use template for test client update
    test_template = env.get_template("test_client_update.py.j2")
    test_context = {"test_cases": test_cases}
    test_case_section = test_template.render(**test_context)

    # Replace the test cases section
    updated_content = re.sub(test_cases_pattern, test_case_section, test_client_content, flags=re.DOTALL)

    with open(test_client_file, "w", encoding="utf-8") as f:
        f.write(updated_content)


def show_summary(config: FeatureConfig, tool_file: Path) -> None:
    """Display a summary of the created feature."""
    console.print("\n[bold green]✨ Tool created successfully![/bold green]")

    table = Table(title=f"Tool: {config.display_name}")
    table.add_column("Property", style="cyan")
    table.add_column("Details", style="green")

    table.add_row("Description", config.description)
    table.add_row("File Created", str(tool_file))
    table.add_row("Class Name", config.class_name)
    table.add_row("API Name", config.tool_name)
    table.add_row("Test Client", "Updated with example test case")

    console.print(table)


def add_feature(feature_name: str) -> None:
    """Add a new feature to an existing MCP server."""
    # Get the configuration for the new feature
    config = FeatureConfig.from_inputs(feature_name)

    # Find MCP server root
    project_root = find_mcp_root()
    if not project_root:
        raise ValueError("Not in an MCP server project directory")

    # Get template directory
    template_dir = Path(__file__).parent.parent / "templates" / "features"
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Get package name from directory structure
    package_name = get_package_name(project_root)

    # Create the tool file
    tool_file = create_tool_file(env, config, project_root, package_name)

    # Update tools/__init__.py
    update_init_file(env, config, project_root, package_name)

    # Update server_stdio.py
    update_server_stdio(env, config, project_root, package_name)

    # Update server_sse.py if it exists
    update_server_sse(env, config, project_root, package_name)

    # Update test_client.py if it exists
    update_test_client(env, config, project_root)

    # Show summary of what was created
    show_summary(config, tool_file)
