#!/usr/bin/env python3
import argparse
import ast
import datetime
import difflib
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

#############################################
# UTILS
#############################################

DEFAULT_IGNORES = [
    '.git', '.DS_Store', 'node_modules', '__pycache__',
    'env', 'venv', 'dist', 'build', 'public'
]

def compute_file_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def detect_language_type(root_dir, forced_lang=None):
    if forced_lang:
        return [forced_lang]
    langs = []
    if os.path.exists(os.path.join(root_dir, 'package.json')):
        langs.append('react')
    if (
        os.path.exists(os.path.join(root_dir, 'pyproject.toml')) or
        os.path.exists(os.path.join(root_dir, 'requirements.txt')) or
        os.path.exists(os.path.join(root_dir, 'setup.py'))
    ):
        langs.append('python')
    return langs

def detect_code_fence_language(filename):
    lower = filename.lower()
    if lower.endswith(('.ts', '.tsx')):
        return 'typescript'
    if lower.endswith('.py'):
        return 'python'
    if lower.endswith('.sh'):
        return 'bash'
    if lower.endswith('.css'):
        return 'css'
    if lower.endswith('.js'):
        return 'javascript'
    if lower.endswith('.html'):
        return 'html'
    return ''

def should_ignore(path, langs, no_ignore=False, skip_patterns=None):
    if no_ignore:
        return False
    basename = os.path.basename(path)
    for ignore_item in DEFAULT_IGNORES:
        if ignore_item in path.split(os.sep):
            return True
    if 'react' in langs and basename == 'node_modules':
        return True
    if 'python' in langs and basename in ['__pycache__', 'env', 'venv']:
        return True
    if skip_patterns:
        for pat in skip_patterns:
            if '*' in pat:
                regex_str = pat.replace('.', r'\.').replace('*', '.*')
                if re.search(regex_str, path):
                    return True
            else:
                if pat in path or pat in basename:
                    return True
    return False

#############################################
# DEP EXTRACTION
#############################################

def add_ast_parents(node):
    for child in ast.iter_child_nodes(node):
        child.parent = node
        add_ast_parents(child)

def parse_python_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ast.parse(content)
    tree.parent = None
    add_ast_parents(tree)
    imports, functions, classes = [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            for n in node.names:
                full_name = module + '.' + n.name if module else n.name
                imports.append(full_name)
        elif isinstance(node, ast.FunctionDef):
            if isinstance(node.parent, ast.Module):
                functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            class_methods = []
            for b in node.body:
                if isinstance(b, ast.FunctionDef):
                    class_methods.append(b.name)
            classes.append({"name": node.name, "methods": class_methods})
    exports = functions + [c['name'] for c in classes]
    structure = {"language": "python", "functions": functions, "classes": classes}
    return imports, exports, structure

def extract_dependencies_ts(file_path):
    deps = {'imports': [], 'exports': [], 'structure': {}}
    imp_pat = r'import\s+(?:[\s\S]*?)from\s+[\'"](.+?)[\'"];'
    exp_pat = r'export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type|enum)?\s*([\w]+)'
    with open(file_path, 'r', encoding='utf-8') as f:
        c = f.read()
    imports = re.findall(imp_pat, c)
    exports = re.findall(exp_pat, c)
    deps['imports'].extend(imports)
    deps['exports'].extend(exports)
    deps['structure'] = {"language": "typescript", "functions": exports, "classes": []}
    return deps

def extract_dependencies_python(file_path):
    d = {'imports': [], 'exports': [], 'structure': {}}
    imports, exports, structure = parse_python_structure(file_path)
    d['imports'] = imports
    d['exports'] = exports
    d['structure'] = structure
    return d

def extract_dependencies(file_path, langs):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.ts', '.tsx']:
        return extract_dependencies_ts(file_path)
    elif ext == '.py':
        return extract_dependencies_python(file_path)
    else:
        return {'imports': [], 'exports': [], 'structure': {}}

#############################################
# DEP GRAPH
#############################################

def resolve_import_path(file, imp, root_dir):
    if imp.startswith('.'):
        base = os.path.dirname(file)
        candidate = os.path.normpath(os.path.join(base, imp))
        exts = ['.ts', '.tsx', '.py']
        if os.path.isdir(os.path.join(root_dir, candidate)):
            for pf in ['index.ts', 'index.tsx', '__init__.py']:
                pfp = os.path.join(candidate, pf)
                if os.path.exists(os.path.join(root_dir, pfp)):
                    return pfp
            return candidate
        else:
            if not any(candidate.endswith(e) for e in exts):
                for e in exts:
                    if os.path.exists(os.path.join(root_dir, candidate + e)):
                        return candidate + e
            return candidate
    else:
        bc = os.path.join(root_dir, imp.replace('.', os.sep))
        for e in ['.ts', '.tsx', '.py']:
            if os.path.exists(bc + e):
                return os.path.relpath(bc + e, root_dir)
        return imp

def build_dependency_graph(root_dir, langs, graph_type='full', no_ignore=False, skip_patterns=None):
    graph = {'nodes': [], 'edges': []}
    file_dependencies = {}
    exts = ['.ts', '.tsx', '.py']
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            d for d in dirnames
            if not should_ignore(os.path.join(dirpath, d), langs, no_ignore, skip_patterns)
        ]
        for filename in filenames:
            e = os.path.splitext(filename)[1].lower()
            if e in exts:
                fp = os.path.join(dirpath, filename)
                relp = os.path.relpath(fp, root_dir)
                if relp not in graph['nodes']:
                    graph['nodes'].append(relp)
                deps = extract_dependencies(fp, langs)
                file_dependencies[relp] = deps
    for file, deps in file_dependencies.items():
        if graph_type in ['full', 'imports_only']:
            for imp in deps['imports']:
                target = resolve_import_path(file, imp, root_dir)
                if target in graph['nodes']:
                    edge = {'from': file, 'to': target, 'type': 'import'}
                    if graph_type != 'no_objects':
                        edge['objects'] = deps['imports']
                    graph['edges'].append(edge)
        if graph_type in ['full', 'exports_only']:
            if deps['exports']:
                edge = {'from': file, 'to': None, 'type': 'export'}
                if graph_type != 'no_objects':
                    edge['objects'] = deps['exports']
                graph['edges'].append(edge)
    return graph, file_dependencies

