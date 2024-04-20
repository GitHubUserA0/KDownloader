import sys
import paramiko
import requests
import json

from paramiko.client import MissingHostKeyPolicy

user_inputs_keys = ['host','port','user','key\'s password','user\'s password','key_path','debrid_service','api_key','connection_mode']
user_inputs = dict.fromkeys(user_inputs_keys)
welcome_message = 'Welcome to KDownloader, please login'
default_download_path = input("Welcome to KDownloader, please, type the default path where you want your files to be downloaded : ")
def connection_user_input():
    user_inputs['host'] = input('host : ')
    user_inputs['port'] = input('port : ')
    user_inputs['user'] = input('user : ')
    connection_mode_is_valid = False
    while not connection_mode_is_valid:
     connection_mode = input('Please choose a connection mode to the server :\n 1 - type \'1\' to connect with a password\n 2 - type \'2\' to connect with a SSH key\nmode : ')
     if connection_mode=='1':
        connection_mode_is_valid = True
        user_inputs['connection_mode']='password_mode'
     if connection_mode=='2':
        connection_mode_is_valid = True
        user_inputs['connection_mode'] = 'SSH_key_mode'
     if user_inputs['connection_mode']=='SSH_key_mode':
        key_password = user_inputs['key\'s password'] = input('your private key\'s password : ')
        key_path = user_inputs['key_path'] = input('path to your private key : ')
        key = paramiko.RSAKey.from_private_key_file(key_path,key_password)
     else:
        user_password = user_inputs['user\'s password'] = input('type your password : ')
    valid_debrid_choice = False
    while not valid_debrid_choice:
        print('0 - type \'0\' if you don\'t have Alldebrid nor Realdebrid')
        print('1 - type \'1\' to select Alldebrid as debrid service')
        print('2 - type \'2\' to select Realdebrid as debrid service')
        debrid_choice = input("Please, choose an option : ")
        if debrid_choice=='1':
            user_inputs['debrid_service']="Alldebrid"
            user_inputs['api_key']=input("Please, type your API key or token : ")
            valid_debrid_choice = True
        elif debrid_choice=='2':
            user_inputs['debrid_service']="Realdebrid"
            user_inputs['api_key'] = input("Please, type your API key or token : ")
            valid_debrid_choice = True
        elif debrid_choice=='0':
            valid_debrid_choice = True
        if debrid_choice!='0' and debrid_choice !='1' and debrid_choice!='2':
            print("Please, select a valid option")
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(MissingHostKeyPolicy)
    try:
        if user_inputs['connection_mode']=='SSH_key_mode':
         ssh_client.connect(hostname=str(user_inputs['host']), port=user_inputs['port'], username=str(user_inputs['user']),pkey=key)
        else:
            ssh_client.connect(hostname=str(user_inputs['host']), port=user_inputs['port'],username=str(user_inputs['user']), password=user_password, look_for_keys=False, allow_agent=False)
    except Exception:
        print('Authentication failed, please try again')
        connection_user_input()
    ssh_client.close()

def logout():
    for key in user_inputs:
        user_inputs[key] = None

def ssh_shell():
    host = user_inputs['host']
    port = user_inputs['port']
    user = user_inputs['user']
    ssh_key_password = user_inputs['key\'s password']
    key_path = user_inputs['key_path']
    user_password= user_inputs['user\'s password']
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(MissingHostKeyPolicy)
    if user_inputs['connection_mode']=='SSH_key_mode':
        key = paramiko.RSAKey.from_private_key_file(key_path, ssh_key_password)
        ssh_client.connect(hostname=str(host),port=port,username=str(user),pkey= key)
    else:
        ssh_client.connect(hostname=str(host),port=port,username=str(user),password= user_password, look_for_keys=False, allow_agent=False)
    channel = ssh_client.get_transport().open_session()
    channel.get_pty()
    channel.invoke_shell()
    # channel.send("stty -echo\n")
    is_remotely_connected_by_ssh = True
    global is_first_command
    is_first_command = True
    global command_to_execute
    command_to_execute = ''
    global output_end
    output_end = ""
    global counter
    counter = 0
    global output
    while is_remotely_connected_by_ssh:
        command = input(user_inputs['user'] + ':~$ ')
        if command == 'exit':
            is_remotely_connected_by_ssh = False
            is_first_command = True
            ssh_client.close()
            main_menu()
        if command=='logout':
            logout()
            ssh_client.close()
            main_menu()
        if command=='close':
            ssh_client.close()
            print('Goodbye ! Hope you enjoyed KDownloader ! ')
            exit()
        channel.send(command + "\n")
        if is_first_command :
            output = channel.recv(99999)
            sys.stdout.write(output.decode())
            output = channel.recv(99999)
        else:
            output = channel.recv(99999)
            sys.stdout.write(output.decode())
        while not str(output).endswith("\\r\\n$ \'"):
            if str(output).endswith("\\r\\r\\n$ \'") or str(output).endswith("b\'$ \'" ):
                break
            else:
                output = channel.recv(99999)
                sys.stdout.write(output.decode())
        is_first_command = False
