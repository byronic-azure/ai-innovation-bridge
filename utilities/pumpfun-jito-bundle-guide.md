# Pump.fun Jito Bundle Example with Result Check

The JavaScript snippet below demonstrates sending a bundle to the Jito block engine after generating and signing Pump.fun transactions. It now captures and verifies the Jito response before continuing, logging any errors or the returned bundle ID.

```javascript
import { VersionedTransaction, Keypair } from '@solana/web3.js';
import bs58 from 'bs58';

async function sendTransactionBundle() {
  const signerKeyPairs = [
    Keypair.fromSecretKey(bs58.decode('Wallet A base 58 private key here')),
    Keypair.fromSecretKey(bs58.decode('Wallet B base 58 private key here')),
  ];

  const bundledTxArgs = [
    {
      publicKey: signerKeyPairs[0].publicKey.toBase58(),
      action: 'buy',
      mint: '2xHkesAQteG9yz48SDaVAtKdFU6Bvdo9sXS3uQCbpump',
      denominatedInSol: 'false',
      amount: 1000000,
      slippage: 50,
      priorityFee: 0.00005,
      pool: 'pump',
    },
    {
      publicKey: signerKeyPairs[1].publicKey.toBase58(),
      action: 'buy',
      mint: '2xHkesAQteG9yz48SDaVAtKdFU6Bvdo9sXS3uQCbpump',
      denominatedInSol: 'false',
      amount: 1000000,
      slippage: 50,
      priorityFee: 0.0,
      pool: 'pump',
    },
  ];

  const response = await fetch('https://pumpportal.fun/api/trade-local', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bundledTxArgs),
  });

  if (response.status !== 200) {
    console.error(response.statusText);
    return;
  }

  const transactions = await response.json();
  const encodedSignedTransactions = [];
  const signatures = [];

  for (let i = 0; i < bundledTxArgs.length; i++) {
    const tx = VersionedTransaction.deserialize(new Uint8Array(bs58.decode(transactions[i])));
    tx.sign([signerKeyPairs[i]]);
    encodedSignedTransactions.push(bs58.encode(tx.serialize()));
    signatures.push(bs58.encode(tx.signatures[0]));
  }

  const jitoResponse = await fetch('https://mainnet.block-engine.jito.wtf/api/v1/bundles', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'sendBundle',
      params: [encodedSignedTransactions],
    }),
  });

  const jitoResult = await jitoResponse.json();
  if (jitoResult.error) {
    console.error('Jito bundle error:', jitoResult.error);
    return;
  }
  console.log('Bundle ID:', jitoResult.result);

  signatures.forEach((sig, i) => console.log(`Transaction ${i}: https://solscan.io/tx/${sig}`));
}

sendTransactionBundle();
```
