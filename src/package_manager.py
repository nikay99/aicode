"""
AICode Package Manager

Handles package installation, dependency resolution, and local registry management.
"""

import os
import json
import shutil
import tarfile
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime


@dataclass
class PackageMeta:
    name: str
    version: str
    description: str = ""
    dependencies: Dict[str, str] = field(default_factory=dict)
    author: str = ""
    license: str = "MIT"


@dataclass
class LockfileEntry:
    name: str
    version: str
    resolved: str
    checksum: str
    dependencies: Dict[str, str] = field(default_factory=dict)


@dataclass
class Lockfile:
    version: str = "1.0"
    packages: Dict[str, LockfileEntry] = field(default_factory=dict)
    generated_at: str = ""


class PackageManagerError(Exception):
    """Package manager error."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class SemverVersion:
    """Semantic version parser and comparator."""
    
    def __init__(self, version: str):
        self.original = version
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.prerelease: List[str] = []
        self.build: List[str] = []
        self._parse(version)
    
    def _parse(self, version: str) -> None:
        version = version.lstrip('v')
        parts = version.split('-')
        nums = parts[0].split('.')
        
        if len(nums) >= 1:
            self.major = int(nums[0]) if nums[0] else 0
        if len(nums) >= 2:
            self.minor = int(nums[1]) if nums[1] else 0
        if len(nums) >= 3:
            self.patch = int(nums[2]) if nums[2] else 0
        
        if len(parts) > 1:
            prerelease_parts = parts[1].split('+')
            self.prerelease = prerelease_parts[0].split('.')
            if len(prerelease_parts) > 1:
                self.build = prerelease_parts[1].split('.')
    
    def __str__(self) -> str:
        v = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            v += "-" + ".".join(self.prerelease)
        if self.build:
            v += "+" + ".".join(self.build)
        return v
    
    def __repr__(self) -> str:
        return f"SemverVersion({self.original})"
    
    def _compare_prerelease(self, other: 'SemverVersion') -> int:
        if not self.prerelease and not other.prerelease:
            return 0
        if not self.prerelease:
            return 1
        if not other.prerelease:
            return -1
        
        for i in range(min(len(self.prerelease), len(other.prerelease))):
            a, b = self.prerelease[i], other.prerelease[i]
            a_is_num = a.isdigit()
            b_is_num = b.isdigit()
            
            if a_is_num and b_is_num:
                if int(a) != int(b):
                    return int(a) - int(b)
            elif a_is_num:
                return -1
            elif b_is_num:
                return 1
            elif a != b:
                return -1 if a < b else 1
            else:
                continue
        
        return len(self.prerelease) - len(other.prerelease)
    
    def _compare_build(self, other: 'SemverVersion') -> int:
        if not self.build and not other.build:
            return 0
        if not self.build:
            return 1
        if not other.build:
            return -1
        
        for i in range(min(len(self.build), len(other.build))):
            a, b = self.build[i], other.build[i]
            if a.isdigit() and b.isdigit():
                if int(a) != int(b):
                    return int(a) - int(b)
            elif a != b:
                return -1 if a < b else 1
        return len(self.build) - len(other.build)
    
    def __lt__(self, other: 'SemverVersion') -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        return self._compare_prerelease(other) < 0 or (
            self._compare_prerelease(other) == 0 and self._compare_build(other) < 0
        )
    
    def __le__(self, other: 'SemverVersion') -> bool:
        return self == other or self < other
    
    def __gt__(self, other: 'SemverVersion') -> bool:
        return other < self
    
    def __ge__(self, other: 'SemverVersion') -> bool:
        return self == other or self > other
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SemverVersion):
            return False
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.prerelease == other.prerelease and
                self.build == other.build)


def parse_version_constraint(constraint: str, version: SemverVersion) -> bool:
    """Check if a version satisfies a constraint."""
    constraint = constraint.strip()
    
    if constraint.startswith('^'):
        min_ver = SemverVersion(constraint[1:])
        max_ver = SemverVersion(f"{min_ver.major + 1}.0.0")
        return min_ver <= version < max_ver
    elif constraint.startswith('~'):
        min_ver = SemverVersion(constraint[1:])
        max_ver = SemverVersion(f"{min_ver.major}.{min_ver.minor + 1}.0")
        return min_ver <= version < max_ver
    elif constraint.startswith('>='):
        return version >= SemverVersion(constraint[2:].strip())
    elif constraint.startswith('<='):
        return version <= SemverVersion(constraint[2:].strip())
    elif constraint.startswith('>'):
        return version > SemverVersion(constraint[1:].strip())
    elif constraint.startswith('<'):
        return version < SemverVersion(constraint[1:].strip())
    elif constraint.startswith('=='):
        return version == SemverVersion(constraint[2:].strip())
    else:
        return version == SemverVersion(constraint)


class PackageManager:
    """AICode package manager for local package management."""
    
    def __init__(self, packages_dir: Optional[Path] = None):
        if packages_dir is None:
            home = Path.home()
            self.packages_dir = home / ".aic" / "packages"
            self.registry_index = home / ".aic" / "registry" / "index.json"
            self.lockfile_path = home / ".aic" / "aic.lock"
        else:
            self.packages_dir = packages_dir
            self.registry_index = packages_dir.parent / "registry" / "index.json"
            self.lockfile_path = packages_dir.parent / "aic.lock"
        
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.registry_index.parent.mkdir(parents=True, exist_ok=True)
    
    def parse_aicode_toml(self, content: str) -> PackageMeta:
        """Parse aicode.toml content."""
        meta = PackageMeta(name="", version="0.0.0")
        
        current_section = ""
        for line in content.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                if current_section == 'project':
                    if key == 'name':
                        meta.name = value
                    elif key == 'version':
                        meta.version = value
                    elif key == 'description':
                        meta.description = value
                    elif key == 'author':
                        meta.author = value
                    elif key == 'license':
                        meta.license = value
                elif current_section == 'dependencies':
                    meta.dependencies[key] = value
        
        return meta
    
    def read_aicode_toml(self, path: Path) -> PackageMeta:
        """Read and parse aicode.toml from a path."""
        content = path.read_text()
        return self.parse_aicode_toml(content)
    
    def get_installed_packages(self) -> Dict[str, PackageMeta]:
        """Get all installed packages."""
        packages: Dict[str, PackageMeta] = {}
        
        if not self.packages_dir.exists():
            return packages
        
        for pkg_path in self.packages_dir.iterdir():
            if pkg_path.is_dir():
                toml_path = pkg_path / "aicode.toml"
                if toml_path.exists():
                    try:
                        meta = self.read_aicode_toml(toml_path)
                        packages[meta.name] = meta
                    except Exception:
                        continue
        
        return packages
    
    def is_installed(self, name: str, version: Optional[str] = None) -> bool:
        """Check if a package is installed."""
        packages = self.get_installed_packages()
        
        if name not in packages:
            return False
        
        if version is None:
            return True
        
        pkg_version = SemverVersion(packages[name].version)
        constraint_version = SemverVersion(version)
        return pkg_version == constraint_version
    
    def install_package(self, name: str, version: str, source: Path) -> None:
        """Install a package from a local source."""
        pkg_dir = self.packages_dir / name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        
        if source.is_file() and source.suffix == '.tar':
            with tarfile.open(source, 'r') as tar:
                tar.extractall(pkg_dir)
        else:
            for item in source.iterdir():
                if item.name == '__pycache__':
                    continue
                dest = pkg_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        
        lock_entry = LockfileEntry(
            name=name,
            version=version,
            resolved=str(source),
            checksum=self._calculate_checksum(source),
        )
        self._update_lockfile(name, lock_entry)
        self._update_registry_index(name, version)
    
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of a file or directory."""
        if path.is_file():
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        
        hash_obj = hashlib.sha256()
        for item in sorted(path.rglob('*')):
            if item.is_file() and '__pycache__' not in str(item):
                with open(item, 'rb') as f:
                    hash_obj.update(f.read())
        return hash_obj.hexdigest()
    
    def _update_lockfile(self, name: str, entry: LockfileEntry) -> None:
        """Update the lockfile with a new entry."""
        lockfile = self._read_lockfile()
        lockfile.packages[name] = entry
        lockfile.generated_at = datetime.now().isoformat()
        self._write_lockfile(lockfile)
    
    def _read_lockfile(self) -> Lockfile:
        """Read the lockfile."""
        if not self.lockfile_path.exists():
            return Lockfile()
        
        try:
            data = json.loads(self.lockfile_path.read_text())
            packages = {}
            for name, entry_data in data.get('packages', {}).items():
                packages[name] = LockfileEntry(
                    name=entry_data['name'],
                    version=entry_data['version'],
                    resolved=entry_data['resolved'],
                    checksum=entry_data['checksum'],
                    dependencies=entry_data.get('dependencies', {}),
                )
            return Lockfile(
                version=data.get('version', '1.0'),
                packages=packages,
                generated_at=data.get('generated_at', ''),
            )
        except (json.JSONDecodeError, KeyError):
            return Lockfile()
    
    def _write_lockfile(self, lockfile: Lockfile) -> None:
        """Write the lockfile."""
        data = {
            'version': lockfile.version,
            'generated_at': lockfile.generated_at,
            'packages': {
                name: {
                    'name': entry.name,
                    'version': entry.version,
                    'resolved': entry.resolved,
                    'checksum': entry.checksum,
                    'dependencies': entry.dependencies,
                }
                for name, entry in lockfile.packages.items()
            },
        }
        self.lockfile_path.write_text(json.dumps(data, indent=2))
    
    def _update_registry_index(self, name: str, version: str) -> None:
        """Update the local registry index."""
        index: Dict[str, Dict[str, str]] = {}
        
        if self.registry_index.exists():
            try:
                index = json.loads(self.registry_index.read_text())
            except json.JSONDecodeError:
                index = {}
        
        if name not in index:
            index[name] = {}
        index[name][version] = str(self.packages_dir / name)
        
        self.registry_index.write_text(json.dumps(index, indent=2))
    
    def remove_package(self, name: str) -> None:
        """Remove an installed package."""
        pkg_dir = self.packages_dir / name
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
        
        lockfile = self._read_lockfile()
        if name in lockfile.packages:
            del lockfile.packages[name]
            self._write_lockfile(lockfile)
        
        if self.registry_index.exists():
            try:
                index = json.loads(self.registry_index.read_text())
                if name in index:
                    del index[name]
                    self.registry_index.write_text(json.dumps(index, indent=2))
            except json.JSONDecodeError:
                pass
    
    def list_packages(self) -> List[PackageMeta]:
        """List all installed packages."""
        return list(self.get_installed_packages().values())
    
    def resolve_dependencies(self, meta: PackageMeta) -> Dict[str, str]:
        """Resolve dependencies for a package."""
        resolved: Dict[str, str] = {}
        to_resolve = list(meta.dependencies.items())
        visited: Set[str] = set()
        
        while to_resolve:
            name, constraint = to_resolve.pop(0)
            
            if name in visited:
                continue
            visited.add(name)
            
            resolved[name] = constraint
            
            if name in self.get_installed_packages():
                continue
            
            if self.registry_index.exists():
                try:
                    index = json.loads(self.registry_index.read_text())
                    if name in index:
                        for ver, path in sorted(index[name].items()):
                            ver_obj = SemverVersion(ver)
                            if parse_version_constraint(constraint, ver_obj):
                                resolved[name] = ver
                                break
                except json.JSONDecodeError:
                    pass
        
        return resolved
    
    def install_from_aicode_toml(self, path: Path) -> None:
        """Install all dependencies from a aicode.toml file."""
        meta = self.read_aicode_toml(path)
        
        for name, version in meta.dependencies.items():
            if not self.is_installed(name):
                print(f"Installing {name}@{version}...")
                source = self._find_package_source(name, version)
                if source:
                    self.install_package(name, version, source)
                else:
                    raise PackageManagerError(
                        "E301",
                        f"Package {name}@{version} not found in registry"
                    )
        
        self._update_project_lockfile(path.parent, meta)
    
    def _find_package_source(self, name: str, version: str) -> Optional[Path]:
        """Find package source in local registry."""
        if self.registry_index.exists():
            try:
                index = json.loads(self.registry_index.read_text())
                if name in index:
                    for ver, path in index[name].items():
                        ver_obj = SemverVersion(ver)
                        if parse_version_constraint(version, ver_obj):
                            return Path(path)
            except json.JSONDecodeError:
                pass
        return None
    
    def _update_project_lockfile(self, project_dir: Path, meta: PackageMeta) -> None:
        """Update project's lockfile."""
        lockfile_path = project_dir / "aic.lock"
        lockfile = Lockfile()
        lockfile.generated_at = datetime.now().isoformat()
        
        packages = self.get_installed_packages()
        for dep_name, dep_version in meta.dependencies.items():
            if dep_name in packages:
                pkg = packages[dep_name]
                lockfile.packages[dep_name] = LockfileEntry(
                    name=dep_name,
                    version=pkg.version,
                    resolved=str(self.packages_dir / dep_name),
                    checksum="",
                    dependencies=pkg.dependencies,
                )
        
        data = {
            'version': lockfile.version,
            'generated_at': lockfile.generated_at,
            'packages': {
                name: {
                    'name': entry.name,
                    'version': entry.version,
                    'resolved': entry.resolved,
                    'checksum': entry.checksum,
                    'dependencies': entry.dependencies,
                }
                for name, entry in lockfile.packages.items()
            },
        }
        lockfile_path.write_text(json.dumps(data, indent=2))