def main_menu():

    if user_inputs['user']==None:
     print('You are currently in the main menu, please login')
     print('0 - type \'0\' to login')
    else:
     print('You are currently in the main menu, logged as ' + user_inputs['user'])
    print('1 - type \'1\' to open the shell')
    print('2 - type \'2\' to download a file from a locked link that needs to be unlocked')
    print('3 - type \'3\' to download a file from an unlocked link or a link that does not need to be unlocked')
    print('4 - type \'4\' to change your debrid service')
    print('5 - type \'5\' to change your api key or token')
    print('6 - type \'6\' to logout')
    print('7 - type \'7\' to exit KDownloader')
    user_choice = input('Please, choose an option : ')
    if ((user_choice=='1' or user_choice=='2' or user_choice=='3') and user_inputs['user']==None) or user_choice=='0':
        connection_user_input()
        if user_choice =='0':
            main_menu()
        if user_choice == '1':
            ssh_shell()
        if user_choice == '2':
            unlocked_download()
        if user_choice == '3':
            download()
    else:
     if user_choice=='1':
        ssh_shell()
     if user_choice=='2':
        unlocked_download()
     if user_choice=='3':
        download()
     if user_choice=='4':
         valid_debrid_choice = False
         while not valid_debrid_choice:
             print('0 - type \'0\' if you don\'t have Alldebrid nor Realdebrid')
             print('1 - type \'1\' to select Alldebrid as debrid service')
             print('2 - type \'2\' to select Realdebrid as debrid service')
             debrid_choice = input("Please, choose an option : ")
             if debrid_choice == '1':
                 user_inputs['debrid_service'] = "Alldebrid"
                 user_inputs['api_key'] = input("Please, type your API key or token : ")
                 valid_debrid_choice = True
             elif debrid_choice == '2':
                 user_inputs['debrid_service'] = "Realdebrid"
                 user_inputs['api_key'] = input("Please, type your API key or token : ")
                 valid_debrid_choice = True
             elif debrid_choice == '0':
                 valid_debrid_choice = True
             elif debrid_choice != '0' and debrid_choice != '1' and debrid_choice != '2':
                 print("Please, select a valid option")
         if debrid_choice=='1' or debrid_choice=='2':
            print("As your debrid service changed, please don\'t forget to change your API key or token")
            user_inputs['api_key']= input("Please, type your new API key or token : ")
         else:
             print("As you don\'t have a debrid service anymore, your former API key or token has been removed from KDownloader")
             user_inputs['api_key'] = None
         main_menu()
     if user_choice=='5':
        new_API_key = input(' Please, type your token or api key for your debrid service (type \'none\' if you don\'t have one) : ')
        if new_API_key.lower()=="none":
            user_inputs['api_key'] = None
        else:
            user_inputs['api_key'] = new_API_key
        main_menu()
     if user_choice=='6':
        logout()
        main_menu()
     if user_choice=='7':
        print('Goodbye ! Hope you enjoyed KDownloader ! ')
        exit()
     else :
        print('Please, select a valid choice')
        main_menu()
def unlock_DDL_link_alldebrid(link):
    unlocked_link_details = {}
    url = "https://api.alldebrid.com/v4/link/unlock?agent=KDownloader&apikey="+user_inputs['api_key']+"&link="+link
    data= requests.get(url).json()
    unlocked_link_details['link'] = json.loads(json.dumps(data, indent=2))['data']['link']
    unlocked_link_details['filename'] = json.loads(json.dumps(data, indent=2))['data']['filename']
    unlocked_link_details['host'] = json.loads(json.dumps(data, indent=2))['data']['host']
    return unlocked_link_details
