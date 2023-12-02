import requests
import os, sys, json, re
from modules.functions import *
from print_color import print
import pandas as pd

#Initialize server
login = os.getlogin()
os.system('start cmd /k C:\\Users\\'+login+'\\Desktop\\textgen_server.bat')
#Connection info
url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
#LLM Selection + History init
print(os.listdir('./history'))
llm_name = input("Select LLM:> ")
if llm_name == 'exit':
        sys.exit(0)
history = []
#Load existing history
try:
    history_df = pd.read_csv('.\history\history_' + llm_name + '.csv')
    history_dict = history_df.to_dict(orient='records')
    history = history + history_dict
    for key in history:
        print(history[key], tag=key, tag_color='magenta', color='cyan')
except:
    pass

def history_update(list_name):
    df = pd.DataFrame(list_name, columns=['role','content'])
    df.to_csv('.\history\history_' + llm_name + '.csv', index=False)

#Chat
while True:
    role_select = input("Select role - system/user :> ")
    if role_select == 'system':
        system_message = input('System:> ')
        history.append({"role": "system", "content": system_message})
    
    user_message = input("Raddka:> ")
    if user_message == 'exit':
        sys.exit(0)
    history.append({"role": "user", "content": user_message})

    data = {"mode": "instruct", "messages": history}
    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    
    history.append({"role": "assistant", "content": assistant_message})
    history_update(history)
    print(assistant_message, tag=llm_name, tag_color='magenta', color='cyan')
        
    if '/function' in assistant_message:
        matches = re.findall(r'\[([^]]+)\]', assistant_message)
        extracted_info = {}    
        function_name = matches[0]
        try:
            args_str = matches[1]
            if function_name in globals() and callable(globals()[function_name]):
                func_to_call = globals()[function_name]  
                args = [arg.strip() for arg in args_str.split(',')]
                response = func_to_call(*args)
            else:
                response = 'Function not found'
        except:
            if function_name in globals() and callable(globals()[function_name]):
                func_to_call = globals()[function_name]
                response = func_to_call()
            else:
                response = 'Function not found'        
        
        history.append({"role": "notification", "content": response})
        data = {"mode": "instruct","messages": history}
        response = requests.post(url, headers=headers, json=data, verify=False)
        print(assistant_message, tag='Notification', tag_color='yellow', color='white')
        assistant_message = response.json()['choices'][0]['message']['content']
        history.append({"role": "assistant", "content": assistant_message})
        history_update(history)  
        print(assistant_message, tag=llm_name, tag_color='magenta', color='cyan')