#############################################
# TREE TEXT
#############################################

def generate_tree_text(root_dir, prefix='', langs=[], no_ignore=False, skip_patterns=None):
    tree = ''
    entries = sorted(os.listdir(root_dir))
    filtered = []
    for entry in entries:
        p = os.path.join(root_dir, entry)
        if os.path.isdir(p):
            if should_ignore(p, langs, no_ignore, skip_patterns):
                continue
        filtered.append(entry)
    for idx, entry in enumerate(filtered):
        p = os.path.join(root_dir, entry)
        connector = '├── ' if idx < len(filtered)-1 else '└── '
        tree += f"{prefix}{connector}{entry}\n"
        if os.path.isdir(p):
            extension = '│   ' if idx < len(filtered)-1 else '    '
            tree += generate_tree_text(p, prefix+extension, langs, no_ignore, skip_patterns)
    return tree

#############################################
# SINGLE-DOC
#############################################

def collect_all_files_in_tree_order(root_dir, langs, no_ignore=False, skip_patterns=None):
    result = []
    entries = sorted(os.listdir(root_dir))
    for e in entries:
        p = os.path.join(root_dir, e)
        if should_ignore(p, langs, no_ignore, skip_patterns):
            continue
        if os.path.isdir(p):
            sub = collect_all_files_in_tree_order(p, langs, no_ignore, skip_patterns)
            result.extend(sub)
        else:
            result.append(os.path.relpath(p, root_dir))
    return result

def guess_frontend_backend(langs, root_dir):
    guess = {'frontend': False, 'backend': False}
    if 'react' in langs:
        guess['frontend'] = True
    if 'python' in langs:
        guess['backend'] = True
    return guess

