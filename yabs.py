#!/usr/bin/python2.7

# likely need pip install futures

import sys
import requests
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from time import gmtime, strftime
import concurrent
from concurrent.futures import ThreadPoolExecutor, wait, as_completed


# start_time = time.time()
#  time.time() - start_time,

def main():
    """ Main entry to get the options yo and kick things off"""
    parser = ArgumentParser()
    parser.add_argument("-w", "--scanlist", dest="scanlist", help="Text file containing domain safe list to scan",
                        metavar="scanlist")
    parser.add_argument("-o", "--outputfile", dest="outputfile", help="Output file defaults to scanout.txt",
                        metavar="outputfile")
    parser.add_argument("-s", "--silent", dest="silent", help="Silent mode only prints public buckets to the console",
                        action="store_true")
    parser.add_argument("-p", "--perftest", dest="perftest", help="takes the first 50 entries in the wordlist and "
                                                                  "calculates the anticipated time for completion "
                                                                  "then extrapolates this to provide estimate for "
                                                                  "processing entire list", action="store_true")
    parser.add_argument("-c", "--concurrentthreads", dest="concurrentthreads", help="specific the number of concurrent "
                                                                                    "threads, use with caution",
                        metavar="concurrentthreads")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    if args.silent:
        silent = 1

    if args.outputfile:
        outputfile = args.outputfile
    else:
        outputfile = "scanout.txt"

    with open(args.scanlist, 'r') as f:
        currentRate = 0
        currentvol = 0
        tempnum = 0
        bucket_names = f.readlines()
        bucket_names = [x.strip() for x in bucket_names]
        scanvol = len(bucket_names)
        # print '{:20,.2f}'.format(scanvol)
        message = "ScanStart," + strftime("%a, %d %b %Y %H:%M:%S", gmtime())
        logger(outputfile,message)

    if args.perftest:
        perftest = 1

    for bucket in bucket_names:
        executor = concurrent.futures.ProcessPoolExecutor(int(args.concurrentthreads))
        futures = [executor.submit(s3_scan, silent, bucket, perftest, outputfile)]
        concurrent.futures.wait(futures)


def parseresponse(reply, target, outputfile, bucket):
    try:
        root = ET.fromstring(reply)

        if root.tag == "Error":
            status = root[0].text
            message = bucket + ',' + status
            logger(outputfile, message)

        elif "ListBucketResult" in root.tag:
            message = bucket + ',Public'
            logger(outputfile, message)
    except:
        message = bucket + ',Error'
        logger(outputfile, message)
        pass


def logger(outputfile, message):
    outFile = open(outputfile, 'a')
    outFile.write(message + "\n")
    outFile.close


def s3_scan(silent, bucket, perftest, outputfile):
    target = "https://" + bucket + ".s3.amazonaws.com"
    try:
        _ = requests.head(target)
        if _.status_code != 404:
            _ = requests.get(target)
            parseresponse(_.text, target, outputfile, bucket)
        else:
            message = bucket + ",Not Found"
            logger(outputfile,message)
    except requests.exceptions.RequestException as _:
        message = bucket + ',' + _
        logger(outputfile, message)
    target = "https://s3.amazonaws.com/" + bucket
    try:
        _ = requests.head(target)
        if _.status_code != 404:
            _ = requests.get(target)
            parseresponse(_.text, target, outputfile, bucket)
        else:
            message = bucket + ",Not Found"
            logger(outputfile, message)
    except requests.exceptions.RequestException as _:
        message = bucket + ',' + _
        logger(outputfile, message)


