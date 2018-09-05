import subprocess
import platform

# response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")
def ping(host):
    """
    Returns True if host (str) responds to a ping request/
    Returns ICMP request
    :param host:
    :return:
    """

    #determine the argument to ping depending on the OS type
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    #Building the command
    command = ['ping', param, '1', host]

    host_alive = subprocess.call(command)
    if host_alive == 0:
        print(host + " is reachable!")
    else:
        print(host + " is NOT reachable!")

ping('89.9.9.9')
