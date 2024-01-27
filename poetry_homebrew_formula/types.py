from dataclasses import dataclass


@dataclass
class PackageInfo:
    name: str
    url: str
    checksum: str | None
    checksum_name: str | None


@dataclass
class RootPackageInfo(PackageInfo):
    description: str
    homepage: str | None
    license: str | None  # noqa: A003
