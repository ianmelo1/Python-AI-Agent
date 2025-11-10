import os
from typing import List
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


# ========== FERRAMENTAS DE DADOS ==========
@tool
def write_json(filepath: str, data: dict) -> str:
    """Write a Python dictionary as JSON to a file with pretty formatting."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        file_size = os.path.getsize(filepath)
        user_count = len(data.get('users', []))
        return f"✅ Saved to '{filepath}' ({file_size} bytes, {user_count} users)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def read_json(filepath: str) -> str:
    """Read and return the contents of a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        user_count = len(data.get('users', []))
        return f"File contains {user_count} users:\n{json.dumps(data, indent=2)}"
    except FileNotFoundError:
        return f"❌ File '{filepath}' not found."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def generate_sample_users(
        first_names: List[str],
        last_names: List[str],
        domains: List[str],
        min_age: int,
        max_age: int
) -> dict:
    """Generate sample user data. Count is determined by the length of first_names."""
    if not first_names or not last_names or not domains:
        return {"error": "Lists cannot be empty"}
    if min_age > max_age or min_age < 0:
        return {"error": "Invalid age range"}

    users = []
    count = len(first_names)

    for i in range(count):
        first = first_names[i]
        last = last_names[i % len(last_names)]
        domain = domains[i % len(domains)]
        email = f"{first.lower()}.{last.lower()}@{domain}"

        user = {
            "id": i + 1,
            "firstName": first,
            "lastName": last,
            "email": email,
            "username": f"{first.lower()}{random.randint(100, 999)}",
            "age": random.randint(min_age, max_age),
            "registeredAt": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        users.append(user)

    return {"users": users, "count": len(users)}


@tool
def generate_random_data(data_type: str, count: int = 5) -> dict:
    """Generate random data: 'emails', 'names', 'companies', 'phones'."""
    try:
        count = max(1, min(count, 20))

        if data_type == "emails":
            domains = ["gmail.com", "outlook.com", "yahoo.com", "company.com"]
            items = [f"user{random.randint(1000, 9999)}@{random.choice(domains)}" for _ in range(count)]
        elif data_type == "names":
            first = ["Ana", "João", "Maria", "Pedro", "Lucas", "Julia", "Carlos", "Beatriz"]
            last = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa"]
            items = [f"{random.choice(first)} {random.choice(last)}" for _ in range(count)]
        elif data_type == "companies":
            pre = ["Tech", "Global", "Smart", "Digital", "Cyber", "Cloud"]
            suf = ["Solutions", "Systems", "Labs", "Corp", "Industries"]
            items = [f"{random.choice(pre)} {random.choice(suf)}" for _ in range(count)]
        elif data_type == "phones":
            items = [f"+55 11 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}" for _ in range(count)]
        else:
            return {"error": f"Unknown type: '{data_type}'. Use: emails, names, companies, phones"}

        return {"data_type": data_type, "items": items, "count": count}
    except Exception as e:
        return {"error": str(e)}


# ========== FERRAMENTAS DE ARQUIVOS ==========
@tool
def list_json_files(directory: str = ".") -> str:
    """List all JSON files in a directory."""
    try:
        path = Path(directory)
        json_files = list(path.glob("*.json"))

        if not json_files:
            return f"No JSON files in '{directory}'"

        result = f"📁 Found {len(json_files)} JSON file(s):\n\n"
        for file in sorted(json_files):
            size = file.stat().st_size
            modified = datetime.fromtimestamp(file.stat().st_mtime)
            result += f"  • {file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M')})\n"
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def verify_file_exists(filepath: str) -> str:
    """Check if a file exists and return its details."""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"❌ File '{filepath}' does NOT exist"

        size = path.stat().st_size
        modified = datetime.fromtimestamp(path.stat().st_mtime)

        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                user_count = len(data.get('users', []))
                return f"✅ EXISTS: '{filepath}'\n  Size: {size} bytes\n  Modified: {modified.strftime('%Y-%m-%d %H:%M')}\n  Users: {user_count}"

        return f"✅ EXISTS: '{filepath}'\n  Size: {size} bytes"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def delete_file(filepath: str) -> str:
    """Delete a file (use with caution!)."""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"❌ File '{filepath}' does not exist"
        path.unlink()
        return f"🗑️ Deleted '{filepath}'"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ========== FERRAMENTAS PARA DEVS ==========
@tool
def create_gitignore(template: str = "python", filepath: str = ".gitignore") -> str:
    """Create .gitignore. Templates: python, node, react, general."""
    templates = {
        "python": """# Python
__pycache__/
*.py[cod]
*.so
.venv/
venv/
.env
.env.local
.idea/
.vscode/
.DS_Store
""",
        "node": """# Node
node_modules/
.env
.env.local
dist/
build/
.DS_Store
""",
        "react": """# React
node_modules/
build/
.env.local
.DS_Store
""",
        "general": """# General
.env
.idea/
.vscode/
.DS_Store
*.log
"""
    }

    try:
        content = templates.get(template.lower(), templates["general"])
        with open(filepath, 'w') as f:
            f.write(content)
        return f"✅ Created {filepath} ({template} template)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def create_readme(project_name: str = "My Project", description: str = "A cool project") -> str:
    """Create a README.md file."""
    content = f"""# {project_name}

{description}

## 🚀 Getting Started

### Installation

```bash
pip install -r requirements.txt
```

## 📖 Usage

```python
# Add usage examples
```

## 🛠️ Technologies

- Python
- [Add more]

## 📝 License

MIT
"""

    try:
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Created README.md"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def create_requirements_txt(packages: List[str]) -> str:
    """Create requirements.txt with packages."""
    try:
        content = "\n".join(packages) + "\n"
        with open("requirements.txt", 'w') as f:
            f.write(content)
        return f"✅ Created requirements.txt ({len(packages)} packages)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def read_python_file(filepath: str) -> str:
    """Read Python file with line numbers."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        numbered = "\n".join(f"{i+1:4d} | {line.rstrip()}" for i, line in enumerate(lines))
        return f"📄 {filepath} ({len(lines)} lines):\n\n{numbered}"
    except FileNotFoundError:
        return f"❌ Not found: {filepath}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def find_todos_in_code(directory: str = ".") -> str:
    """Find TODO, FIXME, HACK in Python files."""
    try:
        todos = []
        path = Path(directory)

        for py_file in path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if any(tag in line for tag in ['TODO', 'FIXME', 'HACK', 'XXX']):
                            todos.append(f"{py_file}:{i} - {line.strip()}")
            except:
                continue

        if not todos:
            return f"✅ No TODOs found"

        result = f"📝 Found {len(todos)} TODO(s):\n\n"
        result += "\n".join(f"  • {t}" for t in todos[:20])
        if len(todos) > 20:
            result += f"\n... +{len(todos) - 20} more"
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def count_lines_of_code(directory: str = ".") -> str:
    """Count lines of code in Python files."""
    try:
        path = Path(directory)
        file_count = 0
        line_count = 0

        for file in path.rglob("*.py"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    file_count += 1
                    line_count += len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            except:
                continue

        return f"📊 Code Stats:\n  • {line_count} lines in {file_count} Python file(s)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def search_in_files(search_term: str, directory: str = ".", extensions: List[str] = [".py"]) -> str:
    """Search for term in files."""
    try:
        path = Path(directory)
        results = []

        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if search_term.lower() in line.lower():
                                results.append(f"{file}:{i} - {line.strip()}")
                except:
                    continue

        if not results:
            return f"❌ No matches for '{search_term}'"

        result = f"🔍 Found {len(results)} match(es):\n\n"
        result += "\n".join(f"  • {r}" for r in results[:15])
        if len(results) > 15:
            result += f"\n... +{len(results) - 15} more"
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ========== CONFIGURAÇÃO ==========
TOOLS = [
    # Dados
    write_json, read_json, generate_sample_users, generate_random_data,
    # Arquivos
    list_json_files, verify_file_exists, delete_file,
    # Dev
    create_gitignore, create_readme, create_requirements_txt,
    read_python_file, find_todos_in_code, count_lines_of_code, search_in_files
]

llm = ChatGoogleGenerativeAI(
    model="models/gemini-pro-latest",
    temperature=0,
    google_api_key=API_KEY
)

SYSTEM_MESSAGE = """You are CodeHelper, an AI assistant for developers.

FORMATTING RULES:
- Use markdown headers (##) for sections
- Keep responses SHORT and organized
- Use bullet points
- Be direct

Execute tasks without asking permission."""

agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_MESSAGE)


def run_agent(user_input: str, history: List[BaseMessage]) -> AIMessage:
    """Run agent with error handling."""
    try:
        result = agent.invoke(
            {"messages": history + [HumanMessage(content=user_input)]},
            config={"recursion_limit": 50}
        )
        return result["messages"][-1]
    except Exception as e:
        return AIMessage(content=f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 CodeHelper Agent - ASSISTENTE DE PROGRAMAÇÃO")
    print("=" * 70)
    print("\n📚 FERRAMENTAS DISPONÍVEIS:\n")
    print("  🔧 PROJETO: gitignore, readme, requirements")
    print("  📝 CÓDIGO: ler arquivos, encontrar TODOs, contar linhas")
    print("  📊 DADOS: gerar usuários, emails, nomes aleatórios")
    print("\n💡 EXEMPLOS:\n")
    print("  • 'create python gitignore'")
    print("  • 'create readme for MyAPI'")
    print("  • 'find all todos'")
    print("  • 'count lines of code'")
    print("  • 'create 5 users and save to users.json'")
    print("\n⌨️  Digite 'quit' para sair")
    print("=" * 70 + "\n")

    history: List[BaseMessage] = []

    while True:
        user_input = input("💬 You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q', '']:
            print("\n👋 Valeu! 🚀\n")
            break

        print("🤖 Agent: ", end="", flush=True)
        response = run_agent(user_input, history)
        print(response.content)
        print()

        history += [HumanMessage(content=user_input), response]