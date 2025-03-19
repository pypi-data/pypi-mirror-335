# Changelog

## v2.0.8.41 - Date

**Improvement**:

- TBD

**New Features**:

- Fully Featured, Tool Agnostic Event Messaging, Currently Includes the following tool support:
  - RabbitMQ (Synchronous & Asynchronous Implementation)
  - Kafka (Synchronous & Asynchronous Implementation)
  - PubSub (Synchronous & Asynchronous Implementation)
- All Implementations are OOP based (Abstract Polymorphic Implementation)

## [2.0.8.44] - 2024-03-18
- Added TAG_DESCRIPTION_MANAGER microservice to KAL-SENSE services group with port 8084

## [2.0.8.43] - 2024-03-18
- Added ONPREM environment type for on-premises deployment

## [2.0.8.42] - 2024-03-18
- Added support for multiple environments (LOCAL, CLOUD, PYCHARM, QA, IT, PROD)
- Added domain property to Environment enum
- Fixed service type handling in URL generation for cloud environment
- Updated ports organization for all services
