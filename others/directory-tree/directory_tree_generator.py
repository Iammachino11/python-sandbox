#!/usr/bin/env python3
"""
Directory Tree Generator
A professional tool for generating visual directory tree structures.

Author: Machino11
License: MIT
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
from typing import List, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


@dataclass
class TreeStats:
    """Statistics for tree generation."""
    total_dirs: int = 0
    total_files: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass
class TreeConfig:
    """Configuration for tree generation."""
    max_depth: Optional[int] = None
    show_hidden: bool = False
    dirs_only: bool = False
    show_size: bool = False
    show_permissions: bool = False
    ignore_patterns: Set[str] = None

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = set()


class DirectoryTreeGenerator:
    """Generate visual directory tree structures."""

    # Tree drawing characters
    PIPE = '│'
    TEE = '├──'
    ELBOW = '└──'
    SPACE = '    '
    PIPE_SPACE = '│   '

    # Default ignore patterns
    DEFAULT_IGNORE = {
        '__pycache__', '.git', '.svn', '.hg', 'node_modules',
        '.idea', '.vscode', '.DS_Store', 'venv', 'env',
        '.pytest_cache', '.mypy_cache', '__MACOSX'
    }

    def __init__(
            self,
            config: Optional[TreeConfig] = None,
            output_format: OutputFormat = OutputFormat.TEXT,
            verbose: bool = False
    ):
        """
        Initialize the tree generator.

        Args:
            config: TreeConfig object with generation options
            output_format: Output format (text, markdown, html, json)
            verbose: Enable verbose logging
        """
        self.config = config or TreeConfig()
        self.output_format = output_format
        self.stats = TreeStats()

        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Combine default and custom ignore patterns
        self.ignore_patterns = self.DEFAULT_IGNORE | self.config.ignore_patterns

    def should_ignore(self, entry: str) -> bool:
        """
        Check if an entry should be ignored.

        Args:
            entry: Directory or file name

        Returns:
            True if should be ignored, False otherwise
        """
        # Check if hidden
        if not self.config.show_hidden and entry.startswith('.'):
            return True

        # Check ignore patterns
        if entry in self.ignore_patterns:
            return True

        # Check pattern matching (*.pyc, *.log, etc.)
        for pattern in self.ignore_patterns:
            if '*' in pattern:
                # Simple wildcard matching
                if pattern.startswith('*'):
                    if entry.endswith(pattern[1:]):
                        return True
                elif pattern.endswith('*'):
                    if entry.startswith(pattern[:-1]):
                        return True

        return False

    def get_entry_info(self, path: Path) -> str:
        """
        Get additional information about an entry.

        Args:
            path: Path to the entry

        Returns:
            Additional info string
        """
        info_parts = []

        if self.config.show_size and path.is_file():
            try:
                size = path.stat().st_size
                info_parts.append(self._format_size(size))
            except (OSError, PermissionError):
                pass

        if self.config.show_permissions:
            try:
                stat_info = path.stat()
                perms = oct(stat_info.st_mode)[-3:]
                info_parts.append(f"[{perms}]")
            except (OSError, PermissionError):
                pass

        return f" {' '.join(info_parts)}" if info_parts else ""

    def _format_size(self, size: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"({size:.1f}{unit})"
            size /= 1024.0
        return f"({size:.1f}PB)"

    def generate_tree_text(
            self,
            directory: Path,
            prefix: str = '',
            depth: int = 0
    ) -> List[str]:
        """
        Generate tree structure as text lines.

        Args:
            directory: Directory to generate tree for
            prefix: Current line prefix
            depth: Current depth level

        Returns:
            List of tree lines
        """
        lines = []

        # Check max depth
        if self.config.max_depth is not None and depth > self.config.max_depth:
            return lines

        try:
            # Get and sort entries
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

            # Filter entries
            entries = [
                e for e in entries
                if not self.should_ignore(e.name)
                   and (not self.config.dirs_only or e.is_dir())
            ]

        except PermissionError:
            self.stats.errors += 1
            self.logger.debug(f"Permission denied: {directory}")
            return lines
        except Exception as e:
            self.stats.errors += 1
            self.logger.debug(f"Error reading {directory}: {e}")
            return lines

        # Process each entry
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)

            # Update statistics
            if entry.is_dir():
                self.stats.total_dirs += 1
            else:
                self.stats.total_files += 1

            # Determine connector
            connector = self.ELBOW if is_last else self.TEE

            # Get additional info
            info = self.get_entry_info(entry)

            # Add current entry
            lines.append(f"{prefix}{connector} {entry.name}{info}")

            # Process subdirectories
            if entry.is_dir():
                extension = self.SPACE if is_last else self.PIPE_SPACE
                new_prefix = prefix + extension

                # Recursively generate tree for subdirectory
                lines.extend(self.generate_tree_text(entry, new_prefix, depth + 1))

        return lines

    def generate_tree_markdown(
            self,
            directory: Path,
            depth: int = 0
    ) -> List[str]:
        """
        Generate tree structure as Markdown.

        Args:
            directory: Directory to generate tree for
            depth: Current depth level

        Returns:
            List of Markdown lines
        """
        lines = []

        # Check max depth
        if self.config.max_depth is not None and depth > self.config.max_depth:
            return lines

        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            entries = [
                e for e in entries
                if not self.should_ignore(e.name)
                   and (not self.config.dirs_only or e.is_dir())
            ]
        except (PermissionError, Exception) as e:
            self.stats.errors += 1
            return lines

        indent = "  " * depth

        for entry in entries:
            if entry.is_dir():
                self.stats.total_dirs += 1
                lines.append(f"{indent}- **{entry.name}/**")
                lines.extend(self.generate_tree_markdown(entry, depth + 1))
            else:
                self.stats.total_files += 1
                info = self.get_entry_info(entry)
                lines.append(f"{indent}- {entry.name}{info}")

        return lines

    def generate_tree_html(
            self,
            directory: Path,
            tree_data: dict,
            depth: int = 0
    ) -> List[str]:
        """
        Generate a lightweight HTML viewer with embedded JSON data.

        Args:
            directory: Root directory (for title)
            tree_data: Tree data as dict (from generate_tree_json)
            depth: Current depth (used for recursion, but we only generate at depth 0)

        Returns:
            List of HTML lines
        """
        lines = []

        if depth == 0:
            lines.append('<!DOCTYPE html>')
            lines.append('<html>')
            lines.append('<head>')
            lines.append('  <meta charset="UTF-8">')
            lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            lines.append('  <title>Directory Tree - ' + directory.name + '</title>')

            # Font Awesome for icons (CDN)
            lines.append(
                '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">')

            # CSS Styles (same as before)
            lines.append('  <style>')
            lines.append('    * {')
            lines.append('      margin: 0;')
            lines.append('      padding: 0;')
            lines.append('      outline: none;')
            lines.append('      box-sizing: border-box;')
            lines.append('      transition: background-color 0.2s ease, color 0.2s ease;')
            lines.append('    }')
            lines.append('')
            lines.append('    body {')
            lines.append('      font-family: system-ui, -apple-system, "Segoe UI", Roboto, monospace;')
            lines.append('      padding: 20px;')
            lines.append('      min-height: 100vh;')
            lines.append('    }')
            lines.append('')
            lines.append('    /* Themes */')
            lines.append('    body.dark {')
            lines.append('      background: #1a1b26;')
            lines.append('      color: #a9b1d6;')
            lines.append('    }')
            lines.append('    body.light {')
            lines.append('      background: #f8f9fa;')
            lines.append('      color: #2c3e50;')
            lines.append('    }')
            lines.append('    body.dracula {')
            lines.append('      background: #282a36;')
            lines.append('      color: #f8f8f2;')
            lines.append('    }')
            lines.append('    body.nord {')
            lines.append('      background: #2e3440;')
            lines.append('      color: #e5e9f0;')
            lines.append('    }')
            lines.append('')
            lines.append('    /* Controls bar */')
            lines.append('    .controls {')
            lines.append('      position: sticky;')
            lines.append('      top: 10px;')
            lines.append('      z-index: 100;')
            lines.append('      display: flex;')
            lines.append('      gap: 12px;')
            lines.append('      padding: 15px 20px;')
            lines.append('      margin-bottom: 25px;')
            lines.append('      border-radius: 12px;')
            lines.append('      backdrop-filter: blur(10px);')
            lines.append('      -webkit-backdrop-filter: blur(10px);')
            lines.append('      flex-wrap: wrap;')
            lines.append('      align-items: center;')
            lines.append('    }')
            lines.append('')
            lines.append('    body.dark .controls {')
            lines.append('      background: rgba(36, 40, 59, 0.9);')
            lines.append('      border: 1px solid #414868;')
            lines.append('    }')
            lines.append('    body.light .controls {')
            lines.append('      background: rgba(255, 255, 255, 0.9);')
            lines.append('      border: 1px solid #e2e8f0;')
            lines.append('    }')
            lines.append('')
            lines.append('    button, select {')
            lines.append('      padding: 10px 18px;')
            lines.append('      border: none;')
            lines.append('      border-radius: 8px;')
            lines.append('      font-size: 14px;')
            lines.append('      font-weight: 500;')
            lines.append('      cursor: pointer;')
            lines.append('      font-family: inherit;')
            lines.append('      display: flex;')
            lines.append('      align-items: center;')
            lines.append('      gap: 8px;')
            lines.append('    }')
            lines.append('')
            lines.append('    body.dark button, body.dark select {')
            lines.append('      background: #2f334d;')
            lines.append('      color: #c0caf5;')
            lines.append('      border: 1px solid #414868;')
            lines.append('    }')
            lines.append('    body.light button, body.light select {')
            lines.append('      background: white;')
            lines.append('      color: #2c3e50;')
            lines.append('      border: 1px solid #e2e8f0;')
            lines.append('    }')
            lines.append('')
            lines.append('    button:hover {')
            lines.append('      transform: translateY(-1px);')
            lines.append('      box-shadow: 0 4px 12px rgba(0,0,0,0.15);')
            lines.append('    }')
            lines.append('')
            lines.append('    /* Tree container */')
            lines.append('    .tree-container {')
            lines.append('      padding: 10px 0;')
            lines.append('    }')
            lines.append('')
            lines.append('    ul {')
            lines.append('      list-style: none;')
            lines.append('      padding-left: 24px;')
            lines.append('      margin: 8px 0;')
            lines.append('    }')
            lines.append('')
            lines.append('    li {')
            lines.append('      margin: 6px 0;')
            lines.append('      line-height: 1.6;')
            lines.append('      border-radius: 6px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .dir, .file {')
            lines.append('      display: flex;')
            lines.append('      align-items: center;')
            lines.append('      gap: 8px;')
            lines.append('      padding: 4px 8px;')
            lines.append('      border-radius: 6px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .dir {')
            lines.append('      cursor: pointer;')
            lines.append('      font-weight: 500;')
            lines.append('    }')
            lines.append('')
            lines.append('    .dir:hover, .file:hover {')
            lines.append('      background: rgba(255, 255, 255, 0.05);')
            lines.append('    }')
            lines.append('')
            lines.append('    .dir i, .file i {')
            lines.append('      width: 20px;')
            lines.append('      font-size: 16px;')
            lines.append('    }')
            lines.append('')
            lines.append('    body.dark .dir i { color: #7aa2f7; }')
            lines.append('    body.light .dir i { color: #3498db; }')
            lines.append('    body.dark .file i { color: #9ece6a; }')
            lines.append('    body.light .file i { color: #27ae60; }')
            lines.append('')
            lines.append('    .size, .perms {')
            lines.append('      font-size: 12px;')
            lines.append('      opacity: 0.7;')
            lines.append('      margin-left: 8px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .stats {')
            lines.append('      margin-left: auto;')
            lines.append('      display: flex;')
            lines.append('      gap: 16px;')
            lines.append('      font-size: 14px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .stats span {')
            lines.append('      display: flex;')
            lines.append('      align-items: center;')
            lines.append('      gap: 6px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .loading {')
            lines.append('      text-align: center;')
            lines.append('      padding: 50px;')
            lines.append('      font-size: 16px;')
            lines.append('    }')
            lines.append('')
            lines.append('    .error {')
            lines.append('      color: #f7768e;')
            lines.append('      text-align: center;')
            lines.append('      padding: 50px;')
            lines.append('    }')
            lines.append('  </style>')
            lines.append('</head>')
            lines.append('<body class="dark">')
            lines.append('  <div class="controls">')
            lines.append('    <button id="expandBtn"><i class="fas fa-expand-alt"></i> Expand All</button>')
            lines.append(
                '    <button id="collapseBtn"><i class="fas fa-compress-alt"></i> Collapse All</button>')
            lines.append('    <select id="themeSelect" onchange="changeTheme(this.value)">')
            lines.append('      <option value="dark">🌙 Dark Theme</option>')
            lines.append('      <option value="light">☀️ Light Theme</option>')
            lines.append('      <option value="dracula">🧛 Dracula Theme</option>')
            lines.append('      <option value="nord">❄️ Nord Theme</option>')
            lines.append('    </select>')
            lines.append('    <div class="stats" id="stats">')
            lines.append('      <span><i class="fas fa-folder"></i> <span id="dirCount">0</span></span>')
            lines.append('      <span><i class="fas fa-file"></i> <span id="fileCount">0</span></span>')
            lines.append('    </div>')
            lines.append('  </div>')
            lines.append('  <h1><i class="fas fa-folder-open"></i> ' + directory.name + '</h1>')
            lines.append('  <div id="tree" class="tree-container">')
            lines.append(
                '    <div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading directory structure...</div>')
            lines.append('  </div>')

            # === Embed JSON data ===
            lines.append('  <script>')
            lines.append('    // Embedded tree data')
            tree_json = json.dumps(tree_data, indent=2)  # pretty print for readability
            # Escape </script> tags if any (unlikely in file names, but safe)
            tree_json = tree_json.replace('</script>', '<\\/script>')
            lines.append(f'    const treeData = {tree_json};')
            lines.append('')
            lines.append('    function renderTree() {')
            lines.append('      if (!treeData) return;')
            lines.append('      document.getElementById("dirCount").textContent = treeData.stats?.dirs || 0;')
            lines.append('      document.getElementById("fileCount").textContent = treeData.stats?.files || 0;')
            lines.append('      const treeEl = document.getElementById("tree");')
            lines.append('      treeEl.innerHTML = \'\'; // Clear first')
            lines.append('      const ul = document.createElement(\'ul\');')
            lines.append('      ul.innerHTML = buildTreeHTML(treeData, true);')
            lines.append('      treeEl.appendChild(ul);')
            lines.append('      attachEventListeners();')
            lines.append('    }')
            lines.append('')
            lines.append('    function attachEventListeners() {')
            lines.append('      const dirs = document.querySelectorAll(\'.dir\');')
            lines.append('      dirs.forEach(dir => {')
            lines.append('        dir.removeEventListener(\'click\', toggleDirHandler); // Prevent duplicates')
            lines.append('        dir.addEventListener(\'click\', toggleDirHandler);')
            lines.append('      });')
            lines.append('    }')
            lines.append('')
            lines.append('    function toggleDirHandler(e) {')
            lines.append('      const element = e.currentTarget;')
            lines.append('      const sublist = element.nextElementSibling;')
            lines.append('      if (sublist && sublist.tagName === "UL") {')
            lines.append('        const isHidden = sublist.style.display === "none";')
            lines.append('        sublist.style.display = isHidden ? "block" : "none";')
            lines.append(
                '        element.querySelector("i").className = isHidden ? "fas fa-folder-open" : "fas fa-folder";')
            lines.append('      }')
            lines.append('    }')
            lines.append('')
            lines.append('    function buildTreeHTML(node, isRoot = false) {')
            lines.append('      if (!node.children || node.children.length === 0) return "";')
            lines.append('      ')
            lines.append('      const fragment = [];')
            lines.append('      for (const child of node.children) {')
            lines.append('        if (child.type === "directory") {')
            lines.append('          const childrenHTML = buildTreeHTML(child, false);')
            lines.append('          fragment.push(')
            lines.append('            \'<li><div class="dir"><i class="fas fa-folder"></i> \',')
            lines.append('            child.name,')
            lines.append('            \'</div>\',')
            lines.append('            childrenHTML ? \'<ul style="display:none">\' + childrenHTML + \'</ul>\' : \'\',')
            lines.append('            \'</li>\'')
            lines.append('          );')
            lines.append('        } else {')
            lines.append(
                '          const size = child.size ? \' <span class="size">(\' + formatSize(child.size) + \')</span>\' : "";')
            lines.append(
                '          fragment.push(\'<li><div class="file"><i class="fas fa-file"></i> \', child.name, size, \'</div></li>\');')
            lines.append('        }')
            lines.append('      }')
            lines.append('      return fragment.join(\'\');')
            lines.append('    }')
            lines.append('')
            lines.append('    function formatSize(bytes) {')
            lines.append('      if (!bytes) return "0 B";')
            lines.append('      const units = ["B", "KB", "MB", "GB", "TB"];')
            lines.append('      let size = bytes;')
            lines.append('      let unitIndex = 0;')
            lines.append('      while (size >= 1024 && unitIndex < units.length - 1) {')
            lines.append('        size /= 1024;')
            lines.append('        unitIndex++;')
            lines.append('      }')
            lines.append('      return `${size.toFixed(1)} ${units[unitIndex]}`;')
            lines.append('    }')
            lines.append('')
            lines.append('    function expandAll() {')
            lines.append('      const uls = document.querySelectorAll("ul");')
            lines.append('      const icons = document.querySelectorAll(".dir i");')
            lines.append('      for (let i = 0; i < uls.length; i++) uls[i].style.display = "block";')
            lines.append('      for (let i = 0; i < icons.length; i++) icons[i].className = "fas fa-folder-open";')
            lines.append('    }')
            lines.append('')
            lines.append('    function collapseAll() {')
            lines.append('      const uls = document.querySelectorAll("ul:not(:first-child)");')
            lines.append('      const icons = document.querySelectorAll(".dir i");')
            lines.append('      for (let i = 0; i < uls.length; i++) uls[i].style.display = "none";')
            lines.append('      for (let i = 0; i < icons.length; i++) icons[i].className = "fas fa-folder";')
            lines.append('    }')
            lines.append('')
            lines.append('    function changeTheme(theme) {')
            lines.append('      document.body.className = theme;')
            lines.append('      localStorage.setItem("treeTheme", theme);')
            lines.append('    }')
            lines.append('')
            lines.append('    // Attach button event listeners')
            lines.append('    document.getElementById(\'expandBtn\').addEventListener(\'click\', expandAll);')
            lines.append('    document.getElementById(\'collapseBtn\').addEventListener(\'click\', collapseAll);')
            lines.append('')
            lines.append('    // Load saved theme and render')
            lines.append('    const savedTheme = localStorage.getItem("treeTheme") || "dark";')
            lines.append('    document.body.className = savedTheme;')
            lines.append('    document.getElementById("themeSelect").value = savedTheme;')
            lines.append('    renderTree();')
            lines.append('  </script>')
            lines.append('</body>')
            lines.append('</html>')

        return lines

    def generate_tree_json(
            self,
            directory: Path,
            depth: int = 0
    ) -> dict:
        """
        Generate tree structure as JSON.

        Args:
            directory: Directory to generate tree for
            depth: Current depth level

        Returns:
            Dictionary representing tree structure
        """
        # Check max depth
        if self.config.max_depth is not None and depth > self.config.max_depth:
            return {}

        tree = {
            "name": directory.name,
            "type": "directory",
            "children": []
        }

        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            entries = [
                e for e in entries
                if not self.should_ignore(e.name)
                   and (not self.config.dirs_only or e.is_dir())
            ]
        except (PermissionError, Exception) as e:
            self.stats.errors += 1
            tree["error"] = str(e)
            return tree

        for entry in entries:
            if entry.is_dir():
                self.stats.total_dirs += 1
                tree["children"].append(self.generate_tree_json(entry, depth + 1))
            else:
                self.stats.total_files += 1
                file_info = {
                    "name": entry.name,
                    "type": "file"
                }

                if self.config.show_size:
                    try:
                        file_info["size"] = entry.stat().st_size
                    except (OSError, PermissionError):
                        pass

                tree["children"].append(file_info)

        return tree

    def get_extension_for_format(self, format: OutputFormat) -> str:
        """Get the appropriate file extension for the output format."""
        format_extensions = {
            OutputFormat.TEXT: '.txt',
            OutputFormat.MARKDOWN: '.md',
            OutputFormat.HTML: '.html',
            OutputFormat.JSON: '.json'
        }
        return format_extensions.get(format, '.txt')

    def generate_to_file(
            self,
            directory: str,
            output_path: str
    ) -> TreeStats:
        """
        Generate tree and write to file.
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        # Handle file extension
        output_path = Path(output_path)

        # Get the correct extension for the format
        correct_extension = self.get_extension_for_format(self.output_format)

        if not output_path.suffix or output_path.suffix != correct_extension:
            output_path = output_path.with_suffix(correct_extension)
            self.logger.info(f"Adjusted output filename: {output_path}")

        self.logger.info(f"Generating tree for: {directory}")

        try:
            if self.output_format == OutputFormat.HTML:
                # Generate tree data
                tree_data = self.generate_tree_json(dir_path)
                tree_data['stats'] = {
                    'dirs': self.stats.total_dirs,
                    'files': self.stats.total_files,
                    'root': dir_path.name
                }

                # Generate HTML with embedded data
                with open(output_path, 'w', encoding='utf-8') as f:
                    lines = self.generate_tree_html(dir_path, tree_data)
                    f.write('\n'.join(lines))

            elif self.output_format == OutputFormat.JSON:
                with open(output_path, 'w', encoding='utf-8') as f:
                    tree = self.generate_tree_json(dir_path)
                    json.dump(tree, f, indent=2)
            else:
                # Other formats remain the same
                with open(output_path, 'w', encoding='utf-8') as f:
                    if self.output_format == OutputFormat.TEXT:
                        f.write(f"{dir_path.name}\n")
                        lines = self.generate_tree_text(dir_path)
                        f.write('\n'.join(lines))
                    elif self.output_format == OutputFormat.MARKDOWN:
                        f.write(f"# {dir_path.name}\n\n")
                        lines = self.generate_tree_markdown(dir_path)
                        f.write('\n'.join(lines))

            self.logger.info(f"Tree successfully generated: {output_path}")
            return self.stats

        except IOError as e:
            self.logger.error(f"Error writing output: {e}")
            raise

    def generate_to_string(self, directory: str) -> str:
        """
        Generate tree and return as string.

        Args:
            directory: Source directory path

        Returns:
            Tree structure as string
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        if self.output_format == OutputFormat.TEXT:
            lines = [dir_path.name] + self.generate_tree_text(dir_path)
            return '\n'.join(lines)

        elif self.output_format == OutputFormat.MARKDOWN:
            lines = [f"# {dir_path.name}", ""] + self.generate_tree_markdown(dir_path)
            return '\n'.join(lines)

        elif self.output_format == OutputFormat.HTML:
            lines = self.generate_tree_html(dir_path)
            return '\n'.join(lines)

        elif self.output_format == OutputFormat.JSON:
            import json
            tree = self.generate_tree_json(dir_path)
            return json.dumps(tree, indent=2)

        return ""

    def print_stats(self):
        """Print generation statistics."""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("GENERATION STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(f"Total directories: {self.stats.total_dirs}")
        self.logger.info(f"Total files:       {self.stats.total_files}")
        if self.stats.errors > 0:
            self.logger.info(f"Errors:            {self.stats.errors}")
        self.logger.info("=" * 50)


def interactive_mode() -> tuple[str, str, TreeConfig, OutputFormat]:
    """
    Interactive mode for getting user input.

    Returns:
        Tuple of (source_dir, output_path, config, format)
    """
    print("Directory Tree Generator")
    print("=" * 50)

    # Get source directory
    while True:
        source_dir = input("\nEnter the source directory path: ").strip()
        if not source_dir:
            print("Please enter a valid directory path.")
            continue

        source_dir = os.path.normpath(source_dir)

        if not os.path.isdir(source_dir):
            print(f"Error: '{source_dir}' is not a valid directory.")
            continue

        break

    # Get output file path
    while True:
        output_path = input("Enter the output file path (e.g., tree.txt): ").strip()
        if not output_path:
            print("Please enter a valid output file path.")
            continue

        # If user enters just a directory, add default filename
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, "directory_tree")
            print(f"Using filename: {output_path}")

        # Check if output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            create = input(f"Directory '{output_dir}' doesn't exist. Create? (y/n): ").lower()
            if create == 'y':
                try:
                    os.makedirs(output_dir)
                    print(f"Created directory: {output_dir}")
                except OSError as e:
                    print(f"Error: {e}")
                    continue
            else:
                continue

        break

    # Get options
    config = TreeConfig()

    show_hidden = input("\nShow hidden files? (y/n, default: n): ").strip().lower()
    config.show_hidden = show_hidden == 'y'

    dirs_only = input("Show directories only? (y/n, default: n): ").strip().lower()
    config.dirs_only = dirs_only == 'y'

    # Get output format
    print("\nOutput format:")
    print("1. Text (.txt) [default]")
    print("2. Markdown (.md)")
    print("3. HTML (.html)")
    print("4. JSON (.json)")

    format_choice = input("Choose format (1-4, default: 1): ").strip()
    format_map = {
        '1': OutputFormat.TEXT,
        '2': OutputFormat.MARKDOWN,
        '3': OutputFormat.HTML,
        '4': OutputFormat.JSON,
        '': OutputFormat.TEXT
    }
    output_format = format_map.get(format_choice, OutputFormat.TEXT)

    # Show the user what extension will be used
    extension_map = {
        OutputFormat.TEXT: '.txt',
        OutputFormat.MARKDOWN: '.md',
        OutputFormat.HTML: '.html',
        OutputFormat.JSON: '.json'
    }
    print(f"Files will be saved with {extension_map[output_format]} extension")

    return source_dir, output_path, config, output_format


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate visual directory tree structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/dir tree.txt
  %(prog)s /path/to/dir tree.md --format markdown
  %(prog)s /path/to/dir tree.html --format html --show-size
  %(prog)s /path/to/dir -d 2 --dirs-only
  %(prog)s /path/to/dir --show-hidden --ignore node_modules --ignore __pycache__
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        help='Source directory (prompts if not provided)'
    )

    parser.add_argument(
        'output',
        nargs='?',
        help='Output file path (prompts if not provided)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['text', 'markdown', 'html', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '-d', '--max-depth',
        type=int,
        help='Maximum depth to traverse'
    )

    parser.add_argument(
        '-a', '--show-hidden',
        action='store_true',
        help='Show hidden files and directories'
    )

    parser.add_argument(
        '--dirs-only',
        action='store_true',
        help='Show directories only'
    )

    parser.add_argument(
        '-s', '--show-size',
        action='store_true',
        help='Show file sizes'
    )

    parser.add_argument(
        '-p', '--show-permissions',
        action='store_true',
        help='Show file permissions (Unix-like systems)'
    )

    parser.add_argument(
        '-i', '--ignore',
        action='append',
        help='Patterns to ignore (can be used multiple times)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Get directory and output path
    if args.directory and args.output:
        source_dir = args.directory
        output_path = args.output

        # Build config from args
        config = TreeConfig(
            max_depth=args.max_depth,
            show_hidden=args.show_hidden,
            dirs_only=args.dirs_only,
            show_size=args.show_size,
            show_permissions=args.show_permissions,
            ignore_patterns=set(args.ignore) if args.ignore else set()
        )

        output_format = OutputFormat(args.format)

    else:
        # Interactive mode
        try:
            source_dir, output_path, config, output_format = interactive_mode()
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(130)

    # Generate tree
    try:
        generator = DirectoryTreeGenerator(
            config=config,
            output_format=output_format,
            verbose=args.verbose if hasattr(args, 'verbose') else False
        )

        stats = generator.generate_to_file(source_dir, output_path)
        generator.print_stats()

        print(f"\nOutput saved to: {output_path}")

        # Exit with appropriate code
        if stats.errors > 0:
            sys.exit(1)

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose if hasattr(args, 'verbose') else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()