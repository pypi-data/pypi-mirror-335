# PatANN - Pattern-Aware Vector Database / ANN

## Overview
PatANN is a massively parallel, distributed, and scalable vector database library for efficient nearest neighbor search across large-scale datasets by finding vector patterns.

PatANN leverages pattern probing for searching which is a fundamental shift from conventional vector search methodologies. Pattern probing is a preliminary filtering mechanism that examines vector patterns before applying computationally expensive distance metrics. This two-phase approach significantly reduces the search space by quickly identifying potential matches based on pattern similarity rather than calculating exact distances.

While still in beta, PatANN outperforms existing solutions including HNSW, Google ScaNN, Microsoft DiskANN, and Facebook FAISS by large margin.

### How Pattern Probing Works
In it's simplest form, when vectors are indexed in PatANN, the system extracts characteristic patterns from each vector. These patterns represent distinctive features or signatures that can be compared much more efficiently than full vector comparisons. These extracted patterns are then hashed and organized into specialized data structures that allow for rapid lookup and comparison.

During a query, PatANN first examines these pattern hashes to identify a subset of vectors that share similar patterns with the query vector. Only after this preliminary filtering does PatANN apply traditional distance metrics (Euclidean, cosine, etc.) to this smaller candidate set.

However, the actual implementation is more involved. Vectors are encoded at multiple resolutions, capturing both macro and micro patterns within the data. This multi-scale approach ensures that both broad similarities and fine details are considered. The patterns are hashed to maintain  locality of reference, minimizing cross-shard communication during searches.

The PatANN dynamically selects which patterns to prioritize based on the distribution characteristics of the vector space, optimizing for the specific dataset. Also, PatANN employs probabilistic matching rather than exact pattern match to get massive speed advantage while maintaining high recall.

### Performance Implications
This pattern-first approach results in massive performance advantages.

By filtering candidates based on patterns before computing exact distances, PatANN drastically reduces the number of expensive distance calculations.

For disk-based operations, pattern probing allows PatANN to be more selective about which vectors to load from disk, minimizing I/O operations.

Pattern probing operations can be highly parallelized, taking advantage of modern CPU architectures and distributed computing environments. Also, as dataset size increases, the efficiency gains from pattern probing become more pronounced, making PatANN particularly effective for very large-scale vector databases.

### Mathematical Foundation
The pattern probing approach is grounded in information theory and dimensionality reduction techniques. While traditional methods like locality-sensitive hashing (LSH) approximate similarity through random projections, PatANN's pattern probing uses a more structured approach that:

1. Identifies statistically significant patterns in the vector space
2. Leverages these patterns to create a hierarchical filtering system
3. Dynamically adjusts the pattern sensitivity based on the density and distribution of the vector space

This mathematically rigorous foundation ensures that PatANN maintains high recall rates while achieving substantial speedups over conventional ANN implementations.
By combining this pattern probing technique with traditional distance metrics in a tiered approach, PatANN achieves both speed and accuracy, representing a significant advancement in vector search technology.


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