def generate_single_context_markdown(root_dir, langs, no_ignore=False, skip_patterns=None):
    fb = guess_frontend_backend(langs, root_dir)
    lines = []
    lines.append("# Repository Overview\n")
    if langs:
        lines.append(f"**Detected Languages**: {', '.join(langs)}\n")
    else:
        lines.append("**Detected Languages**: None\n")
    if fb['frontend']:
        lines.append("**Front-End**: Likely present\n")
    if fb['backend']:
        lines.append("**Back-End**: Likely present\n")

    lines.append("\n## Folder Tree\n```\n")
    bn = os.path.basename(os.path.normpath(root_dir))
    t = generate_tree_text(root_dir, '', langs, no_ignore, skip_patterns)
    lines.append(bn + "\n")
    lines.append(t)
    lines.append("```\n")

    _, file_deps = build_dependency_graph(root_dir, langs, 'full', no_ignore, skip_patterns)
    lines.append("\n## Indexed Files\n")

    all_files = collect_all_files_in_tree_order(root_dir, langs, no_ignore, skip_patterns)
    for fpath in all_files:
        deps = file_deps.get(fpath, {})
        imports = deps.get('imports', [])
        lines.append(f"### {fpath}\n")
        if imports:
            lines.append("**Dependencies**:\n")
            for i in imports:
                lines.append(f" - {i}\n")
        else:
            lines.append("**Dependencies**: None\n")
        abspath = os.path.join(root_dir, fpath)
        try:
            with open(abspath, 'r', encoding='utf-8') as ff:
                c = ff.read()
            fence = detect_code_fence_language(fpath)
            lines.append("\n**Content**:\n")
            lines.append(f"```{fence}\n{c}\n```\n\n")
        except:
            lines.append("\nError reading file.\n\n")

    return "".join(lines)

#############################################
# ORIGINAL DOCS
#############################################

def generate_markdown(root_dir, langs, no_ignore=False):
    md = ''
    for dp, dns, fns in os.walk(root_dir):
        dns[:] = [d for d in dns if not should_ignore(os.path.join(dp, d), langs, no_ignore)]
        for fn in fns:
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, root_dir)
            try:
                with open(fp, 'r', encoding='utf-8') as file:
                    c = file.read()
                lang = detect_code_fence_language(fn)
                md += f"### {rel}\n\n```{lang}\n{c}\n```\n\n"
            except:
                md += f"### {rel}\n\nError reading file.\n\n"
    return md

def generate_light_markdown(root_dir, langs, no_ignore=False):
    md = ''
    code_exts = ('.ts', '.tsx', '.css', '.py', '.sh', '.js', '.html')
    for dp, dns, fns in os.walk(root_dir):
        dns[:] = [d for d in dns if not should_ignore(os.path.join(dp, d), langs, no_ignore)]
        for fn in fns:
            if fn.endswith(code_exts):
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, root_dir)
                try:
                    with open(fp, 'r', encoding='utf-8') as file:
                        c = file.read()
                    lang = detect_code_fence_language(fn)
                    md += f"### {rel}\n\n```{lang}\n{c}\n```\n\n"
                except:
                    md += f"### {rel}\n\nError reading file.\n\n"
    return md

#############################################
# STRUCTURE FILES
#############################################

def generate_structure_files(file_dependencies, output_path):
    detailed, top_level = {}, {}
    for f, deps in file_dependencies.items():
        detailed[f] = deps['structure']
        top_level[f] = {"imports": deps['imports'], "exports": deps['exports']}
    with open(os.path.join(output_path, 'detailed_structure.json'), 'w', encoding='utf-8') as d:
        json.dump(detailed, d, indent=4)
    with open(os.path.join(output_path, 'top_level_structure.json'), 'w', encoding='utf-8') as t:
        json.dump(top_level, t, indent=4)

#############################################
# CACHING & DIFF
#############################################

def load_cache(cf):
    if os.path.exists(cf):
        with open(cf, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"files": {}}

def save_cache(cache, cf):
    with open(cf, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4)

def generate_diff(old, new):
    d = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm='', fromfile='old', tofile='new')
    return "\n".join(d)

