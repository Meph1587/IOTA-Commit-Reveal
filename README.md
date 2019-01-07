# IOTA-Commit-Reveal
Python Implementation of the Commit Reveal Scheme Using IOTA 


## What is Commit Reveal?
Commit-Reveal is a Cryptographic primitive which allows user Alice to proof knowledge/posession of a statement "S" at time "T" without giving away any information about statement "S". 
Commit-Reveal is done in two Steps: 
- the commit phase at time "T" in which Alice commits the encrypted statement 
- the reveal phase at time "T+1" in which Alice reveals the statement and the key to Proof that the revealed statement is the    same as the commited one

## How is it Implemented?
To implement Commit-Reveal using IOTA we need to make 2 0-value transactions.

The first transaction is the commit transaction. Its message field contains a Tryte String of a SHA256 hash of: The Statement "S", a random 9 charachter Salt String and the target address of the transaction. This Tryte Strign is always 128 Tryts long.

The second transaction is the reveal transaction. Its message field contains the same statement, salt and address but this time it is not hashed. 

To check the Proof Bob looks at the Reveal Transaction, from the message he gets the target address of the Commit, which he can use to find the Commit Transaction, he can now apply SHA256 to the message of the Reveal Transaction and comapre it to the message of the Commit transaction, if they are equal he can be sure that Alice already knew the Statement "S" and Salt at the time she made the Commit transaction.

## Why use IOTA
The Tangle gives the ability to store small amounts of data on an immutable ledger for free. This means that once the Commit transaction is attached there is no way for Alice to change its content at a later stage, making the commit binding.
Even though other DLTs can do the same, the ability to make the commits for free makes IOTA the best choiche for this.

## What to do with Commit-Reveal?
Commit-Reveal is a primitive used in more complex Schemes such as Zero-Knowledge Proofs, whitch makes it verry usefull aready.
It can also be used for any application which requires a user to commit to a statement without revealing it. For example if Alice and Bob want to make a bet on the dollar price of IOTA on a given date, but Alice does not want Bob to get influenced by her bet, she migth commit the her price with Commit-Reveal and reveal it only after the bet expired. Bob can not know what price Alice bid on until she reveals it, but Bob can verify that the reveled price is acctualy the one she initialiy commited.
