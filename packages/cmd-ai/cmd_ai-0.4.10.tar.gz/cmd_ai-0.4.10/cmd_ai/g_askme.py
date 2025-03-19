#!/usr/bin/env python3
"""
We create a unit, that will be the test_ unit by ln -s simoultaneously. Runs with 'pytest'
"""
import datetime as dt
import time
import os
import tiktoken
from console import fg,bg,fx
from fire import Fire
import pandas as pd

import openai
from cmd_ai import config
from cmd_ai import texts
from cmd_ai.version import __version__

#### ---- functions -----
from  cmd_ai import function_chmi
from  cmd_ai import function_goog # google search
from  cmd_ai import function_webc # web content
from  cmd_ai import function_calendar # save to DIR and Calendar
import json # for function call


import anthropic
from cmd_ai.api_key import get_api_key_anthropic

# model tools/function recursive tracker
GLOBAL_DEPTH=0

# def num_tokens_from_messages(model="gpt-3.5-turbo-0613"):
#     """
#     Return the number of tokens used by a list of messages.
#     Use by force this model 3.5, gpt4 didnt work
#     """

#     try:
#         encoding = tiktoken.encoding_for_model(model)
#     except KeyError:
#         print("Warning: model not found. Using cl100k_base encoding.")
#         encoding = tiktoken.get_encoding("cl100k_base")
#     if model in {
#         "gpt-3.5-turbo-0613",
#         "gpt-3.5-turbo-16k-0613",
#         "gpt-4-0314",
#         "gpt-4-32k-0314",
#         "gpt-4-0613",
#         "gpt-4-32k-0613",
#         "gpt-4o-2024-08-06",
#     }:
#         tokens_per_message = 3
#         tokens_per_name = 1
#     elif model == "gpt-3.5-turbo-0301":
#         tokens_per_message = (
#             4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
#         )
#         tokens_per_name = -1  # if there's a name, the role is omitted
#     elif "gpt-3.5-turbo" in model:
#         print(
#             "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
#         )
#         return num_tokens_from_messages(config.messages, model="gpt-3.5-turbo-0613")

#     elif "gpt-4" in model:
#         print(
#             "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
#         )
#         return num_tokens_from_messages(config.messages, model="gpt-4")
#     else:
#         raise NotImplementedError(
#             f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
#         )
#     num_tokens = 0
#     for message in config.messages:
#         print( fg.orange, message , fg.default )
#         num_tokens += tokens_per_message
#         for key, value in message.items():
#             num_tokens += len(encoding.encode(value))
#             if key == "name":
#                 num_tokens += tokens_per_name
#     num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
#     return num_tokens


# ===============================================================================================
# def get_price(model, tokens_in = 1, tokens_out = 1):
#     """
#     just putting something that work more or lss
#     """
#     if model == "gpt-4o-2024-05-13":
#         return 0.005/1000 * tokens_in + 0.015/1000 * tokens_out
#     elif model == "gpt-4-turbo-2024-04-09":
#         return 0.01/1000 * tokens_in + 0.03/1000 * tokens_out
#     elif model == "gpt-4-1106-preview":
#         return 0.01/1000 * tokens_in + 0.03/1000 * tokens_out
#     elif model == "gpt-4":
#         return 0.03/1000 * tokens_in + 0.06/1000 * tokens_out
#     elif model == "gpt-4-32k":
#         return 0.06/1000 * tokens_in + 0.12/1000 * tokens_out
#     elif model == "gpt-3.5-turbo-1106":
#         return 0.001/1000 * tokens_in + 0.002/1000 * tokens_out
#     #
#     #
#     elif model.find("gpt-4o-mini") >= 0:
#         return 0.01/1000 * tokens_in + 0.03/1000 * tokens_out
#     elif model.find("gpt-4o") >= 0:
#         return 0.005/1000 * tokens_in + 0.015/1000 * tokens_out
#     elif model.find("gpt-4-turbo") >= 0:
#         return 0.01/1000 * tokens_in + 0.03/1000 * tokens_out
#     elif model.find("gpt-4") >= 0:
#         return 0.01/1000 * tokens_in + 0.03/1000 * tokens_out
#     elif model.find("gpt-3.5-turbo") >= 0:
#         return 0.001/1000 * tokens_in + 0.002/1000 * tokens_out

