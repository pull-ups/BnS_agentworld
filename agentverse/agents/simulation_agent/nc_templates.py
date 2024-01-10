
def get_prompt_talkplayer(name, location, name_player, message):
    return f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}. Also, talk briefly, not too long.
The status of you is as follows:
Location: {location}
Status: {name} is casually chatting with {name_player}.
The interactions are as follows:
{name_player} (speaking): {message}<|eot|>"""

def get_prompt_talknpc_init(name, location, name_other, relationship):
    prompt_talknpc_init=f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}. Also, talk briefly, not too long.
The status of you is as follows:
Location: {location}
Status: You are talking with {name_other}. Talk with {name_other} considering the relationship between you and {name_other}. Say hello to him.
The interactions are as follows:
"""
    prompt_talknpc_init+=relationship
    return prompt_talknpc_init


def get_prompt_talknpc(name, location, name_other, relationship, conversation_log):
    prompt_talknpc=f"""I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}.  Also, talk briefly, not too long.
The status of you is as follows:
Location: {location}
Status: f'You are talking with {name_other}. Talk with {name_other} considering the relationship between you and {name_other}. Following is the conversation between you and him. \n'
The interactions are as follows:
"""
    prompt_talknpc+=relationship
    for (speaker, message) in conversation_log:
        prompt_talknpc+=f"{speaker} (speaking): {message}<|eot|>\n"
    return prompt_talknpc