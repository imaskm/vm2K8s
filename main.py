import os,shlex
import pexpect,subprocess



def set_permissions(vm_pem):
    cmd = "chmod 400 %s" % vm_pem
    return run_command(cmd)

def run_command(cmd):
    cmd=shlex.split(cmd)
    try:
        sp = subprocess.Popen(cmd,stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                            universal_newlines=True )
    except:
        print("ERROR: Failed to run the command")
        return False
    else:
        if(sp.returncode != 0 ):
            print("ERROR: Failed to run the command")
            return False
        else:
            return True 


def get_app_details_from_vm(vm_user,vm_ip,vm_pem):

    if(not set_permissions(vm_pem)):
        print("ERROR: Unable to set right permissions for key file")
        return
    app_details="/tmp/appdetails"
    host_app_dir="./appdata"

    if(not run_command("mkdir -p %s"%host_app_dir)):
        print("ERROR: Unable to create directory")
        return False

    cmd="ssh -o StrictHostKeyChecking=no -i %s %s@%s" %(vm_pem,vm_user,vm_ip)

    child=pexpect.spawn(cmd)

    try:
        child.expect(vm_user)
        cmd='export PROCESS_ID=`sudo netstat -plant | grep "LISTEN.*python3" | awk "{print $7}" | cut -d "/" -f1`'
        child.sendline(cmd)
        child.expect(vm_user)
        cmd='export PORT=`sudo netstat -plant | grep "LISTEN.*python3" | awk "{print $4}" | cut -d ":" -f2`'
        child.sendline(cmd)
        child.expect(vm_user)
        cmd='export APP_DIRECTORY=`sudo lsof | grep python3.*${PROCESS_ID}.*DIR | awk "NR==1{print $9}"`'
        child.sendline(cmd)
        child.expect(vm_user)
        cmd = "echo ${PORT} \n ${APP_DIRECTORY} > %s" %app_details
        child.sendline(cmd)
        child.expect(vm_user)
        child.sendline("logout")
    
    except pexpect.TIMEOUT:
        print("ERROR: Timed out ssh")
        return False
    except:
        print("ERROR: Failed to get app details from VM")
        return False
    
    try:
        cmd="scp -o StrictHostKeyChecking=no -i %s %s@%s:%s ." %(vm_pem,vm_user,vm_ip,app_details)
        
        if( not run_command(cmd) ):
            print("ERROR: Unable to get app details")
            return False

        fp=open(app_details)

        data=fp.readlines()

        APP_PORT=data[0]
        APP_PATH=data[1]

        fp.close()
        
        cmd="scp -r -o StrictHostKeyChecking=no -i %s %s@%s:%s %s"%(vm_pem,vm_user,vm_ip,APP_PATH,host_app_dir )
        print(APP_PATH,APP_PORT)
        return True
    except:
        print("ERROR: Failed to get data")
        return False
    
    

vm_user=input("Enter user ")
vm_ip=input("Enter VM's IP: ")
#need to have a function to check if IP is ssh-able
vm_pem=input("Enter private key file path ")


if( not os.path.exists(vm_pem) ):
    print("ERROR: Private Keyfile doesn't exist")
    exit()

if( not get_app_details_from_vm(vm_user,vm_ip,vm_pem)  ):
    print("Failed App")
else:
    print("Let's build Docker Image now")










