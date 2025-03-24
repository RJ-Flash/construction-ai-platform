# Changelog

All notable changes to the Construction AI Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Subscription management system
  - Organization model for multi-user environments
  - Multiple subscription plans (Free, Starter, Essential, Professional, Advanced, Ultimate)
  - Plugin licensing system for specialized estimating plugins
  - Usage tracking for billing and analytics
  - Document limit enforcement based on subscription tier
- API endpoints for subscription management
  - Organization management
  - Subscription operations
  - Plugin license management
  - Usage tracking
- User organization relationship
  - Users can be assigned to organizations
  - Organization-level permissions and access control
- Subscription limit enforcement
  - Document upload limits based on subscription plan
  - User seat limits for organizations
  - Plugin access based on valid licenses
- Documentation for subscription management system

### Changed
- Updated document upload endpoint to check subscription limits
- Updated document analysis endpoint to track usage
- Enhanced User model to include organization relationship
- Improved API router to include subscription endpoints

### Fixed
- None

## [0.2.0] - 2025-02-15

### Added
- Plugin system for specialized construction analysis
  - Architectural plugins (Walls, Doors, Windows)
  - Structural plugins (Concrete, Steel, Wood)
  - Base plugin infrastructure for extensibility
- Element extraction from construction documents
  - Automatic identification of construction elements
  - Element properties and dimensions extraction
  - Material type recognition
- Quote generation system
  - Convert extracted elements to quote items
  - Customizable pricing and quantities
  - PDF export for quotes

### Changed
- Enhanced document analysis with specialized plugin support
- Improved UI for element management
- Updated API endpoints for plugin integration

### Fixed
- Document upload error handling
- Project permission checks
- Element duplication in quote generation

## [0.1.0] - 2025-01-10

### Added
- Initial release with core functionality
- Document upload and storage
- Basic AI document analysis
- Project management
- User authentication and authorization
- Frontend UI for document management
