from CommitReveal import CommitRevealCheck
import random
import time

comm = CommitRevealCheck(
    "https://potato.iotasalad.org:14265",
    "HGW9HB9LJPYUGVHNGCPLFKKPNZAIIFHZAAHKSGMQKFMANUBA9SMSV9TAJSSMPRZZU9SFZULXKJ9YLAIUA",
    "CXDUYK9XGHC9DTSPDMKGGGOOOARSRVAFGHJOCDDH9ADLVBBOEHLICHTMGKVDOGRU9TBESJNHAXYPVJ999"
    )


while True:

    #get random number
    rnd = random.randint(5,60) 

    #wait some time between commits
    time.sleep(rnd)

    # sometimes make noise commit
    if rnd < 25:

        BundleCommit = comm.commitSignal("RandomNoise")

    # wait some time before reveal
    time.sleep(20)

    # make reveal
    BundleReveal = comm.RevealSignal()

    time.sleep(2)

    #Check if reveal and commit match
    comm.CheckReveal(BundleCommit, BundleReveal)