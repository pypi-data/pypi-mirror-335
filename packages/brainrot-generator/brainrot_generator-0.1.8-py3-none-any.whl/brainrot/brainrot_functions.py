import random

#predefined list 
brainrot_list = {
    "haliey welch": ["hawk tuah, spit on that thang"],
    "squid games": ["I've played these games before!"],
    "the costco guys": ["We're so sorry to hear about your brother that passed away he gets five big booms... BOOM. BOOM. BOOM. BOOM. BOOOOOOOOM!!",
                        "We bring the BOOM, that's what we do"],
    "94.48% accurate": ["LET ME KNOWWW (LET ME KNOW). DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY. HEY, DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY"], 
    "millenial burger restaurant": ["We are Young! Ho! There's a fire in our soul. We go big or go home together!"], 
    "montoya": ["MONTOYA POR FAVOR"], 
    "great meme drought of 2025": ["[Kazoo]: LET ME KNOWWW (LET ME KNOW). DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY. HEY, DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY"],
    "severance": ["Mark is hot, Helly's hot, Irv is hot, Gemma's hot, Dylan's hot, Milkshake's hot... They're all really hot","mm- mm- mark?"],
    "fettywap": ["I want you to be mine again, baby, ayy. I know my lifestyle is drivin' you crazy, ay"], 
    "g3 - tweaker acoustic": ["I might swerve bend that corner whoa whoa... bit hold on tight cause I'll tweak in this bit start letting sh** go"],
    "sal vulcano": ["My name is Tanka Jahari, but I would NEVER eat a whole pizza by myself"],
    "civ": ["Say my name (Say my name), get it right (Get it right) I'm your man (I'm your man), for the night. We pop out at 1 in the mornin' You really wanna know, this kind of life never borin' "],
    "comments": [
        "🥀",
        "They gonna show this in congress bro 😭.",
        "They gonna show this on Fox News bro 😭 ",
        "Historians skipping our generation",
        "ahh"
        "goofy ahh"
    ],
    "raywilliamjohnson": ["He had a pew pew and unalived someone"],
    "hozier": ["*yells"], 
    "bro": ["The typa shi bro sends when ___"], 
    "redsun": ["[extremely high pitched]: 天上太阳红呀红通通 唉, 心中的太阳是毛泽东 唉"], 
    "chinese song": ["我们今生注定是沧桑 哭着来要笑着走过呀"],
    "girlfriends": ["When my boyfriend still hasn't asked me to be his spring for spring break yet"], 
    "where you at": ["I'm in North Liberty"], 
    "i'm in north liberty": ["DOING HHWATTT"],
    "jaden": ["I go around sometimes and I hang out around people my age and..."],
    "a person...": ["A person who thinks all the time... has nothing to thinnk about except thoughts"],
    "ts": ["PMO 🥀"],
    "led guy": ["Not interested sir... ANYWAYS here's how to tell if your sign's cheap... "],
    "cave diver": ["** Leaves wife and kids when they hear a new cave called 'satan's crack' with the entrance the size of a peanut"], 
    "little john": ["Galvanzied Square steel and screws from his aunt"],
    "hyperpigmentation": ["It is fanTAStic"], 
    "joe biden": ["SODA"], 
    "trump": ["ObamNa"],
    "obama": ["Let me be clear"],
    "freak": ["Bob"], 
    "john": ["Pork"],
    "joshua block": ["Put the fries in the bag"], 
    "the uninvited": ["oh my god bruh, oh hell nah man, who invited this kid,"],
    "gen alpha": ["toilet rizz","what the sigma","level 10 gyat","Only in Ohio","negative aura", "livvy dunne"],
    "chat": ["we're cooked"], 
    "raise your": ["raise your ya ya ya"], 
    "fine": ["shyt"], 
    "ws": ["ws in the shatt"], 
    "mama": ["Mama a girl behind you"],
    "wait": ["They don't love you like I love you"]
}

# brainrot function
# arguments: integer number
# return: n random brainrots from list
def brainrot(n: int):
    # check if n is an integer
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    # check if n is positive
    if n <= 0:
        return {}
    
    selected_keys = random.sample(list(brainrot_list.keys()), min(n, len(brainrot_list)))
    return {key: brainrot_list[key] for key in selected_keys}

# brainrot of specific person function
# arguments: name
# return: a brainrot attributed to input name
def get_brain_rot_of(name):
    name = name.lower()
    if not isinstance(name, str):
         name = str(name)
    if name in brainrot_list:
          return name + ": " + random.choice(brainrot_list[name])
    else:
         return name + " is unfortunately not a brainrot contributor"

# Random capitalization function
# arguments: string phrase
# return: string with mixed capitalization
def random_capitalization(phrase: str):
    result = ""
    for i in range(len(phrase)):
            result += phrase[i].upper() if i % 2 == 1 else phrase[i]
    return result 

# rotify function
# arguments: string phrase
# return: string with "ahh" concatenated
def rotify(phrase):
    if not isinstance(phrase,str):
        phrase = str(phrase)
    return phrase + " ahh"

# backwards text function
# arguments: text
# return: string in opposite direction
def backwards_text(text):
    result = ""
    if not isinstance(text, str):
        text = str(text)
    for i in range(len(text) - 1, -1, -1):
        result += text[i]
    return result
     
    
# generate_brain_rot function
# arguments: int word_counter
# return: string with word_counter words of brainrot
def generate_brain_rot(word_counter):
    if not isinstance(word_counter,int):
        return "Input value is not an integer"
    if word_counter == 0:
         return "No brainrot to be returned"
        
    brainrot_dump = [item for sublist in brainrot_list.values() for item in sublist]
    random.shuffle(brainrot_dump) # shuffle the list randomly
    brainrot_words = (" ".join(brainrot_dump)).split(" ")
    
    word_counter = min(word_counter, len(brainrot_dump))
    return " ".join(brainrot_words[:word_counter])
