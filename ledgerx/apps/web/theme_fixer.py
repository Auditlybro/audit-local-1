import os

def replace_in_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want backgrounds that were blindly mapped to bg-slate-900 to be bg-slate-50 instead
    # when paired with dark:bg-navy.
    if 'bg-slate-900 dark:bg-navy' in content:
        content = content.replace('bg-slate-900 dark:bg-navy', 'bg-slate-50 dark:bg-navy')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")

for root, _, files in os.walk('c:/Users/valla/Desktop/audit-local-1/ledgerx/apps/web/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            replace_in_file(os.path.join(root, file))
