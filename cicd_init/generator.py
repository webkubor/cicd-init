"""Main generation orchestrator."""

import os
from pathlib import Path

from cicd_init.detect import detect_project
from cicd_init.templates import generate_gitlab_ci, generate_github_actions


def generate(
    project_dir=".",
    platforms=None,
    dry_run=False,
    node_version=None,
):
    """
    Generate CI/CD configuration files.

    Args:
        project_dir: Path to the project root directory.
        platforms: List of platforms to generate ('gitlab', 'github').
                   Auto-detect from git remote if None.
        dry_run: If True, print config without writing files.
        node_version: Override detected Node.js major version.

    Returns:
        List of generated file paths (empty if dry_run).
    """
    config = detect_project(project_dir)

    if node_version:
        config["node_version"] = node_version

    # Determine target platforms
    if platforms:
        targets = [p.lower() for p in platforms]
    elif config["git_platform"]:
        targets = [config["git_platform"]]
    else:
        targets = ["github"]  # Default to GitHub

    generated = []

    for target in targets:
        if target == "gitlab":
            content = generate_gitlab_ci(config)
            output_path = os.path.join(project_dir, ".gitlab-ci.yml")
        elif target == "github":
            content = generate_github_actions(config)
            output_path = os.path.join(project_dir, ".github", "workflows", "ci.yml")
        else:
            raise ValueError(f"Unsupported platform: {target}. Use 'gitlab' or 'github'.")

        if dry_run:
            print(f"\n{'=' * 60}")
            print(f"  {output_path}")
            print(f"{'=' * 60}")
            print(content)
            continue

        # Write file
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

        print(f"✅ Generated: {output_path}")
        generated.append(output_path)

    return generated
