"""
fix_imports.py — Jugs's Auto-Fix
Renames types.py -> models.py and updates all imports.
Run this in your repo folder. One shot, done.
"""
import os
import re


def fix_repo():
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Rename types.py to models.py
    old_file = os.path.join(repo_path, "types.py")
    new_file = os.path.join(repo_path, "models.py")
    
    if os.path.exists(old_file):
        os.rename(old_file, new_file)
        print(f"[OK] Renamed: types.py -> models.py")
    else:
        print("[WARN] types.py not found, maybe already renamed?")
    
    # Step 2: Update all imports in every .py file
    py_files = [f for f in os.listdir(repo_path) if f.endswith(".py")]
    
    for filename in py_files:
        filepath = os.path.join(repo_path, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace "from types import" -> "from models import"
        # But NOT "from types import MappingProxyType" etc (Python built-ins)
        # Only replace lines that reference YOUR dataclasses
        
        new_content = re.sub(
            r'^from types import (Target|DetectionResult)',
            r'from models import \1',
            content,
            flags=re.MULTILINE
        )
        
        # Also catch "import types" if it was used for your module
        new_content = re.sub(
            r'^import types\s*$',
            'import models',
            new_content,
            flags=re.MULTILINE
        )
        
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[OK] Fixed imports in: {filename}")
    
    print("\n[DONE] All fixed. Run: python ui.py")


if __name__ == "__main__":
    fix_repo()

