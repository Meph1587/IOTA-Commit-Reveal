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

    #global variables

    NodeURL = "" 

    Seed = ""

    TargetAddress = ""

    API = None

    ToReveal = ""



    #init class and IOTA API
    def __init__(self, _url, _seed, _targetAddress):

        self.NodeURL = _url
        self.Seed = _seed
        self.TargetAddress = _targetAddress

        self.API = Iota(_url)



    # function which generates the encrypted hash of the information to commit 
    def generateCommitHash(self, _statement, _salt):

        TrytesStatement = TryteString.from_string(_statement)

        StatementLen = len(TrytesStatement)

        # the format requires that the first 4 chars have the char length of the statement 
        if StatementLen <= 9:

            #if less than 9 than TryteString has only 2 chars, add 99 to get to 4
            SignalLenInTrytes = TryteString.from_bytes(bytes(StatementLen)) + "99"

        elif StatementLen <= 99 :

            #if between 9 and 99 TryteString has 4 chars
            SignalLenInTrytes = TryteString.from_bytes(bytes(StatementLen))

        #not more than 99 Trytes 
        else:
            raise ValueError('Statement String needs to be less than 99 Trytes!')

        #generate plain string 
        reveal = str(SignalLenInTrytes + "9" + TrytesStatement + "9" + _salt)

        #store for reveal
        self.ToReveal = reveal

        #encrypt/hash string
        commit = hashlib.sha256(reveal).hexdigest()

        #make into Trytes 
        commitInTryts = TryteString.from_bytes(commit)

        return commitInTryts



    def commitSignal(self, _signal):

        print "\nPreparing for new commit: "

        #generate random single-use salt
        salt = ''.join(random.choice(string.ascii_uppercase) for _ in range(9))

        #use salt to generate the Hash
        TrytesToCommit = self.generateCommitHash(_signal, salt)

        #make IOTA transaction to store commit on Tangle and get bundle
        revealBundle = str( self.Transact(TrytesToCommit, self.TargetAddress , "COMMIT") )

        return revealBundle



    def RevealSignal(self):

        print "Preparing reveal: "

        #get plain reveal string and store it on Tangle
        revealBundle = str(self.Transact(self.ToReveal, self.TargetAddress, "REVEAL"))

        print "Reveal Bundle: " + revealBundle

        return revealBundle



    def Transact(self, _message , _addr, _tag):

        # preparing transactions
        transfers = ProposedTransaction(address = Address(_addr), # 81 trytes long address
                              message = _message,
                              tag     = _tag, # Up to 27 trytes
                              value   = 0)
         # list of prepared transactions is needed at least
        bundle = ProposedBundle(transactions=[transfers])

        # generate bundle hash using sponge/absorb function + normalize bundle hash + copy bundle hash into each transaction / bundle is finalized
        bundle.finalize()

        # get tips to be approved by your bundle
        gta = self.API.get_transactions_to_approve(depth=3) 

        # bundle as trytes
        Trytes = bundle.as_tryte_strings()

        print "SENDING...."

        #attach Tip to Tangle
        tip = self.API.attach_to_tangle(trunk_transaction=gta['trunkTransaction'], # first tip selected
                           branch_transaction=gta['branchTransaction'], # second tip selected
                           trytes=Trytes, # our finalized bundle in Trytes
                           min_weight_magnitude=14) # MWMN

        #breadcast Tip to Network 
        res = self.API.broadcast_and_store(tip['trytes'])

        #return bundle hash
        return bundle.hash



    def CheckReveal(self, _bundleCommit, _bundleReveal):

        #get reveal transaction object from Tangle
        bundleHash = self.API.find_transactions(bundles=[_bundleReveal])
        lastTrytes = self.API.get_trytes(hashes = bundleHash["hashes"])
        transaction = Transaction.from_tryte_string(trytes = lastTrytes["trytes"][0])

        #get message from transaction
        message = transaction.signature_message_fragment

        #get the length of the statement from first 4 chars 
        statementLength = TryteString.decode(message[  : 4])

        #get statement from message
        signal = str(TryteString.decode(message[5 : 5 + int(statementLength)]))

        #get salt from message
        salt = str(message[6 + int(statementLength) : 6 + int(statementLength) + 9])

        #print results
        print "Revealed Data: "
        print "  Signal: " + signal
        print "  Salt: " + salt

        #use retrieved values to generate hash again
        ResultHash = self.generateCommitHash(signal, salt)

        print "Resulting Hash: " + str(ResultHash)

        #get commit transaction from Tangle
        commited = self.API.find_transactions(bundles = [_bundleCommit])
        commitedTrytes = self.API.get_trytes(hashes = commited["hashes"])
        commitedTransaction = Transaction.from_tryte_string(trytes = commitedTrytes["trytes"][0])

        #get commited message
        commitedMessage = str(commitedTransaction.signature_message_fragment[ :128])

        print "Commited Hash: " + str( commitedMessage )

        print "Commited on: " + str(datetime.fromtimestamp( commitedTransaction.timestamp))

        #check if commited message is equal message generated from revealed data 
        print "Is Equal to Commit: " + str( commitedMessage == ResultHash )



