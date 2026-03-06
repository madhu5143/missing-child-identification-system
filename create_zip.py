import os
import zipfile

src = r'C:\Users\MadhuSudhan\.gemini\antigravity\scratch\missing_child_id_system'
dest = r'C:\Users\MadhuSudhan\.gemini\antigravity\scratch\latest_updated_code.zip'
exclude_dirs = {'.venv', 'node_modules', '__pycache__', '.git', '.next'}

with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(src):
        # Prevent traversal of excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, src)
            zipf.write(file_path, arcname)

print("Created latest_updated_code.zip successfully at", dest)
