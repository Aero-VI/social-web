# The Web — @nnickkh social graph

A measured map of Nicholas Halka's Instagram orbit. Not estimated, not scraped from a profile page: every edge here came from traversing real follow-graphs.

**Live:** https://friends.aeroverra.com

## What it shows
- **547** accounts followed (the complete list)
- **106** of those accounts had their own follow-graphs fully traversed
- **414** directed edges *between accounts inside his own orbit* — the actual friend web
- **8** communities found by label propagation over that edge set

Node size = how many others in the orbit follow that account. Colour = community. Hover isolates a node's connections.

## Findings
- **@sharonxpr** is the single densest node: 28 shared followings with Nicholas and followed by 10 others in his orbit. The cruise-wife is, mathematically, the hub of his social world.
- Family (`halka`) accounts are overwhelmingly **private**, so they return nothing and sit outside the map by design. That absence is itself a finding.
- Verified accounts (87 of 547) behave as gravity wells, not friendships — they are followed by many and connect to nobody.

## Build
```
python3 crawl.py    # traverse follow-graphs (HikerAPI)
python3 build.py    # edges + label-propagation communities -> data.json
```
Front end is D3 v7 force simulation, no framework.

Built by **Azula**.
