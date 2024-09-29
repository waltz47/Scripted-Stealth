import os
import json
import time
from prompts import *
import ollama
import argparse
import sys

agent_comm = "agentcomm" #contains agent chat str
main_comm = "maincomm" #system str

his_dict = {
    "main":  [{'role':'system', 'content':main_prompt.format("")}],
    "agent":  [{'role':'system', 'content':agent_prompt.format("")}]
}

def his_to_str(role, history):
    if role == 'main':
        role = 'dungeon master: '
    else:
        role = 'agent: '

    conv_str = ''

    for chat in history:
        if chat['role'] == 'system':
            continue
        if chat['role'] == 'user':
            conv_str += 'user: ' + chat['content'] + "\n"
        if chat['role'] == 'assistant':
            conv_str += role + chat['content'] + "\n"

    return conv_str

def read_str_from_file(file):
    try:
        f = open(file,'r')
        return f.read()
    except:
        return ''
    return ''


def write_to_file(data, comm_file):
    with open(comm_file, 'w') as f:
        json.dump(data, f)

def read_from_file(comm_file):
    if os.path.exists(comm_file):
        with open(comm_file, 'r') as f:
            return json.load(f)
    return None

def llm_process(model_name, history):

    response = ollama.chat(model=model_name, 
                           options={"temperature":0.4, "top_p":0.95,"num_ctx":12000},
                           messages=history, stream=True)
    
    assistant_response = ''
    for chunk in response:
        print(chunk['message']['content'], end='', flush=True)
        assistant_response += chunk['message']['content']
    
    history.append({'role':'assistant','content':assistant_response})
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run as either main LLM or agent.")
    parser.add_argument('--role', choices=['main', 'agent'], required=True, help="Choose the role: 'main' or 'agent'")
    args = parser.parse_args()

    if args.role == 'main':
        os.remove(main_comm) if os.path.exists(main_comm) else None
        os.remove(agent_comm) if os.path.exists(agent_comm) else None

        #main game environment sim: heist and the timeline changes are here-
        history = his_dict[args.role]
        while True:

            for chat in history:
                if chat['role'] == 'system':
                    chat['content'] = main_prompt.format(read_str_from_file(agent_comm))

            user_input = input(f"[to main] >>  ")
            
            if user_input.lower() == 'quit':
                os.remove(main_comm) if os.path.exists(main_comm) else None
                sys.exit(0)

            history.append({'role':'user','content':user_input})
            # print(history)

            llm_process(model_name, history)
            print("")

            f = open(main_comm,'w')
            f.write(his_to_str(args.role, history))
            f.flush()
            f.close()
            his_dict[args.role] = history
    else:
        # agent actions here. todo: this is redundant
        history = his_dict[args.role]
        while True:

            for chat in history:
                if chat['role'] == 'system':
                    chat['content'] = agent_prompt.format(read_str_from_file(main_comm))

            user_input = input(f"[to agent] >>  ")
            
            if user_input.lower() == 'quit':
                os.remove(agent_comm) if os.path.exists(agent_comm) else None
                sys.exit(0)

            history.append({'role':'user','content':user_input})

            # print(history)

            llm_process(model_name, history)
            print("")

            f = open(agent_comm,'w')
            f.write(his_to_str(args.role, history))
            f.flush()
            f.close()
            his_dict[args.role] = history

