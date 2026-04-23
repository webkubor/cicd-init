"""Project detection module.

Detects git remote, package manager, framework, Node.js version, etc.
"""
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional


def run_cmd(cmd, cwd=None):
    """Run a command and return stdout."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def detect_git_remote(project_dir="."):
    """Detect git remote platform: 'github', 'gitlab', or None."""
    output = run_cmd(["git", "remote", "-v"], cwd=project_dir)
    if not output:
        return None

    for line in output.splitlines():
        if "fetch" in line or "push" in line:
            if "github.com" in line:
                return "github"
            if "gitlab.com" in line:
                return "gitlab"
            # Self-hosted patterns
            if re.search(r"gitlab\.\w+", line):
                return "gitlab"
            if re.search(r"github\.\w+", line):
                return "github"

    return None


def detect_package_manager(project_dir="."):
    """Detect package manager: 'npm', 'yarn', or 'pnpm'."""
    base = Path(project_dir)
    if (base / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (base / "yarn.lock").exists():
        # Yarn 2+ (berry) detection
        pkg_yarn = base / ".yarn" / "rc.yml"
        if pkg_yarn.exists() or (base / ".yarnrc.yml").exists():
            return "yarn-berry"
        return "yarn"
    if (base / "package-lock.json").exists():
        return "npm"
    # Default to npm if package.json exists
    if (base / "package.json").exists():
        return "npm"
    return "npm"


def detect_framework(project_dir="."):
    """Detect frontend framework.

    Returns: 'react', 'vue', 'angular', 'next', 'nuxt', 'svelte', 'vite', 'webpack', or 'unknown'.
    """
    pkg_path = Path(project_dir) / "package.json"
    if not pkg_path.exists():
        return "unknown"

    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, OSError):
        return "unknown"

    deps = {}
    for section in ("dependencies", "devDependencies"):
        deps.update(pkg.get(section, {}))

    dep_names = {k.lower() for k in deps.keys()}

    # Next.js (before React since it depends on React)
    if "next" in dep_names:
        return "next"

    # Nuxt (before Vue since it depends on Vue)
    if "nuxt" in dep_names or "nuxt3" in dep_names:
        return "nuxt"

    # React
    if {"react", "react-dom"} & dep_names and "@angular/core" not in dep_names:
        return "react"

    # Vue
    if "vue" in dep_names:
        return "vue"

    # Angular
    if "@angular/core" in dep_names:
        return "angular"

    # Svelte / SvelteKit
    if {"svelte", "@sveltejs/kit"} & dep_names:
        return "svelte"

    # Generic Vite
    if "vite" in dep_names:
        return "vite"

    # Webpack fallback
    if "webpack" in dep_names:
        return "webpack"

    return "unknown"


def detect_node_version(project_dir="."):
    """Detect Node.js major version from .nvmrc, .node-version, or package.json engines."""
    base = Path(project_dir)

    # .nvmrc
    nvmrc = base / ".nvmrc"
    if nvmrc.exists():
        try:
            content = nvmrc.read_text(encoding="utf-8").strip()
            match = re.search(r"(\d+)\.", content)
            if match:
                return match.group(1)
        except OSError:
            pass

    # .node-version
    node_ver = base / ".node-version"
    if node_ver.exists():
        try:
            content = node_ver.read_text(encoding="utf-8").strip()
            match = re.search(r"(\d+)\.", content)
            if match:
                return match.group(1)
        except OSError:
            pass

    # package.json engines
    pkg_path = base / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            engines = pkg.get("engines", {})
            node_range = engines.get("node", "")
            match = re.search(r"(\d+)\.", node_range)
            if match:
                return match.group(1)
        except (json.JSONDecodeError, OSError):
            pass

    return "20"


def detect_build_output(framework, project_dir="."):
    """Detect build output directory based on framework."""
    base = Path(project_dir)

    output_map = {
        "react": "dist",
        "vue": "dist",
        "angular": "dist",
        "next": ".next",
        "nuxt": ".output/public",
        "svelte": "build",
        "vite": "dist",
        "webpack": "dist",
    }

    if framework in output_map:
        # CRA uses build/
        if framework in ("react", "vue"):
            vite_configs = list(base.glob("vite.config.*"))
            if vite_configs:
                return "dist"
            pkg_path = base / "package.json"
            if pkg_path.exists():
                try:
                    with open(pkg_path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                    dev_deps = pkg.get("devDependencies", {})
                    if "react-scripts" in dev_deps:
                        return "build"
                except (json.JSONDecodeError, OSError):
                    pass
        return output_map[framework]

    return "dist"


def detect_scripts(project_dir="."):
    """Detect available npm scripts."""
    pkg_path = Path(project_dir) / "package.json"
    if not pkg_path.exists():
        return {}

    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        scripts = pkg.get("scripts", {})
        return {
            "lint": "lint" in scripts,
            "test": "test" in scripts,
            "build": "build" in scripts,
            "typecheck": "typecheck" in scripts or "type-check" in scripts,
            "typecheck_script": "typecheck" if "typecheck" in scripts else ("type-check" if "type-check" in scripts else None),
        }
    except (json.JSONDecodeError, OSError):
        return {}


def get_package_manager_commands(pm):
    """Get install/run commands for a package manager."""
    commands = {
        "npm": {
            "install": "npm ci",
            "run": "npm run",
            "lockfile": "package-lock.json",
            "gh_cache": "npm",
        },
        "yarn": {
            "install": "yarn install --frozen-lockfile",
            "run": "yarn",
            "lockfile": "yarn.lock",
            "gh_cache": "yarn",
        },
        "yarn-berry": {
            "install": "yarn install --immutable",
            "run": "yarn",
            "lockfile": "yarn.lock",
            "gh_cache": "yarn",
        },
        "pnpm": {
            "install": "pnpm install --frozen-lockfile",
            "run": "pnpm run",
            "lockfile": "pnpm-lock.yaml",
            "gh_cache": "pnpm",
        },
    }
    return commands.get(pm, commands["npm"])


def detect_project(project_dir="."):
    """Detect all project information and return a config dict."""
    framework = detect_framework(project_dir)
    pm = detect_package_manager(project_dir)
    node_version = detect_node_version(project_dir)
    build_output = detect_build_output(framework, project_dir)
    scripts = detect_scripts(project_dir)
    git_platform = detect_git_remote(project_dir)
    pm_cmds = get_package_manager_commands(pm)

    # Determine run command prefix
    if pm in ("yarn", "yarn-berry"):
        run_prefix = "yarn"
    elif pm == "pnpm":
        run_prefix = "pnpm run"
    else:
        run_prefix = "npm run"

    return {
        "framework": framework,
        "package_manager": pm,
        "node_version": node_version,
        "build_output": build_output,
        "scripts": scripts,
        "git_platform": git_platform,
        "pm": pm_cmds,
        "run_prefix": run_prefix,
    }
