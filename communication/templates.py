prompt_talkplayer=f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}.
The status of you is as follows:
Location: {location}
Status: {name} is casually chatting with Miles.
The interactions are as follows:
{name_player} (speaking): {message}<|eot|>"""

prompt_talknpc_init=f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}.
The status of you is as follows:
Location: {location}
Status: You are talking with {name_other}. Talk with {name_other} considering the relationship between you and {name_other}. Say hello to him.
The interactions are as follows:
"""
prompt_talknpc_init+=relationship


prompt_talknpc=f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}.
The status of you is as follows:
Location: {location}
Status: f'You are talking with {name_other}. Talk with {name_other} considering the relationship between you and {name_other}. Following is the conversation between you and him. \n'
The interactions are as follows:
"""
prompt_talknpc+=relationship
for i in conversation_log:
    prompt_talknpc+=i
