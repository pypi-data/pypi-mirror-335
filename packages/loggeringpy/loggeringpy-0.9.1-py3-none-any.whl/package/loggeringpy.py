import datetime
import colorama
import os
import json


from datetime import datetime
from colorama import init
from dacite import from_dict
from dataclasses import dataclass
from colorama import Fore, Back, Style

init()


time = datetime.now().strftime('%m-%d %H:%M')

    
@dataclass
class Information:
    logLocation: str
    type: str
    name: str
    writeLogs: bool


@dataclass
class infor:
    Information: Information




def create_file(name = any,location = any,type = ".log" or ".txt", writing = True or False):
    """
    creating new log file in folder
    
    """
    if type.find(".") == -1:
        prop = location + "/" + name + "." + type
    else:
        prop = location + "/" + name + type
    
    if writing == True:
        if os.path.exists(prop):
            create_json(name,type,location,writing)
            return
        else:
            print(Style.BRIGHT + Fore.GREEN + f"[SUCCESS] -> | {time} | Created new log file!" + Style.RESET_ALL)
        
        file = open(prop, 'a')
        file.write(f"[INFO] -> | {time} | Start logging now!\n")
        create_json(name,type,location,writing)
    else:
        return
        
    
def create_json(name, type, location, writing):
    data = {'Information': {
        'logLocation': location,
        'type': type,
        'name': name,
        "writeLogs": writing
    }}
        

    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    print(my_filename)
    with open(my_filename + "\configuration" + ".json", 'w+') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    
        

class color():
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    UNDER = "\033[4m"


def info(text = any):  
    '''
    printing your text in class [ INFO ]
    and writing to log file (option)
    
    '''
    print(Style.BRIGHT + f"[ INFO ]  -> | {time} | {text}" + Style.RESET_ALL)
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    with open(my_filename + "\configuration" + ".json", 'r') as outfile:
        data = from_dict(infor, json.loads(outfile.read()))
        loglocation = data.Information.logLocation
        name = data.Information.name
        type = data.Information.type
        write = data.Information.writeLogs
        if write == True:
            if type.find(".") == -1:
                prop = loglocation + "/" + name + "." + type
            else:
                prop = loglocation + "/" + name + type
            file = open(prop, 'a')
            file.write(f"[ INFO ]  -> | {time} | {text}\n")
        else:
            return
        
def warning(text = any):  
    '''
    printing your text in class [ WARN ]
    and writing to log file (option)
    
    '''
    print(Style.BRIGHT + Fore.YELLOW +  f"[ WARN ]  -> | {time} | {text}" + Style.RESET_ALL)
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    with open(my_filename + "\configuration" + ".json", 'r') as outfile:
        data = from_dict(infor, json.loads(outfile.read()))
        loglocation = data.Information.logLocation
        name = data.Information.name
        type = data.Information.type
        write = data.Information.writeLogs
        if write == True:
            if type.find(".") == -1:
                prop = loglocation + "/" + name + "." + type
            else:
                prop = loglocation + "/" + name + type
            file = open(prop, 'a')
            file.write(f"[ WARN ]  -> | {time} | {text}\n")
        else:
            return
        
def success(text = any):  
    '''
    printing your text in class [ SUCCESS ]
    and writing to log file (option)
    
    '''
    print(Style.BRIGHT + Fore.GREEN +  f"[SUCCESS] -> | {time} | {text}" + Style.RESET_ALL)
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    with open(my_filename + "\configuration" + ".json", 'r') as outfile:
        data = from_dict(infor, json.loads(outfile.read()))
        loglocation = data.Information.logLocation
        name = data.Information.name
        type = data.Information.type
        write = data.Information.writeLogs
        if write == True:
            if type.find(".") == -1:
                prop = loglocation + "/" + name + "." + type
            else:
                prop = loglocation + "/" + name + type
            file = open(prop, 'a')
            file.write(f"[SUCCESS] -> | {time} | {text}\n")
        else:
            return

def critical(text = any):  
    '''
    printing your text in class [ CRIT ]
    and writing to log file (option)
    
    '''
    print(Style.BRIGHT+ Fore.RED + color.UNDERLINE +  f"[ CRIT ]  -> | {time} | {text}" + Style.RESET_ALL + color.END)
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    with open(my_filename + "\configuration" + ".json", 'r') as outfile:
        data = from_dict(infor, json.loads(outfile.read()))
        loglocation = data.Information.logLocation
        name = data.Information.name
        type = data.Information.type
        write = data.Information.writeLogs
        if write == True:
            if type.find(".") == -1:
                prop = loglocation + "/" + name + "." + type
            else:
                prop = loglocation + "/" + name + type
            file = open(prop, 'a')
            file.write(f"[ CRIT ]  -> | {time} | {text}\n")
        else:
            return


def debug(text = any):  
    '''
    printing your text in class [ DEBUG ]
    and writing to log file (option)
    
    '''
    print(Style.NORMAL + Fore.YELLOW +  f"[ DEBUG ] -> | {time} | {text}" + Style.RESET_ALL )
    path_to_script = os.path.dirname(os.path.abspath(__file__))
    my_filename = os.path.join(path_to_script)
    with open(my_filename + "\configuration" + ".json", 'r') as outfile:
        data = from_dict(infor, json.loads(outfile.read()))
        loglocation = data.Information.logLocation
        name = data.Information.name
        type = data.Information.type
        write = data.Information.writeLogs
        if write == True:
            if type.find(".") == -1:
                prop = loglocation + "/" + name + "." + type
            else:
                prop = loglocation + "/" + name + type
            file = open(prop, 'a')
            file.write(f"[ DEBUG ] -> | {time} | {text}\n")
        else:
            return



