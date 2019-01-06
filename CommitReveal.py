from iota import Iota
from iota import Address, ProposedTransaction, Tag, Transaction
from iota import TryteString
from iota import ProposedBundle
from iota.commands.extended import utils
from datetime import datetime
from pprint import pprint
import hashlib 
import time
import random
import string


class CommitRevealCheck(object):

    NodeURL = "" 

    Seed = ""

    RevealAddress = ""

    Tag = ""

    API = None

    ToReveal = ""

    def __init__(self, _url, _seed, _targetAddress, _tag):

        self.NodeURL = _url
        self.Seed = _seed
        self.RevealAddress = _targetAddress
        self.Tag = _tag

        self.API = Iota(_url)


    def commitSignal(self, _signal):

        print "Preparing for commit: "

        salt = ''.join(random.choice(string.ascii_uppercase) for _ in range(9))

        commitAddress = ''.join(random.choice(string.ascii_uppercase) for _ in range(81))

        reveal = _signal + "9" + salt + "9" + commitAddress

        self.ToReveal = reveal


        commit = hashlib.sha256(reveal).hexdigest()

        commitInTryts = TryteString.from_bytes(commit)

        self.Transact(commitInTryts, commitAddress,None)


    def RevealSignal(self):

        print "Preparing reveal: "

        revealBundle = str(self.Transact(self.ToReveal, self.RevealAddress, self.Tag))

        print "Reveal Bundle: " + revealBundle

        return revealBundle


    def Transact(self, _message , _addr, _tag):
        # preparing transactions
        transfers = ProposedTransaction(address = Address(_addr), # 81 trytes long address
                              message = _message,
                              tag     = _tag, # Up to 27 trytes
                              value   = 0)

        bundle = ProposedBundle(transactions=[transfers]) # list of prepared transactions is needed at least


        # generate bundle hash using sponge/absorb function + normalize bundle hash + copy bundle hash into each transaction / bundle is finalized
        bundle.finalize()

        gta = self.API.get_transactions_to_approve(depth=3) # get tips to be approved by your bundle

        Trytes = bundle.as_tryte_strings() # bundle as trytes

        print "SENDING...."

        tip = self.API.attach_to_tangle(trunk_transaction=gta['trunkTransaction'], # first tip selected
                           branch_transaction=gta['branchTransaction'], # second tip selected
                           trytes=Trytes, # our finalized bundle in Trytes
                           min_weight_magnitude=14) # MWMN


        res = self.API.broadcast_and_store(tip['trytes'])

        return bundle.hash


    def GetLastTXFromAddress(self, _address):

        allTransactions = self.API.find_transactions(addresses = [_address])

        lastTrytes = self.API.get_trytes(hashes = allTransactions["hashes"])

        newestTx = None

        newestTxTsmp = 0

        for transaction in lastTrytes["trytes"]:

            tx = Transaction.from_tryte_string(trytes = transaction)

            if tx.timestamp > newestTxTsmp:
                newestTx = tx
                newestTxTsmp = tx.timestamp


        return newestTx



    def CheckReveal(self, _bundle):

        if _bundle == None:
            transaction = self.GetLastTXFromAddress(self.RevealAddress)
        else :
            bundleHash = self.API.find_transactions(bundles=[_bundle])
            lastTrytes = self.API.get_trytes(hashes = bundleHash["hashes"])
            transaction = Transaction.from_tryte_string(trytes = lastTrytes["trytes"][0])

        message = str(transaction.signature_message_fragment)

        signal = ""

        signalStop = 0

        for i,c in enumerate(message):

            if c != "9":
                signal = signal + c
            else:
                signalStop = i 
                break;

        salt = message[signalStop + 1 : signalStop + 10]

        address = message[signalStop + 11 : signalStop + 92]

        print "Revealed Data: "
        print "  Signal: " + signal
        print "  Salt: " + salt
        print "  Address: " + address

        reveal = signal + "9" + salt + "9" + address

        Result = TryteString.from_bytes( hashlib.sha256(reveal).hexdigest() ) 

        print "Resulting Hash: " + str(Result)

        commited = self.API.find_transactions(addresses = [address])
        commitedTrytes = self.API.get_trytes(hashes = commited["hashes"])
        commitedTransaction = Transaction.from_tryte_string(trytes = commitedTrytes["trytes"][0])
        commitedMessage = str(commitedTransaction.signature_message_fragment[ :128])

        print "Commited Hash: " + str( commitedMessage )

        print "Commited on: " + str(datetime.fromtimestamp( commitedTransaction.timestamp))

        print "Is Equal: " + str( commitedMessage == Result )









comm = CommitRevealCheck("https://potato.iotasalad.org:14265",
                        "HGW9HB9LJPYUGVHNGCPLFKKPNZAIIFHZBDHKSGMQKFMANUBA9SMSV9TAJSSMPRZZU9SFZULXKJ9YLAIUA",
                         "CXDUYK9XGHC9DTSPDMKGGGXTIARSRVAFGHJOCDDH9ADLVBBOEHLICHTMGKVDOGRU9TBESJNHAXYPVJ999",
                          "COMMIT9REVEAL9")

comm.commitSignal("SOMEMESSAGE")

time.sleep(20)

bd = comm.RevealSignal()

time.sleep(2)

comm.CheckReveal(bd)