def update_cache_and_generate_diff(r, langs, no_ignore, outdir, no_cache=False, skip_patterns=None):
    cf = os.path.join(outdir, 'repindex_cache.json')
    if no_cache:
        if os.path.exists(cf):
            os.remove(cf)
        return
    cache = load_cache(cf)
    old_files = cache.get('files', {})
    current = {}
    for dp, dns, fns in os.walk(r):
        dns[:] = [d for d in dns if not should_ignore(os.path.join(dp, d), langs, no_ignore, skip_patterns)]
        for fn in fns:
            fp = os.path.join(dp, fn)
            try:
                with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                    c = f.read()
                h = compute_file_hash(c)
                current[os.path.relpath(fp, r)] = {"hash": h, "content": c}
            except:
                pass
    changed = []
    for f, d in current.items():
        oldd = old_files.get(f)
        if not oldd or oldd['hash'] != d['hash']:
            changed.append(f)
    removed = [f for f in old_files if f not in current]
    if changed or removed:
        changes_file = os.path.join(outdir, 'repindex_changes.md')
        with open(changes_file, 'w', encoding='utf-8') as cf2:
            cf2.write(f"# Changes since last run ({datetime.datetime.now().isoformat()})\n\n")
            if changed:
                cf2.write("## Changed or New Files:\n\n")
                for f in changed:
                    cf2.write(f"### {f}\n\n")
                    newc = current[f]['content']
                    oldc = old_files.get(f, {}).get('content', '')
                    diff = generate_diff(oldc, newc)
                    if diff.strip():
                        cf2.write("```diff\n" + diff + "\n```\n\n")
                    else:
                        cf2.write("_No diff available (new file)_\n\n")
            if removed:
                cf2.write("## Removed Files:\n\n")
                for f in removed:
                    cf2.write(f"- {f}\n")
    new_cache = {"files": {f: {"hash": d["hash"]} for f, d in current.items()},
                 "timestamp": datetime.datetime.now().isoformat()}
    save_cache(new_cache, cf)

#############################################
# CONTEXT EXTRACTION
#############################################

def gather_dependencies_for_files(r, langs, no_ignore, targets, skip_patterns=None):
    g, fdeps = build_dependency_graph(r, langs, 'full', no_ignore, skip_patterns)
    involved = set()
    def dfs(f):
        if f in involved:
            return
        involved.add(f)
        for e in g['edges']:
            if e['from'] == f and e['type'] == 'import' and e['to']:
                dfs(e['to'])
    for tf in targets:
        if tf in g['nodes']:
            dfs(tf)
    return involved, fdeps

def generate_context_file(r, inv, fdeps, targets, outdir):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    cf = os.path.join(outdir, f"context_{ts}.md")
    with open(cf, 'w', encoding='utf-8') as cfile:
        cfile.write(f"# Context for Files: {', '.join(targets)}\n\n")
        cfile.write("## Involved Files\n\n")
        for f in sorted(inv):
            mk = "(TARGET)" if f in targets else ""
            cfile.write(f"- {f} {mk}\n")
        cfile.write("\n## File Contents\n\n")
        for f in targets:
            fp = os.path.join(r, f)
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as fff:
                    cc = fff.read()
                lang = detect_code_fence_language(os.path.basename(fp))
                cfile.write(f"### {f} (Main)\n\n```{lang}\n{cc}\n```\n\n")
                d = fdeps.get(f, {})
                if 'structure' in d:
                    cfile.write("#### Structure\n\n```json\n" + json.dumps(d['structure'], indent=4) + "\n```\n\n")
        for f in sorted(inv):
            if f not in targets:
                fp = os.path.join(r, f)
                if os.path.exists(fp):
                    with open(fp, 'r', encoding='utf-8') as fff:
                        cc = fff.read()
                    lang = detect_code_fence_language(os.path.basename(fp))
                    cfile.write(f"### {f}\n\n```{lang}\n{cc}\n```\n\n")
                    d = fdeps.get(f, {})
                    if 'structure' in d:
                        cfile.write("#### Structure\n\n```json\n" + json.dumps(d['structure'], indent=4) + "\n```\n\n")
    return cf

#############################################
# MAIN
#############################################

