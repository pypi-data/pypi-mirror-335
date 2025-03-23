# mach-client-py

This library contains 2 things:

- A client for the [Mach exchange](https://www.mach.exchange/) and [asset server](https://tokens.machprotocol.com/docs)
- A strongly typed set of abstractions used for working with clients, transactions, tokens, accounts and scanners on smart contract chains

## Getting Started

Create a copy of the `template.config.yaml` file:

```bash
cp template.config.yaml config.yaml
```

Edit the config to add the credentials for the account you wish to run the example with:

```yaml
accounts:
  ethereum: "YOUR PRIVATE KEY"
  solana: "..."
  tron: "..."
# ...
```

Then look at the notebook in the `examples/` directory.
