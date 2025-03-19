import time
import random


jokes = [
    # {
    #   "id": 1,
    #   "setup": "Knock knock!",
    #   "punchline": "Who's there? Boo! Boo who? Don't cry, it's just a joke!"
    # },
    # {
    #   "id": 2,
    #   "setup": "What do ghosts serve for dessert?",
    #   "punchline": "I scream!"
    # },
    # {
    #   "id": 3,
    #   "setup": "Why didn't the skeleton go to the dance?",
    #   "punchline": "He had no-body to go with!"
    # },
    {
    "id": 4,
    "setup": "What's a ghost's favorite fruit?",
    "punchline": "Boo-berries!"
    },
    {
    "id": 5,
    "setup": "What do you call a ghost's mistake?",
    "punchline": "A boo-boo!"
    },
    # {
    #   "id": 6,
    #   "setup": "What kind of streets do ghosts haunt?",
    #   "punchline": "Dead ends!"
    # },
    # {
    #   "id": 7,
    #   "setup": "Why do ghosts like to ride elevators?",
    #   "punchline": "It lifts their spirits!"
    # },
    # {
    #   "id": 8,
    #   "setup": "What's a ghost's favorite dessert?",
    #   "punchline": "Boo-berry pie!"
    # },
    # {
    #   "id": 9,
    #   "setup": "Why did the ghost go to the bar?",
    #   "punchline": "For the boos!"
    # },
    # {
    #   "id": 10,
    #   "setup": "How do ghosts search the web?",
    #   "punchline": "They use Boo-gle!"
    # },
    # {
    #   "id": 11,
    #   "setup": "What do you call a ghost's favorite candy?",
    #   "punchline": "Boo-ble gum!"
    # },
    # {
    #   "id": 12,
    #   "setup": "Where do baby ghosts go during the day?",
    #   "punchline": "Dayscare centers!"
    # },
    # {
    #   "id": 13,
    #   "setup": "What's a ghost's favorite play?",
    #   "punchline": "Romeo and Boo-liet!"
    # },
    # {
    #   "id": 14,
    #   "setup": "What do you call a scary ghost?",
    #   "punchline": "Bam-boo!"
    # },
    # {
    #   "id": 15,
    #   "setup": "What kind of makeup do ghosts wear?",
    #   "punchline": "Mas-scare-a!"
    # },
    # {
    #   "id": 16,
    #   "setup": "What's a ghost's favorite social media app?",
    #   "punchline": "Snap-BOO!"
    # },
    # {
    #   "id": 17,
    #   "setup": "What kind of exercise do ghosts enjoy?",
    #   "punchline": "Boo-camp!"
    # },
    # {
    #   "id": 18,
    #   "setup": "Why do ghosts make terrible liars?",
    #   "punchline": "You can see right through them!"
    # },
    # {
    #   "id": 19,
    #   "setup": "What's a ghost's favorite ice cream flavor?",
    #   "punchline": "Boo-nilla!"
    # },
    # {
    #   "id": 20,
    #   "setup": "Why didn't the ghost join the football team?",
    #   "punchline": "They were afraid he'd phantom the plays!"
    # },
    # {
    #   "id": 21,
    #   "setup": "How do ghosts cheer for their favorite teams?",
    #   "punchline": "They stand up and BOO!"
    # },
    # {
    #   "id": 22,
    #   "setup": "What's a ghost's favorite nursery rhyme?",
    #   "punchline": "Little Boo Peep!"
    # },
    # {
    #   "id": 23,
    #   "setup": "What do you call a ghost detective?",
    #   "punchline": "A boo-sleuth!"
    # },
    # {
    #   "id": 24,
    #   "setup": "What kind of roads do ghosts travel on?",
    #   "punchline": "Boo-levards!"
    # },
    # {
    #   "id": 25,
    #   "setup": "What do you call a ghost's favorite vacation spot?",
    #   "punchline": "The Boo-hamas!"
    # },
    # {
    #   "id": 26,
    #   "setup": "What's a ghost's favorite carnival ride?",
    #   "punchline": "The roller-ghoster!"
    # },
    # {
    #   "id": 27,
    #   "setup": "Why do ghosts hate the rain?",
    #   "punchline": "It dampens their spirits!"
    # },
    # {
    #   "id": 28,
    #   "setup": "What's a ghost's favorite board game?",
    #   "punchline": "Hide and Shriek!"
    # },
    # {
    #   "id": 29,
    #   "setup": "What's a ghost's favorite music?",
    #   "punchline": "Sheet music!"
    # },
    # {
    #   "id": 30,
    #   "setup": "What kind of ghost haunts gyms?",
    #   "punchline": "Exorcise ghosts!"
    # },
    # {
    #   "id": 31,
    #   "setup": "Why did the ghost apply for a loan?",
    #   "punchline": "He needed some boo-llion!"
    # },
    # {
    #   "id": 32,
    #   "setup": "What's a ghost's favorite instrument?",
    #   "punchline": "The boo-kulele!"
    # },
    # {
    #   "id": 33,
    #   "setup": "What do you call a ghost that gets things wrong?",
    #   "punchline": "A boo-boo!"
    # },
    # {
    #   "id": 34,
    #   "setup": "Why did the ghost go to therapy?",
    #   "punchline": "He had too many boo-issues!"
    # },
    # {
    #   "id": 35,
    #   "setup": "What soap do ghosts use?",
    #   "punchline": "BOO-ty wash!"
    # },
    # {
    #   "id": 36,
    #   "setup": "What's a ghost's favorite TV show?",
    #   "punchline": "American Horror-Story!"
    # },
    # {
    #   "id": 37,
    #   "setup": "What do you call a high-ranking ghost?",
    #   "punchline": "Boo-tenant General!"
    # },
    # {
    #   "id": 38,
    #   "setup": "What's a ghost's favorite hot beverage?",
    #   "punchline": "Ghoul-aid!"
    # },
    # {
    #   "id": 39,
    #   "setup": "What do you get when you cross a ghost with a bee?",
    #   "punchline": "Boo-bees!"
    # },
    # {
    #   "id": 40,
    #   "setup": "What's a ghost's favorite medication?",
    #   "punchline": "Boo-profin!"
    # },
    # {
    #   "id": 41,
    #   "setup": "How do ghosts sign their emails?",
    #   "punchline": "Best frights!"
    # },
    # {
    #   "id": 42,
    #   "setup": "What's a ghost's favorite vegetable?",
    #   "punchline": "Boo-ccoli!"
    # },
    # {
    #   "id": 43,
    #   "setup": "How do ghosts send messages?",
    #   "punchline": "By scare-mail!"
    # },
    # {
    #   "id": 44,
    #   "setup": "What's a ghost's favorite cookie?",
    #   "punchline": "Boo-scotti!"
    # },
    # {
    #   "id": 45,
    #   "setup": "What do you call a ghost's favorite pastime?",
    #   "punchline": "BOO-ling!"
    # },
    # {
    #   "id": 46,
    #   "setup": "What does a ghost wear to bed?",
    #   "punchline": "Boo-jamas!"
    # },
    # {
    #   "id": 47,
    #   "setup": "What do you call a ghost chef?",
    #   "punchline": "A booker!"
    # },
    # {
    #   "id": 48,
    #   "setup": "What's a ghost's favorite movie?",
    #   "punchline": "The Blair Witch Boo-ject!"
    # },
    # {
    #   "id": 49,
    #   "setup": "Why are ghosts bad at lying?",
    #   "punchline": "Because you can see right through them!"
    # },
    # {
    #   "id": 50,
    #   "setup": "What do you call a ghost comedian?",
    #   "punchline": "A real scream!"
    # },
    {"id": "1", "setup": "Why did the ghost go to the party?", "punchline": "Because he heard it was going to be a boo-last!"},
    {"id": "2", "setup": "What does a panda ghost eat?", "punchline": "Bamboo!"},
    {"id": "3", "setup": "What do you call a ghost comedian?", "punchline": "A boo-mer!"},
    {"id": "4", "setup": "Why did the ghost break up with his girlfriend?", "punchline": "She said he was too boo-ring!"},
    {"id": "5", "setup": "What’s a ghost’s favorite kind of fruit?", "punchline": "Boo-berries!"},
    {"id": "6", "setup": "Why did the ghost go into the bar?", "punchline": "For the boos!"},
    {"id": "7", "setup": "What do you say when you surprise a ghost?", "punchline": "Boo-hoo!"},
    {"id": "8", "setup": "Why don’t ghosts make good cheerleaders?", "punchline": "Because they always say boo!"},
    {"id": "9", "setup": "What do you call a ghost detective?", "punchline": "Sherlock Boo-lmes!"},
    {"id": "10", "setup": "Why did the ghost get a ticket?", "punchline": "He was caught boo-speeding!"},
    {"id": "11", "setup": "What do ghosts put in their coffee?", "punchline": "Boo-cream!"},
    {"id": "12", "setup": "What do you call a ghost who loves classical music?", "punchline": "Boo-thoven!"},
    {"id": "13", "setup": "What’s a ghost’s favorite exercise?", "punchline": "Boo-t camp!"},
    {"id": "14", "setup": "Why do ghosts hate the rain?", "punchline": "It dampens their spirits!"},
    {"id": "15", "setup": "What do you call a ghost’s favorite dessert?", "punchline": "Boo-lé!"},
    {"id": "16", "setup": "What’s a ghost’s favorite ride at the amusement park?", "punchline": "The roller-boo-ster!"},
    {"id": "17", "setup": "Why did the ghost go to school?", "punchline": "To improve his boo-cabulary!"},
    {"id": "18", "setup": "What do you call a haunted chicken?", "punchline": "Poultrygeist!"},
    {"id": "19", "setup": "What’s a ghost’s favorite game?", "punchline": "Hide and shriek!"},
    {"id": "20", "setup": "Why did the ghost take the elevator?", "punchline": "Because it was a boo-st!"},
    {"id": "21", "setup": "Why did the ghost get kicked out of the theater?", "punchline": "He kept yelling ‘Boo!’"},
    {"id": "22", "setup": "What do you call a sad ghost?", "punchline": "A boo-hoo!"},
    {"id": "23", "setup": "What’s a ghost’s favorite bedtime story?", "punchline": "Boo-ty and the Beast!"},
    {"id": "24", "setup": "Why do ghosts love elevators?", "punchline": "They lift their spirits!"},
    {"id": "25", "setup": "What’s a ghost’s favorite instrument?", "punchline": "The boo-kulele!"},
    {"id": "26", "setup": "What do you call a ghost in a rock band?", "punchline": "Boo Jovi!"},
    {"id": "27", "setup": "Why don’t ghosts like rain?", "punchline": "Because it gives them chills!"},
    {"id": "28", "setup": "What’s a ghost’s favorite social media platform?", "punchline": "Boo-ker!"},
    {"id": "29", "setup": "Why did the ghost fail math?", "punchline": "He couldn’t count on his fingers!"},
    {"id": "30", "setup": "Why do ghosts hate the wind?", "punchline": "Because it blows them away!"},
    {"id": "31", "setup": "What’s a ghost’s favorite party activity?", "punchline": "Boo-loon animals!"},
    {"id": "32", "setup": "What do you call a ghost’s autobiography?", "punchline": "Boo-ography!"},
    {"id": "33", "setup": "What do you call a ghost’s dream job?", "punchline": "A boo-siness owner!"},
    {"id": "34", "setup": "What’s a ghost’s favorite winter sport?", "punchline": "Boo-bogganing!"},
    {"id": "35", "setup": "Why did the ghost become a stand-up comedian?", "punchline": "He was great at boo-sting the crowd!"},
    {"id": "36", "setup": "What do you call a fashionable ghost?", "punchline": "Boo-tique shopper!"},
    {"id": "37", "setup": "What’s a ghost’s favorite exercise?", "punchline": "Boo-ty squats!"},
    {"id": "38", "setup": "Why do ghosts hate spicy food?", "punchline": "Because it gives them the chills!"},
    {"id": "39", "setup": "What do ghosts do before eating dinner?", "punchline": "They say ‘Boo-n Appétit!’"},
    {"id": "40", "setup": "What’s a ghost’s favorite romantic movie?", "punchline": "Casperablanca!"},
    {"id": "41", "setup": "Why don’t ghosts use elevators?", "punchline": "They prefer to take the scare-case!"},
    {"id": "42", "setup": "What’s a ghost’s favorite cereal?", "punchline": "Boo-berry crunch!"},
    {"id": "43", "setup": "What do ghosts do at the gym?", "punchline": "Boo-ty building!"},
    {"id": "44", "setup": "Why did the ghost sit alone at lunch?", "punchline": "He was a little boo-shy!"},
    {"id": "45", "setup": "What’s a ghost’s favorite type of music?", "punchline": "Boo-gie woogie!"},
    {"id": "46", "setup": "Why did the ghost refuse to fight?", "punchline": "He didn’t have the guts!"},
    {"id": "47", "setup": "What do ghosts wear in the rain?", "punchline": "Boo-ts!"},
    {"id": "48", "setup": "Why don’t ghosts like shopping?", "punchline": "Too many hidden fees!"},
    {"id": "49", "setup": "What do ghosts order at fast food places?", "punchline": "Boo-gers and fries!"},
    {"id": "50", "setup": "What’s a ghost’s favorite kind of dance?", "punchline": "The boo-gie! "}
]


def tell_a_boo_joke():
    joke = random.choice(jokes)
    print(f"{joke['setup']}")
    time.sleep(2.5)
    print(f"{joke['punchline']}")