def main():
    parser = argparse.ArgumentParser(description='Index a repository and generate structured outputs.')
    parser.add_argument('repository_path', help='Path to the repository to index')
    parser.add_argument('-o', '--output_dir', default='.', help='Output directory (default: current dir)')
    parser.add_argument('--lang', help='Force a specific language (e.g., python, react)')
    parser.add_argument('--no-ignore', action='store_true', help='Do not ignore default directories')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching & diff generation')
    parser.add_argument('--context-for', nargs='+', help='Generate a context file for specified file(s)')
    parser.add_argument('--minimal', action='store_true', help='Produce minimal outputs')
    parser.add_argument('--skip', type=str, default='', help='Comma-separated list of extra ignore patterns.')
    parser.add_argument('--single-doc', action='store_true',
                        help='Generate a single consolidated Markdown doc with tree, dependencies, code.')
    parser.add_argument('--copy-to-clipboard', action='store_true',
                        help='Copy the single doc output to clipboard (needs pyperclip).')

    args = parser.parse_args()
    repo_path = os.path.abspath(args.repository_path)
    output_dir = os.path.abspath(args.output_dir)
    repindex_out = os.path.join(output_dir, 'repindex')

    if not os.path.isdir(repo_path):
        print(f"Error: '{repo_path}' does not exist or is not a directory.")
        sys.exit(1)

    os.makedirs(repindex_out, exist_ok=True)
    skip_pats = [s.strip() for s in args.skip.split(',') if s.strip()]
    langs = detect_language_type(repo_path, forced_lang=args.lang)

    if args.context_for:
        inv, fdeps = gather_dependencies_for_files(repo_path, langs, args.no_ignore, args.context_for, skip_pats)
        cf = generate_context_file(repo_path, inv, fdeps, args.context_for, repindex_out)
        print(f"Context file generated at: {cf}")
        sys.exit(0)

    if args.single-doc:
        doc = generate_single_context_markdown(repo_path, langs, args.no_ignore, skip_pats)
        if args.copy_to_clipboard:
            if not HAS_CLIPBOARD:
                print("Error: pyperclip not installed. Cannot copy.")
                sys.exit(1)
            pyperclip.copy(doc)
            print("Single doc copied to clipboard.")
        else:
            outfile = os.path.join(repindex_out, 'repindex_single_doc.md')
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"Single doc written to: {outfile}")
        sys.exit(0)

    print("Detecting structure...")
    tree_output = generate_tree_text(repo_path, '', langs, args.no_ignore, skip_pats)
    if not args.minimal:
        with open(os.path.join(repindex_out, 'tree_structure.txt'), 'w', encoding='utf-8') as tf:
            tf.write(os.path.basename(repo_path) + '\n')
            tf.write(tree_output)

    print("Building dependency graphs...")
    dg_full, fdeps = build_dependency_graph(repo_path, langs, 'full', args.no_ignore, skip_pats)
    dg_imports, _ = build_dependency_graph(repo_path, langs, 'imports_only', args.no_ignore, skip_pats)
    dg_exports, _ = build_dependency_graph(repo_path, langs, 'exports_only', args.no_ignore, skip_pats)
    dg_no_objects, _ = build_dependency_graph(repo_path, langs, 'no_objects', args.no_ignore, skip_pats)

    if not args.minimal:
        with open(os.path.join(repindex_out, 'dependency_graph_full.json'), 'w', encoding='utf-8') as jf:
            json.dump(dg_full, jf, indent=4)
        with open(os.path.join(repindex_out, 'dependency_graph_imports.json'), 'w', encoding='utf-8') as jf:
            json.dump(dg_imports, jf, indent=4)
        with open(os.path.join(repindex_out, 'dependency_graph_exports.json'), 'w', encoding='utf-8') as jf:
            json.dump(dg_exports, jf, indent=4)
        with open(os.path.join(repindex_out, 'dependency_graph_no_objects.json'), 'w', encoding='utf-8') as jf:
            json.dump(dg_no_objects, jf, indent=4)
        generate_structure_files(fdeps, repindex_out)
        print("Generating Markdown documentation...")
        md_out = generate_markdown(repo_path, langs, args.no_ignore)
        with open(os.path.join(repindex_out, 'documentation.md'), 'w', encoding='utf-8') as mdf:
            mdf.write(md_out)
        print("Generating light Markdown documentation...")
        lmd_out = generate_light_markdown(repo_path, langs, args.no_ignore)
        with open(os.path.join(repindex_out, 'documentation_light.md'), 'w', encoding='utf-8') as lm:
            lm.write(lmd_out)

    print("Updating cache & generating diffs...")
    update_cache_and_generate_diff(repo_path, langs, args.no_ignore, repindex_out,
                                  no_cache=args.no_cache, skip_patterns=skip_pats)

    print(f"All outputs saved to '{repindex_out}'.")