def unlocked_download():
    host = user_inputs['host']
    port = user_inputs['port']
    user = user_inputs['user']
    ssh_key_password = user_inputs['key\'s password']
    key_path = user_inputs['key_path']
    user_password = user_inputs['user\'s password']
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(MissingHostKeyPolicy)
    if user_inputs['connection_mode'] == 'SSH_key_mode':
        key = paramiko.RSAKey.from_private_key_file(key_path, ssh_key_password)
        ssh_client.connect(hostname=str(host), port=port, username=str(user), pkey=key)
    else:
        ssh_client.connect(hostname=str(host), port=port, username=str(user), password=user_password,look_for_keys=False, allow_agent=False)
    if user_inputs['debrid_service']==None:
        user_inputs['debrid_service'] = input('your debrid service (type \'none\' if you don\'t have one) : ')
    if user_inputs['api_key']==None:
        user_inputs['api_key'] = input('your token or api key for your debrid service : ')
    if user_inputs['api_key']=='none' or user_inputs['debrid_service']=='none':
        print('In order to unlock links, you need to have a debrid_service. You will be redirected to the main menu.')
        ssh_client.close()
        main_menu()
    else:
        link = input('link : ')
        default_filename = unlock_DDL_link_alldebrid(link).get('filename')
        filename=default_filename
        user_filename = input('type the name you want the file to have or let this field empty to name it by default : ')
        channel = ssh_client.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()
        if len(user_filename)!=0:
            filename= user_filename
        download_path = default_download_path
        user_download_path = input('type the path you want the file to be downloaded or let this field empty to download the file in the folder \'../../Downloads\' by default : ')
        if len(user_download_path)!=0:
          download_path=user_download_path
        command = 'cd ' + download_path + '; curl ' +unlock_DDL_link_alldebrid(link).get('link')+ ' >' + filename
        channel.send(command + "\n")
        output = channel.recv(99999)
        sys.stdout.write(output.decode())
        output = channel.recv(99999)
        while not str(output).endswith("\\r\\n$ \'"):
            if str(output).endswith("\\r\\r\\n$ \'") or str(output).endswith("b\'$ \'"):
                break
            else:
                output = channel.recv(99999)
                sys.stdout.write(output.decode())
        # output = stdout.read().decode()
        ssh_client.close()
        print("File successfully downloaded ! ")
        print(output)
def download():
 host = user_inputs['host']
 port = user_inputs['port']
 user = user_inputs['user']
 ssh_key_password = user_inputs['key\'s password']
 key_path = user_inputs['key_path']
 user_password= user_inputs['user\'s password']
 link = input('link : ')
 ssh_client = paramiko.SSHClient()
 ssh_client.load_system_host_keys()
 ssh_client.set_missing_host_key_policy(MissingHostKeyPolicy)
 if user_inputs['connection_mode']=='SSH_key_mode':
     key = paramiko.RSAKey.from_private_key_file(key_path, ssh_key_password)
     ssh_client.connect(hostname=str(host),port=port,username=str(user),pkey= key)
 else:
     ssh_client.connect(hostname=str(host),port=port,username=str(user),password=user_password, look_for_keys=False, allow_agent=False)
 channel = ssh_client.get_transport().open_session()
 channel.get_pty()
 channel.invoke_shell()
 user_filename = input('type the name you want the file to have or let this field empty to name it by default : ')
 while len(user_filename)==0:
      user_filename = input('please type a name for the file : ')
 filename = user_filename
 download_path = default_download_path
 user_download_path = input('type the path you want the file to be downloaded or let this field empty to download the file in the folder \'../../Downloads\' by default : ')
 if len(user_download_path)!=0:
      download_path=user_download_path
 command = 'cd ' + download_path +'; curl '+link+' >'+filename
 channel.send(command + "\n")
 output = channel.recv(99999)
 sys.stdout.write(output.decode())
 output = channel.recv(99999)
 while not str(output).endswith("\\r\\n$ \'"):
     if str(output).endswith("\\r\\r\\n$ \'") or str(output).endswith("b\'$ \'"):
        break
     else:
        output = channel.recv(99999)
        sys.stdout.write(output.decode())
 ssh_client.close()
 print("File successfully downloaded ! ")

# print (welcome_message)
main_menu()