#     else:
#         print("X... unknown model for calculating the budget",model)
#         return 0.03/1000 * tokens_in + 0.03/1000 * tokens_out
#     return -1




# ===========================================================================
#   generated :  calculate price
# ---------------------------------------------------------------------------

def get_price(model_name, input_tokens=0, output_tokens=0):
    """
    generated from the org  table by AI
    """
    data = {'Model': ['gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4o-audio-preview', 'gpt-4o-audio-preview-2024-12-17', 'gpt-4o-audio-preview-2024-12-17', 'gpt-4o-audio-preview-2024-10-01', 'gpt-4o-realtime-preview', 'gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-realtime-preview-2024-10-01', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18', 'gpt-4o-mini-2024-07-18', 'gpt-4o-mini-audio-preview', 'gpt-4o-mini-audio-preview-2024-12-17', 'gpt-4o-mini-audio-preview-2024-12-17', 'gpt-4o-mini-realtime-preview', 'gpt-4o-mini-realtime-preview-2024-12-17', 'gpt-4o-mini-realtime-preview-2024-12-17', 'o1', 'o1-2024-12-17', 'o1-2024-12-17', 'o1-preview-2024-09-12', 'o1-mini', 'o1-mini-2024-09-12', 'o1-mini-2024-09-12', 'o3-mini-2025-01-31', 'gpt-4.5-preview', 'gpt-4.5-preview-2025-02-27'], 'Input Price': [2.5, 2.5, 2.5, 2.5, 5.0, 2.5, 2.5, 2.5, 2.5, 5.0, 5.0, 5.0, 5.0, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.6, 0.6, 0.6, 15.0, 15.0, 15.0, 15.0, 3.0, 3.0, 3.0, 1.1, 75.0, 75.0], 'Output Price': [10.0, 10.0, 10.0, 10.0, 15.0, 10.0, 10.0, 10.0, 10.0, 20.0, 20.0, 20.0, 20.0, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 2.4, 2.4, 2.4, 60.0, 60.0, 60.0, 60.0, 12.0, 12.0, 12.0, 4.4, 150.0, 150.0]
             }
    #     "Model": [
    #         "gpt-4o", "gpt-4o-2024-08-06", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06",
    #         "gpt-4o-2024-05-13", "gpt-4o-audio-preview", "gpt-4o-audio-preview-2024-12-17",
    #         "gpt-4o-audio-preview-2024-12-17", "gpt-4o-audio-preview-2024-10-01",
    #         "gpt-4o-realtime-preview", "gpt-4o-realtime-preview-2024-12-17",
    #         "gpt-4o-realtime-preview-2024-12-17", "gpt-4o-realtime-preview-2024-10-01",
    #         "gpt-4o-mini", "gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18",
    #         "gpt-4o-mini-audio-preview", "gpt-4o-mini-audio-preview-2024-12-17",
    #         "gpt-4o-mini-audio-preview-2024-12-17", "gpt-4o-mini-realtime-preview",
    #         "gpt-4o-mini-realtime-preview-2024-12-17", "gpt-4o-mini-realtime-preview-2024-12-17",
    #         "o1-preview", "o1-2024-12-17", "o1-2024-12-17", "o1-preview-2024-09-12",
    #         "o1-mini", "o1-mini-2024-09-12", "o1-mini-2024-09-12"
    #     ],
    #     "Input Price": [
    #         2.50, 2.50, 2.50, 2.50, 5.00, 2.50, 2.50, 2.50, 2.50, 5.00, 5.00, 5.00, 5.00,
    #         0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.60, 0.60, 0.60, 15.0, 15.0, 15.0, 15.0,
    #         3.00, 3.00, 3.00
    #     ],
    #     "Output Price": [
    #         10.00, 10.00, 10.00, 10.00, 15.00, 10.00, 10.00, 10.00, 10.00, 20.00, 20.00, 20.00, 20.00,
    #         0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 2.40, 2.40, 2.40, 60.00, 60.00, 60.00, 60.00,
    #         12.00, 12.00, 12.00
    #     ]
    # }

    df = pd.DataFrame(data)
    model_row = df[df['Model'] == model_name]

    if model_row.empty:
        return 0 #"Model not found."

    input_price = model_row['Input Price'].values[0]
    output_price = model_row['Output Price'].values[0]

    total_price = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price

    return total_price


# ===============================================================================================
def log_price(model, tokens_in = 1, tokens_out = 1):

    price = round(100000*get_price( model, tokens_in, tokens_out ))/100000

    with open( os.path.expanduser( config.CONFIG['pricelog']), "a" )  as f:
        now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        f.write(f"{now} {tokens_in} {tokens_out} {price}")
        f.write("\n")



###================================================================================

def g_ask_chat(prompt, temp, model,  total_model_tokens=4096 * 2 - 50, tool=False):
    #
    """
    CORE ChatGPT function
    """
    # global task_assis, limit_tokens
    global GLOBAL_DEPTH # track depth...

    # ---- if no system present, add it
    if len(config.messages) == 0:
        config.messages.append({"role": "assistant", "content": texts.role_assistant})
    # add the message~
    if tool:
        config.messages.append( prompt )
    else:
        config.messages.append({"role": "user", "content": prompt})

    #max_tokens = total_model_tokens - num_tokens_from_messages()
    max_tokens = 300 # total_model_tokens - num_tokens_from_messages()
    limit_tokens = config.CONFIG['limit_tokens']
    #if not config.silent:
    #    print(f"D...   {fg.lightslategray}{fx.italic}g_ask_chat: conf tokens:", config.CONFIG['limit_tokens'], fg.default, fx.default)
    if limit_tokens < 30000: # ;max_tokens
        max_tokens = limit_tokens
    #if not config.silent:
    #    print(f"i...  {fx.italic}{fg.lightslategray}max_tokens: {max_tokens}, model: {model};  {fg.default}{fx.default}")
    #
    # DEBUG PURPLE
    #print(fg.lightpurple,config.messages,fg.default)

    # THIS CAN OBTAIN ERROR: enai.error.RateLimitError: Rate limit reached for 10KTPM-200RPM in organization org-YaucYGaAecppFiTrhbnquVvB on tokens per min. Limit: 10000 / min. Please try again in 6ms.
    # token size block it

    waittime = [
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
        3,
    ]


    #####################################################################################

    DONE = len(waittime) - 1
    responded = False
    while DONE > 0:  # I forgot to decrease
        DONE -= 1
        time.sleep(1 * waittime[0])
        if GLOBAL_DEPTH>5:
            print("X... TOO DEEP RECURISVELY", GLOBAL_DEPTH)
            sys.exit(1)
        try:
            # print(messages)
            if not config.silent:
                print(bg.white," --> ", fg.blue,"depth:",GLOBAL_DEPTH, " ", bg.default, end="", flush=True)

            ################################################
            #         MODEL CALL    ########################
            ################################################
            response = None
            if len(config.TOOLLIST)>0:
                print(f" ... {fg.red} request with TOOLS ON {fg.default}")
                #print(config.TOOLLIST)
                #print("--------------------------------------------------")
                #print(config.messages)
                #print("--------------------------------------------------")
                response = config.client.chat.completions.create(
                    model=model,
                    messages=config.messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                    tool_choice="auto",
                    tools= config.TOOLLIST )
                #print(f" ... response length is {len(response)} ")
            else:
                #print(f" ... {fg.red} {model} * {config.messages} {fg.default} begin")
                #print(type(config.messages))
                # config.messages = [
                #         { "role": "assistant", "content": "You speak briefly, in short sentences." },
                #         { "role": "user",
                #          "content": "What version of gpt are you?"
                #             }
                #         ]
                # print(type(config.messages))
                #print(f" ... {fg.red} {model} * {config.messages} {fg.default} begin")
                response = config.client.chat.completions.create(
                    model=model,
                    messages=config.messages,
#                    store=True
#                    temperature=temp,
#                    max_tokens=max_tokens
                )

                #print(f" ... {fg.red} {model} {fg.default} end")

            if not config.silent:
                print("...",bg.green," >>OK", bg.default, f" model={model}")
            DONE = 0
            responded = True

    #####################################################################################


        except openai.RateLimitError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 1 * waittime[0]
            #if hasattr(e,"message"): print(e.message)
            if hasattr(e,"code"): print(e.code)
            if hasattr(e,"type"): print(e.type)
            print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            waittime.pop(0)
            DONE -= 1

        except openai.APIError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 1 * waittime[0]
            if hasattr(e,"code"): print(" ... error code:", e.code)
            if hasattr(e,"type"): print(" ... error type:", e.type)
            print(f" ... API error occurred. Retrying in {retry_time} seconds...")
            print(" ... ... might be for difficulties when calling a tool? Unallowd options?")
            time.sleep( retry_time)
            waittime.pop(0)
            DONE -= 1

        except openai.ServiceUnavailableError as e:
            retry_time = 10  # Adjust the retry time as needed
            if hasattr(e,"code"): print(e.code)
            if hasattr(e,"type"): print(e.type)
            print(f"Service is unavailable. Retrying in {retry_time} seconds...")
            time.sleep(1 * waittime[0])
            waittime.pop(0)
            DONE -= 1

        except openai.Timeout as e:
            retry_time = 10  # Adjust the retry time as needed
            if hasattr(e,"code"): print(e.code)
            if hasattr(e,"type"): print(e.type)
            print(f"Request timed out: {e}. Retrying in {retry_time} seconds...")
            time.sleep(1 * waittime[0])
            waittime.pop(0)
            DONE -= 1

        except OSError as e:
            if isinstance(e, tuple) and len(e) == 2 and isinstance(e[1], OSError):
                retry_time = 10  # Adjust the retry time as needed
                if hasattr(e,"code"): print(e.code)
                if hasattr(e,"type"): print(e.type)
                print(f"Connection error occurred: {e}. Retrying in {retry_time} seconds...")
                time.sleep(1 * waittime[0])
                waittime.pop(0)
                DONE -= 1


            else:
                retry_time = 10  # Adjust the retry time as needed
                print(f"Connection error occurred: {e}. Retrying in {retry_time} seconds...")
                time.sleep(retry_time)
                raise e







    # print("i... OK SENT")
    if not responded:
        print("i... NOT RESPONDED  ====================================")
        return None

    #print(type(response))
    #print(str(response))

    resdi = response.choices[0].message.content
    finish = response.choices[0].finish_reason
    # I believe that tokens are correctly counted
    tokens_out = response.usage.completion_tokens
    tokens_in = response.usage.prompt_tokens
    tokens = response.usage.total_tokens
    price = get_price( model, tokens_in, tokens_out)
    # not rosybrown color

    now = dt.datetime.now()#  .replace(microsecond=0)

    #print(fg.lightpurple,prompt,fg.default)
    task_sec=round( (now-config.started_task).total_seconds() ,1 )
    total_sec = round( (now-config.started_total).total_seconds(), 1 )

    if not config.silent:
        print(f"i... {fx.italic}{fg.lightslategray}tokens: {tokens_in} in + {tokens_out} out == {tokens}  for {round(price*10000)/10000}$ ... task: {task_sec} s; total:{total_sec} s{fx.default}{fx.default}{fg.default}")

    log_price( model, tokens_in, tokens_out )
    STOPPED_BY_LENGTH = False
    if finish != "stop":
        if finish!="tool_calls":
            print(f"!... {fg.red} stopped because : {finish} {fg.default}")
            STOPPED_BY_LENGTH = True

        # print( response ) # DEBUG #
        if finish=="tool_calls":
            print(f"!... {fg.green} stopped because : {finish} {fg.default}")
            #print("####")
            #print( response.choices[0].message )
            #print( response.choices[0].message.tool_calls[0] )

            response_message = response.choices[0].message
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                if config.DEBUG: print("i... appending current response...  ")#, response_message)
                config.messages.append(response_message)
                for tool_call in tool_calls:

                    function_name = tool_call.function.name
                    # this i have
                    function_to_call = config.available_functions[function_name]
                    function_args = tool_call.function.arguments # NO json.loads here...
                    #print(f"i... executing {function_name} with {function_args}")
                    function_response = execute_function_call( function_name, function_args  )

                    if config.DEBUG: print("i... appending the result length==", len(function_response) )
                    #print(f"i... {fg.green} {function_response}{fg.default}")
                    #print()
                    LAST_MESSAGE = {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    #config.messages.append( LAST_MESSAGE )  # extend conversation with function response


                GLOBAL_DEPTH+=1
                rrres = g_askme(LAST_MESSAGE, model=model, tool=True)
                GLOBAL_DEPTH-=1

                #print(fg.lightpurple,rrres,fg.default)
                return rrres
                # --- THIS WORKED
                #second_response = config.client.chat.completions.create(
                #    model=model,
                #    messages=config.messages,
                #)  # get a new response from the model where it can see the function response
                #
                # return second_response.choices[0].message.content # my version



            #print( response.choices[0].message.tool_calls[0].function )
            function_name  = response.choices[0].message.tool_calls[0].function.name
            funpar = response.choices[0].message.tool_calls[0].function.arguments
            print( "i... calling", function_name, funpar )
            function_response = execute_function_call( function_name, funpar  )
            # replace output
            resdi = function_response # external function was called... should be json.dumps

            # #config.messages.append(response.choices[0].message)  # extend conversation with assistant's reply

            # # UPDATE SOMEHOW ABOUT THIS CONVERSATION

            # config.messages.append( #response.choices[0].message)
            #     {
            #         "role":  config.CONFIG["current_role"],
            #         "content": None, #f"calling external function {function_name} with parameters {funpar}",
            #         "function_call":  { "function":{"name":function_name,"arguments":funpar} } ]
            #         # "output": function_response
            #     }
            # )

            # config.messages.append(
            #     {
            #         "role": "function",
            #         "name": function_name,
            #         "content": str(function_response),
            #     }
            # )

            # # config.messages.append( #response.choices[0].message)
            # #     {
            # #         "role":  "function", #config.CONFIG["current_role"],
            # #         "output": function_response,
            # #         "content": None
            # #         #"tool_calls": [ { "function":{"name":function_name,"arguments":funpar} } ]
            # #         # "output": function_response
            # #     }
            # # )

            # # config.messages.append(
            # #     {
            # #         "role": "function",
            # #         "name": function_name,
            # #         "content": str(function_response),
            # #     }
            # # )

            print("============ LAST PICTURE OF THE FUNCTION CALL ==============")
            print(config.messages)
        print(f"!... {fg.red} stopped because : {finish} {fg.default}")

    # resdi = json.loads( str(response)  )
    return resdi, STOPPED_BY_LENGTH
    # print(resdi)

    # ========================================================================



def execute_function_call(function_name,arguments):
    print("i--- executing ", function_name)
    function = config.available_functions.get(function_name,None)
    if function:
        arguments = json.loads(arguments)
        if config.DEBUG: print("i--- running ", arguments )
        results = function(**arguments)
    else:
        results = f"Error: function {function_name} does not exist"
    return results



# def getCzechWeather( time ):

#     res = "Kolem tlakové výše se středem nad Francií k nám proudí teplý vzduch od západu.   Počasí u nás bude zpočátku ovlivňovat okraj tlakové výše nad jižní Evropou, postupně studená fronta od severozápadu."
#     if time=="today":
#         res = "Kolem tlakové výše se středem nad Francií k nám proudí teplý vzduch od západu."
#     if time=="tomorrow":
#         res = "Počasí u nás bude zpočátku ovlivňovat okraj tlakové výše nad jižní Evropou, postupně studená fronta od severozápadu."
#     return json.dumps(  {"weather":res } , ensure_ascii=False) #  i can see they do json.dumps( dict )



########################################################
config.available_functions = {
    "getCzechWeather": function_chmi.get_chmi, # getCzechWeather,
    "searchGoogle": function_goog.get_google_urls, #
    "getWebContent": function_webc.fetch_url_content, #
    "setMeetingRecord": function_calendar.setMeetingRecord, # i am trying new thing
    "getTodaysDateTime": function_calendar.getTodaysDateTime, # i am trying new thing
}


# **********************************************************************************
# **********************************************************************************
# **********************************************************************************
# **********************************************************************************
# model="claude-3-7-sonnet-20250219"
# model="claude-3-5-sonnet-20241022"
def g_ask_claude(prompt , temp=0,
                 model="claude-3-7-sonnet-20250219",
#                 model="claude-3-5-sonnet-20241022",
                 max_tokens=1000, role=None):
    STOPPED_BY_LENGTH = False
    # ** init
    clienta = anthropic.Anthropic(api_key=get_api_key_anthropic())

    system_prompt = texts.role_assistant
    if role is None:
        system_prompt = texts.role_assistant



    # ---- if no system present, add it
    #if len(config.messages) == 0:
    #    config.messages.append({"role": "system", "content": texts.role_assistant})

    #    config.messages.append({"role": "user", "content": prompt})
    newmsg = []
    for i in config.messages:
        #print("D...", type(i), i)
        #if i["role"] == "assistant": continue
        newmsg.append( i )

    #config.messages.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    newmsg.append({"role": "user", "content": [{"type": "text", "text": prompt}] } )
    limit_tokens = config.CONFIG['limit_tokens']

    #print(newmsg)


    #********************************************** GO
    message = clienta.messages.create(
        model=model,
        max_tokens=limit_tokens,
        temperature=temp,
        system=system_prompt,
        messages=newmsg #config.messages,#[
#            {
#                "role": "user", "content": [ {"type": "text", "text": prompt }]
#            } #, {next turn}, {next turn}
#
#        ]
    )
    # **********
    response = message.content
    res = response[0].text #decode_response_anthropic(message.content)

    if not config.silent:
        print("...",bg.green," >>OK", bg.default, f" model={model}")
    return res, STOPPED_BY_LENGTH



def g_askme(
        prompt,
        temp=0.0,
        model="gpt-4-1106-preview",
        # limit_tokens=300,
        total_model_tokens=4096 * 2 - 50, # guess
        tool = False
):
    """
    CALL g_ask_chat()
    """
    #print(prompt)

    #if model is not None:
    config.MODEL_TO_USE = model   # HARD SWITCH MODEL

    # #model_change = False
    # if prompt.lower().find("claude,") == 0:
    #     MODEL_TO_USE = "claude-3-5-sonnet-20241022"  # sonnet is fast, may bbe worse in math, good in science
    #     #model_change = True
    # elif prompt.lower().find("opus,") == 0:
    #     MODEL_TO_USE = "claude-3-opus-20240229" # no reason, maybe math+reasoning
    #     #model_change = True
    # elif prompt.lower().find("gpt,") == 0:
    #     MODEL_TO_USE = "gpt-4o-2024-08-06"
    #     #model_change = True
    # else:
    #     MODEL_TO_USE = model

    #estimate_tokens = num_tokens_from_messages() + len(prompt) + 600
    #estimate_tokens = 300
    estimate_tokens = config.CONFIG['limit_tokens']
    #if not config.silent:
    #    print(f"D....  {fg.lightslategray}{fx.italic}g_ask estimate tokens {estimate_tokens}; {MODEL_TO_USE}",fg.default, fx.default)

    resdi = None
    if config.MODEL_TO_USE.find("claude") >= 0:
        #print("C")
        resdi = g_ask_claude( prompt, temp, config.MODEL_TO_USE, estimate_tokens)

    else:
        #print("G")
        resdi = g_ask_chat( prompt, temp, config.MODEL_TO_USE, estimate_tokens, tool=tool )

    #if model_change:
    if resdi is None:
        return None
    return resdi[0],resdi[1], config.MODEL_TO_USE
    return resdi


if __name__ == "__main__":
    print("i... in the __main__ of unitname of cmd_ai")
    Fire(get_price)
