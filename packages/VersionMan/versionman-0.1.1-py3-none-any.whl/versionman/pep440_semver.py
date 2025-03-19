from __future__ import annotations

from typing import Literal as _Literal
from packaging.version import Version as _Version, InvalidVersion as _InvalidVersion

from versionman.exception import pep440_semver as _exception


class PEP440SemVer:
    def __init__(self, version: str):
        self._version_input = version
        try:
            self._version = _Version(version)
        except _InvalidVersion:
            raise _exception.VersionManInvalidPEP440SemVerError(version)
        if len(self._version.release) != 3:
            raise _exception.VersionManInvalidPEP440SemVerError(
                version, "Release segment must have exactly three numbers"
            )
        if self._version.local:
            raise _exception.VersionManInvalidPEP440SemVerError(
                version, "Local segment is not allowed"
            )
        return

    @property
    def base(self) -> str:
        """The base version string."""
        return self._version.base_version

    @property
    def epoch(self) -> int:
        """The epoch of the version. If unspecified, this is 0."""
        return self._version.epoch

    @property
    def release(self) -> tuple[int, int, int]:
        """The release segment of the version."""
        return self._version.release

    @property
    def pre(self) -> tuple[_Literal["a", "b", "rc"], int] | None:
        """The pre-release segment of the version."""
        return self._version.pre

    @property
    def post(self) -> int | None:
        """The post segment of the version."""
        return self._version.post

    @property
    def dev(self) -> int | None:
        """The dev segment of the version."""
        return self._version.dev

    @property
    def major(self) -> int:
        """The major number of the release segment."""
        return self.release[0]

    @property
    def minor(self) -> int:
        """The minor number of the release segment."""
        return self.release[1]

    @property
    def patch(self) -> int:
        """The patch number of the release segment."""
        return self.release[2]

    @property
    def input(self) -> str:
        """The input string used to create this object."""
        return self._version_input

    @property
    def release_type(self) -> _Literal["final", "pre", "post", "dev"]:
        if self.dev is not None:
            return "dev"
        if self.post is not None:
            return "post"
        if self.pre:
            return "pre"
        return "final"

    @property
    def is_final_like(self) -> bool:
        """Whether the version is final or post-final."""
        return not (self.dev is not None or self.pre)

    @property
    def next_major(self) -> PEP440SemVer:
        """The next major version."""
        return PEP440SemVer(f"{self.major + 1}.0.0")

    @property
    def next_minor(self) -> PEP440SemVer:
        """The next minor version."""
        return PEP440SemVer(f"{self.major}.{self.minor + 1}.0")

    @property
    def next_patch(self) -> PEP440SemVer:
        """The next patch version."""
        return PEP440SemVer(f"{self.major}.{self.minor}.{self.patch + 1}")

    @property
    def next_post(self) -> PEP440SemVer:
        """The next post version."""
        if self.dev is not None:
            raise ValueError("Cannot increment post version of dev version")
        base = self.base
        if self.pre:
            base += f"{self.pre[0]}{self.pre[1]}"
        if self.post is None:
            return PEP440SemVer(f"{base}.post0")
        return PEP440SemVer(f"{base}.post{self.post + 1}")

    def __str__(self):
        return str(self._version)

    def __repr__(self):
        return f'PEP440SemVer("{self.input}")'

    def __hash__(self):
        return hash(self._version)

    def __lt__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__lt__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__lt__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__lt__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")

    def __le__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__le__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__le__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__le__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")

    def __eq__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__eq__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__eq__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__eq__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")

    def __ne__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__ne__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__ne__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__ne__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")

    def __gt__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__gt__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__gt__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__gt__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")

    def __ge__(self, other: str | _Version | "PEP440SemVer"):
        if isinstance(other, str):
            return self._version.__ge__(_Version(other))
        if isinstance(other, _Version):
            return self._version.__ge__(other)
        if isinstance(other, PEP440SemVer):
            return self._version.__ge__(other._version)
        raise TypeError(f"Cannot compare PEP440SemVer with {type(other)}")


def from_tag(tag: str, version_tag_prefix: str = "") -> PEP440SemVer:
    """Create a PEP440SemVer from a tag.

    Parameters
    ----------
    tag : string
        Tag to convert to a PEP440SemVer object.
    version_tag_prefix : string, default: ""
        Prefix to remove from the tag to obtain the version string.

    Returns
    -------
    version: PEP440SemVer
        PEP440SemVer object created from the tag.
    """
    return PEP440SemVer(tag.removeprefix(version_tag_prefix))


def latest_version_from_tags(
    tags: list[str | list[str]],
    version_tag_prefix: str = "",
    release_types: tuple[_Literal["final", "pre", "post", "dev"], ...] = ("final", "pre", "post", "dev"),
    ignore_non_version_tags: bool = True,
) -> PEP440SemVer | None:
    """Get the latest version from a list of (e.g., git) tags.

    Parameters
    ----------
    tags : list
        A sequence of tags or groups of tags, e.g., a list where each element is either a string
        or a list of strings. The main list is expected to be sorted in descending order of relevance,
        e.g., if the order is based on commit date, the most recent commit should be first.
        When an element is a list, the tags in the list are considered to have the same relevance,
        e.g., point to the same commit.
    version_tag_prefix : string, default: ""
        If given, only tags starting with this prefix are considered.
    release_types : tuple, default: ("final", "pre", "post", "dev")
        Type of release versions to consider. By default, all types are considered.
    ignore_non_version_tags : boolean, default: True
        If set to False, any tag with the given prefix (by default, all tags) that is not a valid
        version tag will raise an error. Otherwise (default), such tags are ignored.

    Returns
    -------
    latest_version: PEP440SemVer | None
        Latest version found in the tags, or None if no version tag is found.
    """

    def get_latest_version(tags_list: list[str]) -> PEP440SemVer | None:
        ver_tags = []
        for tag in tags_list:
            if tag.startswith(version_tag_prefix):
                try:
                    version = PEP440SemVer(tag.removeprefix(version_tag_prefix))
                except _exception.VersionManInvalidPEP440SemVerError as e:
                    if ignore_non_version_tags:
                        continue
                    raise e
                ver_tags.append(version)
        if not ver_tags:
            return
        ver_tags = sorted(ver_tags, reverse=True)
        for ver_tag in ver_tags:
            if ver_tag.release_type in release_types:
                return ver_tag
        return

    for tag_group in tags:
        if isinstance(tag_group, str):
            tag_group = [tag_group]
        latest_version = get_latest_version(tag_group)
        if latest_version:
            return latest_version
    return
