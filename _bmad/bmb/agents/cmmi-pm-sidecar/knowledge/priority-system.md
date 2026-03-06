# Priority System Definition
## P0 / P1 / P2 Standards

This document defines the standard priority levels used across all CMMI-PM generated artifacts.

### P0 (Must Have) - Critical
**Definition**: Essential features without which the product cannot work or cannot be released.
**Impact**: Failure to deliver blocks the release.
**Examples**:
- Core login/authentication
- Basic CRUD operations for main entities
- Security & Compliance requirements associated with legal risks

### P1 (Should Have) - Important
**Definition**: Important features that are not critical for the immediate release but should be included if possible. Workarounds may exist.
**Impact**: Failure to deliver causes pain but does not block release.
**Examples**:
- Advanced filtering/search
- Bulk operations
- Performance optimizations beyond baseline

### P2 (Nice to Have) - Desirable
**Definition**: Features that add value but are not time-critical. Can be deferred to future releases.
**Impact**: Minimal impact if deferred.
**Examples**:
- UI animations/polish
- Nice-to-have integrations
- Experimental features

### Mapping to CMMI/MoSCoW
| Priority | MoSCoW | CMMI Level |
|---|---|---|
| **P0** | Must Have | Mandatory |
| **P1** | Should Have | Expected |
| **P2** | Could Have / Won't Have | Optional |
