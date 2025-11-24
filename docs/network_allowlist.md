# Network Allowlist

This document captures the externally hosted services that the stop-azs toolchain is permitted to contact when downloading dependencies, verifying signatures, or retrieving official SDK/runtime installers.  The domains are grouped by the ecosystems they support so that automated build or bootstrap tooling can quickly determine whether an outbound request is expected.

## Using This List

- Treat the entries as the authoritative source for firewall or proxy rules used by CI, developer workstations, and the Windows NAS bootstrap bundle.
- When new tooling requires additional destinations, submit a pull request that updates this document and reference the relevant installer or package feed.
- Subdomains of the listed hosts are implicitly allowed unless otherwise noted.

## Approved Domains

### Operating System & Distribution Repositories
- `alpinelinux.org`
- `archlinux.org`
- `centos.org`
- `debian.org`
- `fedoraproject.org`
- `ubuntu.com`
- `launchpad.net`
- `ppa.launchpad.net`
- `packagecloud.io`
- `packages.microsoft.com`
- `apt.llvm.org`

### Container Registries & Cloud Artifacts
- `docker.com`
- `docker.io`
- `gcr.io`
- `ghcr.io`
- `quay.io`
- `mcr.microsoft.com`
- `k8s.io`

### Programming Language Ecosystems
- `pythonhosted.org`
- `pypi.python.org`
- `pypi.org`
- `pypa.io`
- `rubygems.org`
- `ruby-lang.org`
- `rubyforge.org`
- `rubyonrails.org`
- `npmjs.org`
- `npmjs.com`
- `nodejs.org`
- `nuget.org`
- `hex.pm`
- `crates.io`
- `pkg.go.dev`
- `golang.org`
- `haskell.org`
- `cpan.org`
- `metacpan.org`
- `pub.dev`
- `swift.org`
- `rustup.rs`
- `rvm.io`
- `packagist.org`
- `cocoapods.org`

### Java & JVM Tooling
- `java.com`
- `java.net`
- `maven.org`
- `jcenter.bintray.com`
- `gradle.org`

### Microsoft & .NET Ecosystem
- `dot.net`
- `dotnet.microsoft.com`
- `visualstudio.com`
- `azure.com`
- `microsoft.com`
- `cdn.winget.microsoft.com`
- `winget.azureedge.net`

### Developer Platforms & Source Hosting
- `github.com`
- `githubusercontent.com`
- `gitlab.com`
- `bitbucket.org`
- `sourceforge.net`
- `apache.org`
- `spring.io`
- `hashicorp.com`
- `google.com`
- `eclipse.org`
- `anaconda.com`
- `continuum.io`
- `oracle.com`
- `golang.org`
- `json-schema.org`
- `json.schemastore.org`
- `bower.io`
- `goproxy.io`
- `gradle.org`
- `nodejs.org`
- `npmjs.org`
- `npmjs.com`
- `packages.microsoft.com`
- `packagecloud.io`
- `packagist.org`
- `rubygems.org`
- `swift.org`
- `yarnpkg.com`

### Additional Notes
- The allowlist intentionally overlaps across categories (for example, `golang.org` supports both module downloads and language documentation).  When configuring outbound rules, deduplicate entries as needed.
- `google.com` is restricted to API calls needed for dependency verification (e.g., checking official checksum manifests).  Wider web browsing should still be blocked by default.
