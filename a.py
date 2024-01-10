import requests

url = "http://127.0.0.1:10003/reactionplan"

# Data to be sent in the POST request
#data = {"agents_id":[1,2,3,4],"reactions":[" Jinsoyun, gazing at the flames consuming Jiwan's Peak, her heart heavy with anguish and determination, Jinsoyun's grip on her sword tightens as she contemplates her next move. Her eyes, filled with a mix of rage and sorrow, pierce through the darkness, reflecting the flickering embers of the raging inferno."," I will focus my chi, channeling the power of Dark Chi within me, using the flames as a conduit for my emanation of vengeance. The crackling fire becomes my ally, my catalyst for destruction. I will unleash a storm of chaos upon my enemies, consuming all who stand in my way."," Ah, the sound of flames and destruction, an ironic accompaniment to our victory. The defeat of the Ultrasoul would have been far more satisfying without it, don' inc ~ A lesser foe, but one that still provided a measure of entertainment. The heat licks at my skin, a comforting reminder of my immortal nature."," Fire! The very word sends a shiver down my spine as I glance around, my heart pounding in my chest. The flames lick at the edges of the camp, devouring everything in their path, their heat searing the air with an intensity that is both terrifying and mesmerizing."]}
#data = '{"agent_id":[1,2,3,4],"reactions":["A","B","C","D"]}'
data = '{"agent_id":[1,2,3,4],"reactions":["A","B","C","D"]}'
# Sending the POST request
response = requests.post(url, data=data)

# Printing the response
print("Status Code:", response.status_code)
print("Response Text:", response.text)