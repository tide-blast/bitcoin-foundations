# Bitcoin Foundations

A personal technical learning journey exploring Bitcoin protocol, software development, and infrastructure. The finished products are small Python tools built from first principles, each with tests and documentation.

I used Bitcoin as a subject due to my enthusiasm for its contributions to the monetary system. (It helped motivate me to complete the work.) The skills I enhanced (reading and explaining a technical system, working with APIs, version control, testing, technical writing) apply well beyond Bitcoin.

Overall Goals:
- Understand Bitcoin at the protocol level
- Learn Linux, Python, networking, and Git
- Build Bitcoin-related tools
- Document technical concepts clearly

## Projects

| Project | What it does | What it shows | Read more |
|---|---|---|---|
| [Raw Transaction Decoder](projects/Raw_Transaction_Decoder) | Decodes a raw Bitcoin transaction (legacy and SegWit) into its fields by parsing the bytes directly, with no third-party dependencies | Byte-level knowledge of the transaction format; tests checked against Bitcoin Core's own decoding | [README](projects/Raw_Transaction_Decoder/README.md) · [Explainer](projects/Raw_Transaction_Decoder/EXPLAINER_Bitcoin_Transaction_Decoder.md) |
| [Node Info Tool](projects/Node_Info_Tool) | Queries a local Bitcoin Core node over RPC and prints one status report: chain and sync state, peer connections, mempool | Working with an API: authentication without hardcoded secrets, clear handling of failures, and tests that run without a node | [README](projects/Node_Info_Tool/README.md) · [Explainer](projects/Node_Info_Tool/EXPLAINER_Bitcoin_Node_Info_Tool.md) |

**Where to start.** For a quick idea of the work, read either project's explainer. Each walks through the concepts behind its tool in plain language. To run something, follow the "Getting started" section of that project's README.

## How the learning is organized

- [`curriculum.md`](curriculum.md) is the plan: eight modules from Git and the Linux terminal through Python, Bitcoin protocol theory and Bitcoin Core, to the two builds above, with what is done and what remains.
- [`progress-log.md`](progress-log.md) is a session-by-session journal, newest first. It records what I covered, what was still open, and where I got confused, so the path (including the stumbles) is visible. I used an LLM to compose this each day to capture my progress from a more objective point of view. (I made some edits for clarity and brevity.)

## How this was built

I worked with an AI assistant as a tutor and reviewer: it explained concepts, helped review my code and highlight bugs, while I wrote and debugged the programs step-by-step. The test suites and some of the project documentation were produced by the assistant. I reviewed and edited them, and I can explain what they do.

## Repository layout

```
bitcoin-foundations/
├── curriculum.md
├── progress-log.md
└── projects/
    ├── Raw_Transaction_Decoder/
    └── Node_Info_Tool/
```

Find me on GitHub: [tide-blast](https://github.com/tide-blast)

Copyright (c) 2026 [tide-blast](https://github.com/tide-blast)

Released under the MIT License. See [LICENSE](LICENSE) for the full text.
