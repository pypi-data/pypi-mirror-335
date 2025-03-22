# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-02

### Added
- Initial release of the Postchain Python Client
- Full asynchronous API support using `aiohttp`
- Secure transaction creation and signing
- GTV (Generic Type Value) encoding/decoding
- Comprehensive blockchain querying capabilities
- Transaction status polling and confirmation
- Failover strategies for node communication
- Extensive test coverage with pytest
- Type hints throughout for better development experience
- Example implementations in examples directory
- Comprehensive documentation in README.md

### Dependencies
- Python 3.7+
- aiohttp>=3.8.0
- cryptography>=3.4.7
- pyasn1>=0.4.8
- ecdsa>=0.18.0
- coincurve>=18.0.0
- python-dotenv>=0.19.0
- asn1crypto>=1.4.0
- asn1>=2.6.0

[0.1.0]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.0 

## [0.1.1] - 2025-01-10

### Added
- Added multi-signature support for transactions.
- Added pipeline on Bitbucket.
- Removed unused code.


[0.1.1]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.1 


## [0.1.2] - 2025-01-17

### Added
- Added CHANGELOG.md
- Added new versioning
- Added MIT license to README.md

[0.1.2]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.2 

## [0.1.3] - 2025-01-17

### Added
- Added pypirc configurations
- Updated README.md
- Unused module (common) removed

[0.1.3]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.3 

## [0.1.4] - 2025-01-20

### Fixed
- Added missing packages to the pyproject.toml

[0.1.4]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.4 

## [0.1.5] - 2025-01-22

### Added
- Added rich for pretty printing on tests (dev environment)
- Added integration tests for multi-signature transactions

### Fixed
- Fixed the multi signature transaction serialization to fix sending the transaction to the blockchain


[0.1.5]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.5 

## [0.1.6] - 2025-01-22

### Added
- Added integration tests for querying the blockchain

### Fixed
- Fixed the query response handling when getting singular type response
- Fixed add_signature method to handle multisig transactions

[0.1.6]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.6 

## [0.1.7] - 2025-01-28

### Added
- Added dynamic node discovery via directory node URL pools
- Added support for connecting to blockchain nodes through a directory service
- Added new test cases for node discovery functionality
- Added test for Merkle hash calculator and GTV hash verification

### Fixed
- Updated error message format for query parameter validation
- Improved node URL handling and validation

[0.1.7]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.7
