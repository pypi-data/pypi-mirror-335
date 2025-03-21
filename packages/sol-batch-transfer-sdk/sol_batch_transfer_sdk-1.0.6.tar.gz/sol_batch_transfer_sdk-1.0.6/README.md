## ⚡ Quickstart

**🐍 The Solana Batch Transfer Python SDK 🐍**

### Installation

1. Install sol-batch-transfer-sdk

```
pip install sol-batch-transfer-sdk
```

### General Usage

```
from sol_batch_transfer_sdk.api import batch_transfer
```

### Example

```
from sol_batch_transfer_sdk.api import batch_transfer

if __name__ == '__main__':
	# sender wallet
    source_signer = 'qSMvYUEY61fTV6ZfdTaBoqHZHUEG6e1FTo9v9dVcw4jZtYyWY4sw5YDBPyywRRjMhF645aNbFoPZbtVFvYjA6qy'
    # fee payer wallet
    fee_payer_str = 'h6d2Wn4cRgBZiZoFJ6ZoFBWosk8Cove2EjD8tk3BWAQ1Mje7v5JVRPMT76NPgJ2ExeDzWgcYcnsQJv2WN3G37FM'
    target_address = [
        ('FetTyW8xAYfd33x4GMHoE7hTuEdWLj1fNnhJuyVMUGGa', 1),
        ('oQPnhXAbLbMuKHESaGrbXT17CyvWCpLyERSJA9HCYd7', 2),
    ]
    batch_transfer(
        source_signer_str=source_signer,
        fee_payer_str=fee_payer_str,
        target_address_list=target_address,
        net_type='mainnet',
        console_print=True,
    )
```

### Parameter description

- source_signer_str [Sender wallet private key]
- fee_payer_str [Transaction Fee Signature Wallet] (If none, use source_signer_str)
- target_address_list [Receiving wallet address and amount]
- net_type [Network type] Optional< mainnet | devnet >
- console_print [Whether to print transaction hash] (Do not print by default)