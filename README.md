# DeadW3 Documentation

> Documentation repository for the **DeadW3 Protocol**: A decentralized, censorship-resistant preservation system for cultural archives on Arweave.

---

## 🎵 About DeadW3

**DeadW3** (Decentralized Archive Preservation Protocol) creates a sustainable framework for preserving humanity's digital heritage, starting with Grateful Dead live music recordings. The protocol combines:

- **Arweave** for permanent decentralized storage
- **Clanker token deployment** with automatic liquidity for sustainable funding
- **AI-assisted verification** for data integrity and policy compliance
- **Blockchain registry** on Base network for transparent provenance
- **DAO governance** for community-driven curation

### Mission

> To ensure that the world's cultural and digital memory — from music to the web itself — outlives the platforms that host it, sustained by community-driven economic activity.

### Vision

A decentralized ecosystem where archivists, curators, and AI agents collaborate to mirror and preserve humanity's shared history in permanent, verifiable form, funded by a self-sustaining tokenomic model that converts trading activity into permanent storage capacity.

---

## 📁 Repository Structure

```
docs/
├── protocol/              # Protocol specifications and whitepapers
│   ├── DeadW3_Whitepaper_v0.3.md    # Latest protocol specification
│   └── DeadW3_Whitepaper_v0.2.md    # Previous version
│
├── planning/              # Development planning documents
│   └── DeadW3 Protocol: Two-Week Foundation Sprint.md
│
├── prompts/               # AI assistant instructions
│   └── DeadW3_Builder_GPT_Instructions.md
│
├── Crawler/              # Internet Archive documentation crawler
│   ├── crawl_archive_docs.py        # Archive.org developer docs crawler
│   ├── crawl_clanker_docs.py        # Clanker documentation crawler
│   ├── combine_docs.py              # Combine docs for GPT instructions
│   ├── archive_docs/                 # Crawled Archive.org docs
│   ├── clanker_docs/                 # Crawled Clanker docs
│   └── combined_docs/               # Combined documentation outputs
│
└── README.md             # This file
```

---

## 📚 Documentation Guide

### Protocol Specifications

The `protocol/` directory contains the technical specifications for DeadW3:

- **[DeadW3 Whitepaper v0.3](./protocol/DeadW3_Whitepaper_v0.3.md)** - Current protocol specification with Clanker integration
- **[DeadW3 Whitepaper v0.2](./protocol/DeadW3_Whitepaper_v0.2.md)** - Previous version for reference

**Key Topics Covered:**
- System architecture and component layers
- Tokenomics and economic model (Clanker integration)
- Storage layer (Arweave + ANS-104 bundles)
- Verification pipeline (AI + LLM analysis)
- Blockchain contracts (Base network)
- Governance and DAO structure
- Technical implementation details

### Development Planning

The `planning/` directory contains development roadmaps and sprint plans:

- **[Two-Week Foundation Sprint](./planning/DeadW3%20Protocol%20Two-Week%20Foundation%20Sprint.md)** - Detailed 14-day sprint plan establishing the technical foundation

**Includes:**
- Repository architecture and setup
- Smart contract implementation roadmap
- Storage integration tasks
- Verification service development
- API and database schema design
- Testing and documentation requirements

### Developer Resources

The `Crawler/` directory contains tools and documentation for working with Internet Archive and Clanker:

- **[Crawler README](./Crawler/README.md)** - Documentation crawler setup and usage
- Scripts to crawl Archive.org developer documentation
- Scripts to crawl Clanker protocol documentation
- Combined documentation outputs for AI assistant context

---

## 🚀 Quick Start

### For Developers

1. **Read the Whitepaper**: Start with [DeadW3 Whitepaper v0.3](./protocol/DeadW3_Whitepaper_v0.3.md) to understand the protocol architecture
2. **Review Planning Docs**: Check the [Two-Week Sprint Plan](./planning/DeadW3%20Protocol%20Two-Week%20Foundation%20Sprint.md) for implementation roadmap
3. **Explore Crawlers**: Use the [Crawler tools](./Crawler/) to gather Internet Archive and Clanker documentation

### For Contributors

- Review the planning documents to identify areas needing development
- Check protocol specifications for technical requirements
- Use the crawler tools to gather up-to-date documentation for AI assistants

---

## 🔗 Related Repositories

DeadW3 uses a multi-repository structure:

- **deadw3-contracts** - Smart contracts (Solidity/Foundry)
- **deadw3-protocol** - API service, indexer, database (TypeScript)
- **deadw3-verifier** - AI verification service (Python/FastAPI)
- **deadw3-explorer** - Frontend application (Next.js)
- **deadw3-docs** - This repository (documentation)

---

## 📋 Key Concepts

### Storage Layer
- Permanent storage on **Arweave** using **ANS-104 bundles**
- Metadata stored as **Arweave tags** (show date, venue, lineage, etc.)
- **BLAKE3 hashes** for integrity verification

### Verification Pipeline
- **Integrity checks**: Manifest parsing, hash verification
- **Audio quality analysis**: Clipping, SNR, spectrogram analysis
- **Duplicate detection**: Chromaprint fingerprinting
- **Policy compliance**: LLM-based evaluation of Archive.org policies

### Economic Model
- **Clanker token deployment** ($DEADW3) with automatic Uniswap v4 liquidity
- **80% of trading fees** fund DAO treasury
- **Treasury funds** Arweave storage and uploader rewards
- **Self-sustaining** revenue model for perpetual preservation

### Governance
- **DAO structure**: Root DAO and Curator DAO
- **Token-based voting**: DEADW3 holders participate in governance
- **Proposal system**: Transparent decision-making process

---

## 📝 License

This documentation is licensed under **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International).

---

## 🤝 Contributing

Contributions to documentation are welcome! Please:

1. Review existing documentation for style and structure
2. Follow markdown formatting standards
3. Include clear, accurate technical details
4. Update version numbers and dates appropriately

---

## 📧 Contact

For questions about DeadW3 Protocol:
- **GitHub Organization**: https://github.com/DeadW3
- **Author**: BoilerHaus / DeadW3 Core

---

## 🗺️ Status

**Current Version**: v0.3 - Clanker Integration  
**Status**: Planning and Development Phase  
**Last Updated**: 2025-11-02

---

*Preserving the Grateful Dead Archives — and the Internet's Memory — on Arweave*
