# Changelog

## [0.1.0] - 2024-03-22

### Added
- Initial implementation of Kubernetes MCP server
- Core functionality:
  - Connection to Kubernetes clusters
  - Pod, service, deployment, and node management
  - Helm v3 support
  - Kubectl explain and api-resources
  - Namespace management with `set_namespace` tool
  - Port forwarding with `port_forward`, `stop_port_forward`, and `list_port_forwards` tools
- Type definitions for resources, port forwarding, and watches
- Tests for core functionality 