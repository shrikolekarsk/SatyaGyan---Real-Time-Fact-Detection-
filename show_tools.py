# src/fact_checker/show_tool.py
# ✅ Import FactChecker
from crew import FactChecker  # ✅ Direct local import since same folder

# ✅ Instantiate and show tool info
fc = FactChecker()

print("🔧 Tools used by the Crew:")
for tool in fc.tools:
    name = tool.__class__.__name__
    desc = getattr(tool, 'description', 'No description provided')
    print(f"✅ {name}: {desc}")
