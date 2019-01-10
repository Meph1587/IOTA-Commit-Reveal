from CommitReveal import CommitRevealCheck
import random
import time

comm = CommitRevealCheck(
    "https://potato.iotasalad.org:14265",
    "HGW9HB9LJPYUGVHNGCPLFKKPNZAIIFHZBDHKSGMQKFMANUBA9SMSV9TAJSSMPRZZU9SFZULXKJ9YLAIUA",
    "CXDUYK9XGHC9DTSPDMKGGGXTIARSRVAFGHJOCDDH9ADLVBBOEHLICHTMGKVDOGRU9TBESJNHAXYPVJ999"
    )

Buy = True

while True:

    #get random number
    rnd = random.randint(5,60) 

    #wait some time between commits
    time.sleep(rnd)

    # sometimes make noise commit
    if rnd < 25:

        BundleCommit = comm.commitSignal("RandomNoise")

    #commit a a buy or sell signal
    else:

        if Buy : 
            BundleCommit = comm.commitSignal("BUY AT PRICE: 3779.80988")
            Buy = False
        else:
            BundleCommit = comm.commitSignal("SELL AT PRICE: 153779.80988")
            Buy = True

    # wait some time before reveal
    time.sleep(20)

    # make reveal
    BundleReveal = comm.RevealSignal()

    time.sleep(2)

    #Check if reveal and commit match
    comm.CheckReveal(BundleCommit, BundleReveal)