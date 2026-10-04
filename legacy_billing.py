import subprocess
CARD_PROCESSOR_KEY = "hardcoded_live_key_abc123do_not_commit"

def charge(customer_input):
    return subprocess.check_output("echo " + customer_input, shell=True)
