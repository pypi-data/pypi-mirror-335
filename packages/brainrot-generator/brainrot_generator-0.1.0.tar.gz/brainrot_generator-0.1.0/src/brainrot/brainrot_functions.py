import random

#predefined list 
brainrot_list = {
    "Haliey Welch": ["hawk tuah, spit on that thang"],
    "The Costco Guys": ["We're so sorry to hear about your brother that passed away he gets five big booms... BOOM. BOOM. BOOM. BOOM. BOOOOOOOOM!!"],
    "94.48% Accurate": ["LET ME KNOWWW (LET ME KNOW). DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY. HEY, DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY"], 
    "Millenial Burger Restaurant": ["We are Young! Ho! There's a fire in our soul. We go big or go home together!"], 
    "Montoya": ["MONTOYA POR FAVOR"], 
    "Great Meme Drought of 2025": ["[Kazoo]: LET ME KNOWWW (LET ME KNOW). DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY. HEY, DO YOU LOVE THE WAY I DO WHEN I'M LOVING YOUR BODY"],
    "Severance": ["Mark is hot, Helly's hot, Irv is hot, Gemma's hot, Dylan's hot, Milkshake's hot... They're all really hot"],
    "FettyWap": ["I want you to be mine again, baby, ayy. I know my lifestyle is drivin' you crazy, ay"], 
    "G3 - TWEAKER ACOUSTIC": ["I might swerve bend that corner whoa whoa... bit hold on tight cause I'll tweak in this bit start letting sh** go"],
    "Sal Vulcano": ["My name is Tanka Jahari, but I would NEVER eat a whole pizza by myself"],
    "Civ": ["Say my name (Say my name), get it right (Get it right) I'm your man (I'm your man), for the night. We pop out at 1 in the mornin' You really wanna know, this kind of life never borin' "],
    "Comments": [
        "🥀",
        "They gonna show this in congress bro 😭.",
        "They gonna show this on Fox News bro 😭 ",
        "Historians skipping our generation",
        "ahh"
    ],
    "RayWilliamJohnson": ["He had a pew pew and unalived someone"],
    "Hoszier": ["*yells"], 
    "bro": ["The typa shi bro sends when ___"], 
    "Redsun": ["[extremely high pitched]: 天上太阳红呀红通通 唉, 心中的太阳是毛泽东 唉"], 
    "Chinese Song": ["我们今生注定是沧桑 哭着来要笑着走过呀"],
    "Girlfriends": ["When my boyfriend still hasn't asked me to be his spring for spring break yet"], 
    "Where you at": ["I'm in North Liberty"], 
    "I'm in North Liberty": ["DOING HHWATTT"],
    "Jaden": ["I go around sometimes and I hang out around people my age and..."],
    "A person...": ["A person who thinks all the time... has nothing to thinnk about except thoughts"],
    "TS": ["PMO 🥀"],
    "LED guy": ["Not interested sir... ANYWAYS here's how to tell if your sign's cheap... "],
    "Cave Diver": ["** Leaves wife and kids when they hear a new cave called 'satan's crack' with the entrance the size of a peanut"], 
    "Little John": ["Galvanzied Square steel and screws from his aunt"],
    "Hyperpigmentation": ["It is fanTAStic"], 
    "Joe Biden": ["SODA"], 
    "Trump": ["ObamNa"],
    "Freak": ["Bob"], 
    "John": ["Pork"],
    "Joshua Block": ["Put the fries in the bag"], 
    "The uninvited": ["oh my god bruh, oh hell nah man, who invited this kid,"],
    "skibidi": ["toilet rizz"], 
    "what the": ["sigma"], 
    "chat": ["we're cooked"], 
    "raise your": ["raise your ya ya ya"], 
    "fine": ["shyt"], 
    "Ws": ["ws in the shatt"], 
    "Mama": ["Mama a girl behind you"],
    "10": ["level 10 gyat"], 
    "negative": ["aura"],
    "Only in": ["Ohio"],
    "Wait": ["They don't love you like I love you"],    
    "Haliey Welch": ["hawk tuah, spit on that thang"],
    "The Costco Guys": ["We're so sorry to hear about your brother that passed away he gets five big booms... BOOM. BOOM. BOOM. BOOM. BOOOOOOOOM!!", "we bring the BOOM"]
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
def rotify(input_string: str):
    return input_string + " ahh"

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
    brainrot_dump = [item for sublist in brainrot_list.values() for item in sublist]
    random.shuffle(brainrot_dump) # shuffle the list randomly
    brainrot_words = (" ".join(brainrot_dump)).split(" ")
    
    word_counter = min(word_counter, len(brainrot_dump))
    return " ".join(brainrot_words[:word_counter])