if __name__ == "__main__":
    print(r"""

                                `..--:::::::::::::-....`
                `-/+oyhdmNNMNNNmmmmmddddddmmmmmNNNMMMMNNNmdhyyso/:-`
          ./oydNMNmdhysso+++oosssyyyhhhhhhhhhhhhhhhdhhhdddmmmmNNMMMMNmhs+-`
     ./sdNMmdhso+osyhddmNNMNNNmmmddmmddhhdddddhhddmmdmmmmNNMMMMMMMMMMMMMMMMmy/.
   +mMNdysoshdmmmmddhhhyysyssssssssssssssssssssssssssssssssssyyhhhdmmNMMMMNdmNMd+.
  .NMMms+hNMMNdddhhhhyyysyssssssssssssssssssssssssssssssyyyysssyyyhhhdmNMMd+++omMN-
   :NMMMNyooydNNMMMMMMMMMMNNNNmNmdmmmddddddhhhhhhhddddddmmdNmNNMMMMMMNNmmo++++ohMM+
    `sMMMMMNdyso+++ooossssyyyyhhhhhhdddddddddddddddddhhhhhyyysssoo+++++++oshdNMMNo
      :MMMMMMMMMMNmmdhhyyyssoo++/++++++++++++++++++++++++++++++++ossyhdmNMMMMms:
       +MhosydmNMMMMMMMMMMMMMMMMNmmhdddhhyhyhhhyhhyhyhhdhdmmmNNMMMNNmdhhysNM-
        hN:-+ydmmNmdsooyyyhddmmmmmmmmNNmmmmmmmmdhhhhyyysso+++//:---------/Md
        /MhdMMMMNhmMMo---------------------------------------------------dM/
        `NMMMMMMMNssMM+-------------------------------------------------+MN`             YABS - Yet Another Bucket Scanner  V0.1
         hMMMMy+dMN+dMN:------------------------------------------------mMs
         /MMMMhmMMN+hMMs-----------------------------------------------+MM-
         `mMMMMMMMsoNMMs-----------------------------------------------mMd                    Multi-threaded S3 Bucket finder
         .dMsdMMMNdMMMm:----------------------------------------------+MM/
        .mMy+NMMMMMMmy:-----------------------------------------------dMN`
       `mMd+dMMhso/:-------------------------------------------------/MMs
       hMN+yMMM:-----------------------------------------------------dMM-
      /MMosMMMm-----------------------------------------------------/MMd
     `mMyoMMMMm-----------------------------------------------------hMM/
     +MdoNMNdMN----------------------------------------------------:NMN`
    `NN+NMM++MM:---------------------------------------------------yMMs
    yMydMMd :MMs--------------------------------------------------:NMM.
   +MmsMMM. `MMm--------------------------------------------------yMMd
   NMyNMMy   mMM+-------------------------------------:syyo------:NMM/
  -MNsMMM-   sMMm------------------------------------sMMMMMs-----yMMN`
  oMddMMN`   :MMMo----------------------------------yMMmNNMds/--/MMMs
  dMyhMMd     dMMN---------------------------------:MMMhyyhdNMNydMMM-
 `MMsoMMm     /MMMy--------------------------------:NMMNmddhydNMMMMd
 `MMs+dMM`     yMMM/--------------------------------:ymMMMMMMmhhNMM/
 `NMy++hMh:-:sdNMMMd------------------------------------/ohNMMNhhdNd-
  sMMy++smMMMMMMMMMM/---------------------------------------sMMNhhymN/
   oNMMmdhdNMMMMMMMMd----------------------------------------dMMmhyhMN-
    .+hNMMMMMMNdhsNMM/---------------------------------------hMMMhhyNMd
        `.--``    :NMMNdys+/:-------------------------------sMMMMdhydMM-                     `-::.
                   :NMMMMMMMMMNmddhyysssooooo++++++++ooooydMMMsoMNhhdMMy      `.-.`       .odNNNNMo
                    -ohmMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNo `MdyhyNMN:/oydNMNNMMmo    :NNhyydmMs
                        `.:+osyhdmmmNMMMMMmmmmmmmmmmNmmmdyo:` .hMdyhhhdNMMMmy+/::+yMN   `NMMMMMMMd.
                                       `.               `-/oymMMMdyhyyhhyNMMMNmNMMMm:    .......`
                                             ./o+/-`  `oNMNNmmddhyhyhhyhhNMMNdhsss/`
                                           /dNmmMMMo `dMmhhyhhdddhhhhyyhhhhhddmdmmNNh/
                                          oMNhdNMh-  .MMNNMMMMMMMNyhhyhhhhyyyhhhhhhymMm.
                                          smNmho.     ./+o+/:--mNhyhyhdhhyhhmNMMMMNmmMM-
                                                             `mNyyhymMMNmdhyhNMMMddddh:
                                                             :MMmdmms+sdMMMNNNMMd`
                                                              .oyhs`    `:+sso+:`

    """)

    main()
