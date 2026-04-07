import os, re

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    
    # Backgrounds
    content = re.sub(r'(?<!dark:)\bbg-navy-400(/80)?\b', r'bg-white dark:bg-navy-400\1', content)
    content = re.sub(r'(?<!dark:)\bbg-navy-300\b', 'bg-slate-50 dark:bg-navy-300', content)
    content = re.sub(r'(?<!dark:)\bbg-navy-100(/30)?\b', r'bg-slate-100 dark:bg-navy-100\1', content)
    content = re.sub(r'(?<!dark:)\bbg-navy\b', 'bg-slate-900 dark:bg-navy', content)

    # Borders
    content = re.sub(r'(?<!dark:)\bborder-navy-100(/(\d+))?\b', r'border-slate-200 dark:border-navy-100\1', content)
    content = re.sub(r'(?<!dark:)\bborder-navy-300\b', 'border-slate-300 dark:border-navy-300', content)

    # Texts
    # Careful not to change text-white inside buttons we just designed (MS, Apple have arbitrary bg-white text-something). But MS/Apple don't use text-white, they use text-[#3c4043]. Apple uses text-[#3c4043].
    # But wait! If text-white is used inside gold buttons, it might become text-slate-900, which might be fine on gold.
    content = re.sub(r'(?<!dark:)\btext-white\b', 'text-slate-900 dark:text-white', content)
    content = re.sub(r'(?<!dark:)\btext-slate-300\b', 'text-slate-600 dark:text-slate-300', content)
    content = re.sub(r'(?<!dark:)\btext-slate-400\b', 'text-slate-500 dark:text-slate-400', content)

    if original != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")

for root, _, files in os.walk('c:/Users/valla/Desktop/audit-local-1/ledgerx/apps/web/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            process_file(os.path.join(root, file))
