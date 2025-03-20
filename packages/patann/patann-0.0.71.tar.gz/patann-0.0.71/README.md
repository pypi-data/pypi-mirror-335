# PatANN - Pattern-Aware Vector Database / ANN

## Overview
PatANN is a massively parallel, distributed, and scalable vector database library for efficient nearest neighbor search across large-scale datasets by finding vector patterns.

## Status
**Beta Version**: Currently uploaded for benchmarking purposes. Complete documentation and updates are under development. Not for production use yet.

## Platforms
- **Beta Version**: Restricted to Linux to prevent premature circulation of beta versions
- **Production Releases (late April 2025)***: Will support all platforms that are supported by mesibo

## Key Features
- Faster Index building and Searching
- Supports both in-memory and on-disk operations
- Dynamic sharding to load balance across servers
- Refined search, filtering and pagination
- Unlimited scalability without pre-specified capacity

## Algorithmic Approach
- Novel pattern-based probing technique for ANN search
- Preliminary results show phenomenal performance in building index and searching
- Potential slight variations in lower-end matching
- Detailed research paper forthcoming

## Contributions
We are seeking help to:

- Run additional datasets. So far, all tested datasets (including self-generated) exhibit patterns that helps algorithm. We have yet to test datasets without clear patterns or with uniform distribution.
- Validate and improve the algorithm

## Contact
For support / questions, please contact: support@mesibo.com

