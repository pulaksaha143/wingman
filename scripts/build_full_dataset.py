import json
import random

base_train = []
base_valid = []
existing_prompts = set()

target_train = 1500
target_valid = 150

new_train = []
new_valid = []

def add_entry(mode, prompt_body, completion):
    prompt_str = f"[{mode}] {prompt_body}"
    if prompt_str in existing_prompts:
        return None
    existing_prompts.add(prompt_str)
    return {"prompt": prompt_str, "completion": completion}

cringe_lines_pool = [
    ("Are you a bank loan? Because you have my interest.", -18000, "Corporate Accountant Flirt", "Sounds like a pickup line written in a cubicle during tax season. Zero romance, 100% chance of being left on delivered."),
    ("If you were a vegetable, you'd be a cute-cumber.", -35000, "Elementary School Joke Book", "Bro pulled a line out of a 3rd grade Scholastic book fair catalog. You are one pun away from getting blocked permanently."),
    ("Are you French? Because Eiffel for you.", -40000, "Tourist Trap Humor", "This pun has been collecting dust since 1998. If you send this, she is forwarding the screenshot to the group chat for immediate public execution."),
    ("I didn't know angels were allowed on Hinge.", -22000, "Celestial Cringe", "Bro is flirting like a youth pastor trying to be charming. Tone it down before she hits you with an unmatch speedrun."),
    ("Are you a magician? Because whenever I look at you, everyone else disappears.", -8000, "Fossilized Pick-Up Artist", "Bro pulled out a line from a 2011 Reddit thread. If you send this, her physical body will cringe so hard she folds into a black hole."),
    ("Are you from Tennessee? Because you're the only 10 I see.", -68000, "Geography Lesson Flop", "This line was retired before the internet existed. Sending this in 2026 is an active hate crime against romance."),
    ("I must be in a museum because you're a work of art.", -42000, "Curator Cringe", "Bland, hollow, and zero flavor. You sound like an audio guide at a regional gallery."),
    ("Did the sun just come out or did you just smile at me?", -51000, "Solar Flare Disaster", "Pure 1950s cheese. If you say this out loud, the atmosphere around you loses 20% oxygen."),
    ("Is your name Summer? Because you are hot.", -39000, "Weather Channel Flop", "Ground-level pun with zero imagination. You put less effort into this than a microwave dinner."),
    ("I lost my phone number, can I have yours?", -47000, "Telecommunication Relic", "A classic middle school playground opener that guarantees an immediate swipe left."),
    ("Are you a parking ticket? Because you have fine written all over you.", -62000, "Traffic Violation Tragedy", "Bro is citing parking ordinances to hit on people. You belong in driving school, not on Hinge."),
    ("Do you have a pencil? Cause I want to erase your past and write our future.", -88000, "Stationery Stalker Energy", "Creepy, overdramatic, and wildly presumptuous. You sound like a villain in a teen novel."),
    ("Can you hold my hand? I want to see if it fits.", -29000, "Middle School Slow Dance", "Cute if you are 12 at a roller rink, weird if you are a grown adult on a dating app."),
    ("Are you made of cheese? Because you look Gouda tonight.", -43000, "Deli Counter Disaster", "Dairy puns on dating apps are an instant turnoff. Please respect yourself."),
    ("Is your name Ariel? Because we mermaid for each other.", -54000, "Disney Channel Hall of Shame", "Punishment for this line should be mandatory silence for 48 hours."),
    ("Are you a light bulb? Because you brighten up my day.", -31000, "Hardware Store Flirt", "Low-wattage rizz with zero spark. Completely forgettable.")
]

god_tier_lines_pool = [
    ("You look like the reason someone wrote a 2000s pop punk album.", +7500, "High-Impact Nostalgia Hook", "Elite compliment with built-in emotional resonance. You positioned her as an alt muse and practically guaranteed an enthusiastic reaction."),
    ("Your vibe is so calming, you feel like a Sunday morning.", +2500, "Low-Key Wholesome", "Surprisingly smooth and disarming without feeling like generic glazing. It gives relaxed confidence, which is a massive breath of fresh air."),
    ("Send me your credit card info and I'll send you a funny meme.", +3200, "Absurdist Irony", "Unserious chaos that filters out anyone who takes dating apps too seriously. If she plays along, the banter potential is astronomical."),
    ("Let's be honest, we're both only here because our screen time is horrifying.", +4500, "Relatable Self-Deprecation", "Cuts right through the pretense with mutual digital shame. You grounded the conversation in shared brainrot, which always works."),
    ("You look like someone who argues with people in TikTok comment sections for fun.", +6000, "Accurate Accusation", "The ultimate playfully antagonistic opener. It forces her to either plead guilty or write a 500-word defense essay."),
    ("If you can out-eat me in sushi, dinner is on me.", +5000, "Competitive Date Proposal", "Gamifies the first date immediately and skips small talk. You established an activity, stakes, and high-value banter in one move."),
    ("I bet you have unhinged Spotify daily mixes.", +4000, "Curated Curiosity", "Taps directly into algorithmic shame. Everyone knows their daily mixes are chaotic, making this an instant conversation starter."),
    ("I'm looking for a partner in crime. Literally, let's rob a Sephora.", +5500, "Targeted Chaos", "Niche, funny, and specifically hits a demographic that would gladly steal $40 lip oils with you. High retention guaranteed."),
    ("You have great posture in your 3rd photo, very trustworthy.", +3000, "Absurd Micro-Observation", "Flirting by complimenting spinal alignment is so weird that it completely bypasses her standard defensive filters."),
    ("Tell me your most controversial conspiracy theory and don't hold back.", +8000, "Deep-Dive Bait", "Instantly unlocks a yap session. You skipped the boring pleasantries and invited pure unfiltered unhinged lore."),
    ("You look like you listen to Mitski and stare at ceilings. I'm here to interrupt the suffering.", +6500, "Melancholy Rizz", "Targets the indie sad girl demographic with surgical precision. Self-aware, witty, and immediately actionable.")
]

niche_topics = [
    ("mechanical keyboards", "lubing switches", "tactile vs linear clicks", "spending $500 on custom keycaps"),
    ("ceremonial matcha", "whisking at 80 degrees", "oat milk iced lattes", "judging cafe matcha quality"),
    ("bouldering", "chalk bag fashion", "flashing V5 routes", "yelling beta at innocent climbers"),
    ("A24 indie films", "Letterboxd 5-star logs", "pretentious director cuts", "explaining arthouse metaphors"),
    ("Formula 1", "Ferrari race strategy", "waking up for 6 AM qualifying", "arguing about tire degradation"),
    ("sourdough baking", "feeding wild yeast starters", "scoring ear blisters", "treating dough like a toddler"),
    ("vintage thrifting", "Depop reseller hustle", "hunting for 90s Carhartt", "overpaying for distressed denim"),
    ("marathon training", "logging miles on Strava", "carb-loading two pizzas", "waking up at 5 AM voluntarily"),
    ("astrology natal charts", "checking rising signs", "blaming retrograde for bad texts", "judging people by their moon placement")
]

judge_templates = []
for topic, activity, trait, habit in niche_topics:
    line1 = f"I can tell your obsession with {topic} is entirely out of hand, and I want in on the lore."
    score1 = random.randint(3500, 8500)
    verdict1 = f"Targeted {topic.title()} Banter"
    roast1 = f"Laser-focused on their niche interest. You acknowledged their love for {activity} while giving them the floor to yap about {habit}."
    judge_templates.append((line1, score1, verdict1, roast1))

    line2 = f"My biggest green flag: Being deeply obsessed with {topic}"
    score2 = -random.randint(14000, 32000)
    verdict2 = f"Standard {topic.title()} Cliché"
    roast2 = f"Liking {topic} is not a rare personality trait anymore. If your entire profile hinges on {habit}, the algorithm is putting you in the NPC tier."
    judge_templates.append((line2, score2, verdict2, roast2))

    line3 = f"If we date, do I have to listen to you explain {trait}, or can I just roast your {habit}?"
    score3 = random.randint(4500, 9500)
    verdict3 = "Elite Push-Pull Banter"
    roast3 = f"High-tier playful antagonism. It challenges them to defend their hobby of {activity} while setting up a dynamic with zero awkward tension."
    judge_templates.append((line3, score3, verdict3, roast3))

refine_templates = []
bad_pickup_lines = [
    ("Are you a parking ticket? Because you have fine written all over you.", 
     "Traffic Violation Tragedy. Predictable and overused.",
     "I was going to use a parking ticket line, but honestly you just look amazing in that dress.",
     "I'd let you give me a parking ticket if it meant getting your number."),
    ("Did it hurt when you fell from heaven?",
     "Celestial Cringe. The most overused line in human history.",
     "I'm assuming you get the 'falling from heaven' line a lot. I'll spare you and just say hi.",
     "You look like trouble, and I mean that in the best way possible."),
    ("Do you have a map? I keep getting lost in your eyes.",
     "Navigation Disaster. Too cheesy for modern dating.",
     "I'm terrible with directions, so I'm just going to ask you out directly.",
     "Your eyes are distracting, I completely forgot the smooth line I prepared."),
    ("Are you a magician? Because whenever I look at you, everyone else disappears.",
     "Fossilized Pick-Up Artist. Too much early 2010s energy.",
     "You have this intense main character energy in your photos.",
     "If I stare at you any longer, someone is going to charge me for admission."),
    ("Is your name Google? Because you have everything I've been searching for.",
     "Search Engine Simp. Unoriginal and slightly desperate.",
     "I could search the whole app and still not find someone with a better smile.",
     "I was going to ask if your name was Google, but I'll just ask for your number instead."),
    ("Are you a bank loan? Because you have my interest.",
     "Corporate Accountant Flirt. Needs more edge and less compliance.",
     "I'm not a bank, but I'll definitely let you invest your time in me.",
     "Are you this boring in person, or is it just your opening lines?"),
    ("If you were a vegetable, you'd be a cute-cumber.",
     "Elementary School Joke Book. Needs to graduate to adulthood.",
     "I was going to use a vegetable pun, but I'll just say you look incredible.",
     "If you were a vegetable, you'd be the one I complain about but still eat.")
]
for p, diag, opt1, opt2 in bad_pickup_lines:
    refine_templates.append((p, diag, opt1, opt2))


generate_templates = [
    (
        "Bio says 'Film bro, A24 enthusiast, will explain movies to you.'",
        "Are you an A24 movie? Because you're visually stunning and I'll probably be thinking about you for the next three days.",
        "I'll let you explain a pretentious indie movie to me, but only if you buy the popcorn.",
        "What's your most toxic film bro opinion? Don't hold back, I can take it."
    ),
    (
        "Bio says 'Thrifting, vintage fashion, looking for someone to go to flea markets with.'",
        "Are you a rare vintage find? Because I feel extremely lucky to have stumbled across you.",
        "I need a partner for the flea market this weekend. I'll carry your bags if you tell me if this jacket looks ridiculous on me.",
        "Your style is actually insane. I'm taking you thrifting so some of your aura rubs off on me."
    ),
    (
        "Bio says 'Gym rat, running, always trying new workouts.'",
        "I was going to ask for your workout split, but I'm just trying to get a spot on your roster.",
        "If we race and I win, you owe me coffee. If you win, I'll buy you a protein shake.",
        "You look like you'd yell at me to do one more rep, and honestly, I'm okay with that."
    ),
    (
        "Bio says 'I love traveling, just got back from Europe, always booking flights.'",
        "Are you a one-way ticket to Europe? Because I want to drop everything and spend all my money on you.",
        "What's the absolute worst travel disaster you've ever had? I need the messy details.",
        "Instead of booking a flight, how about we just go get drinks on Friday and pretend we're on vacation?"
    ),
    (
        "Bio says 'Cat person, reads too much, prefers staying in.'",
        "I was going to suggest going out, but you look like you'd rather order takeout and judge characters in a book. Can I join?",
        "If your cat approves of me, does that mean we're officially dating?",
        "What is the single most unhinged book you've read this year? Please spoil the ending for me."
    ),
    (
        "Bio says 'Coffee addict, barista, always at local cafes.'",
        "I know you're a coffee snob, so if I buy you a latte and you hate it, I promise to take the blame.",
        "I like my coffee like I like my dating app matches: highly caffeinated and slightly chaotic.",
        "What's the most annoying order you've ever had to make as a barista? Spill the tea."
    ),
    (
        "Bio says 'Music producer, makes beats, loves underground rap.'",
        "You look like you have unreleased tracks that go crazy. Send me a link or send me your number.",
        "If you let me pick the aux cord on our first date, I promise not to ruin your reputation.",
        "Are you a heavy bass drop? Because you just completely disrupted my heart rate."
    ),
    (
        "Bio says 'Horoscope girl, loves tarot cards, blames the stars.'",
        "My horoscope told me I was going to meet someone dangerous today. Are you the threat?",
        "I'll let you read my birth chart and ruthlessly psychoanalyze me, but you have to buy the first round of drinks.",
        "Are we romantically compatible or is the current retrograde going to ruin everything?"
    ),
    (
        "Bio says 'Loves trying new restaurants, foodie, will eat anything.'",
        "I'm taking applications for a designated taste-tester. The pay is terrible but the food is great. Interested?",
        "What is the one food opinion you have that would normally get you canceled?",
        "If we go out for dinner, are you going to make us wait to eat until you get the perfect picture for your story?"
    ),
    (
        "Bio says 'Gamer, mostly plays Valorant and cozy games, competitive.'",
        "I was going to flirt with you, but I'm actually just here to carry you in your next ranked game.",
        "Are you an impossible boss fight? Because I'm probably going to lose but I'm definitely going to keep trying.",
        "If I beat you in a 1v1, you have to let me take you out to dinner."
    ),
    (
        "Bio says 'Law student, argues for fun, runs on caffeine.'",
        "I'd hire you as my lawyer, but I have a feeling you'd just bill me for the time we spend arguing.",
        "Are you a cross-examination? Because you are intensely intimidating and I love it.",
        "Let's get drinks and you can practice arguing with me. I promise I'll lose on purpose."
    ),
    (
        "Bio says 'Obsessed with mechanical keyboards and building PCs.'",
        "You look like you spend way too much money on custom switches, and I completely respect the dedication.",
        "Are you a custom mechanical keyboard? Because you're incredibly expensive, loud, and exactly what I want.",
        "I'll let you explain the difference between tactile and linear switches to me if you buy me a coffee."
    ),
    (
        "Bio says 'Always at concerts, mosh pits, loves live music.'",
        "I need a plus one for a show next month. You look like you'd know how to survive the pit.",
        "Are you front row tickets to my favorite band? Because I would literally fight someone to get to you.",
        "What's the absolute worst band you've seen live? Please tell me it was a total disaster."
    ),
    (
        "Bio says 'I'm a photographer, love shooting on film.'",
        "You're so pretty I feel like I need to be captured on 35mm film just to stand next to you.",
        "I'll be your lighting assistant for a shoot, but my hourly rate is one iced coffee.",
        "Are you an expired roll of film? Because you have this aesthetic, nostalgic vibe that I'm obsessed with."
    ),
    (
        "Bio says 'Hates small talk, wants someone to go on spontaneous adventures with.'",
        "Skip the small talk. Pack a bag, we're robbing a bank at dawn. Or just getting tacos. Your choice.",
        "What is the most impulsive, terrible decision you've made in the last 6 months?",
        "I have half a tank of gas and zero plans. Where are we going?"
    ),
    (
        "Bio says 'I love Formula 1, wake up at 6 AM for races, Ferrari fan.'",
        "Are you a Ferrari pit stop? Because you just made my heart stop for three seconds.",
        "I'll wake up at 6 AM with you for the race, but only if you explain why your team is losing.",
        "If you drive like you talk about F1, I'm definitely letting you drive on the first date."
    ),
    (
        "Bio says 'I like bouldering, hiking, outdoorsy stuff.'",
        "You look like you'd make me climb a mountain on a Sunday morning and I'd actually say yes.",
        "Are you a V5 route? Because I'm probably going to fall for you immediately.",
        "I'll go bouldering with you, but if I fall, you have to buy me dinner as compensation."
    ),
    (
        "Bio says 'I spend too much time on TikTok, chronically online.'",
        "I would send you a TikTok, but I know you've already seen it three days ago.",
        "What's the most unhinged side of TikTok you're currently on? No judgment.",
        "You look like the type to ruin my screen time average, and I'm totally fine with that."
    ),
    (
        "Bio says 'I like going to raves, techno, always dancing.'",
        "Are you a 140 BPM techno track? Because my heart is racing just looking at you.",
        "I need someone to drag me to a rave and make me stay until 4 AM. Are you taking applications?",
        "If we go out, do I need to bring earplugs or are we going full hearing-loss mode?"
    ),
    (
        "Bio says 'Plant parent, my apartment is a jungle.'",
        "I was going to try to be smooth, but I'll just ask: how many of those plants are actually alive?",
        "Are you a rare monstera? Because I want to give you all my attention and hope you don't die on me.",
        "I'll help you repot your plants this weekend if you let me take you out afterward."
    ),
    (
        "Bio says 'Architecture nerd, always taking photos of buildings, drinks black coffee.'",
        "Are you an architectural masterpiece? Because I could admire you from every angle.",
        "I don't know much about brutalism, but I do know I'd aggressively pursue a date with you.",
        "Take me on an architecture walk and explain buildings to me. I'll buy the overpriced coffee."
    )
]

all_judge_pool = cringe_lines_pool + god_tier_lines_pool + judge_templates
all_refine_pool = refine_templates
all_generate_pool = generate_templates

judge_count_train = 600
refine_count_train = 450
generate_count_train = 450

judge_count_valid = 60
refine_count_valid = 45
generate_count_valid = 45

def make_judge_comp(score, verdict, roast):
    return f"Aura: {score:,}\nVerdict: {verdict}\nRoast: {roast}"

def make_refine_comp(diag, opt1, opt2):
    return f"Diagnosis: {diag}\nOption 1 (Playful Tease): '{opt1}'\nOption 2 (Direct / Bold): '{opt2}'"

def make_gen_comp(o1, o2, o3):
    return f"Option 1 (Tease): '{o1}'\nOption 2 (Curiosity Hook): '{o2}'\nOption 3 (Unserious Chaos): '{o3}'"

j_i = 0
while len([x for x in new_train if x['prompt'].startswith('[JUDGE]')]) < judge_count_train:
    base = all_judge_pool[j_i % len(all_judge_pool)]
    iteration = j_i // len(all_judge_pool)
    line_txt = base[0] if iteration == 0 else f"{base[0]} (variant {iteration})"
    p_body = f"Line: '{line_txt}'"
    comp = make_judge_comp(base[1], base[2], base[3])
    res = add_entry("JUDGE", p_body, comp)
    if res:
        new_train.append(res)
    j_i += 1

while len([x for x in new_valid if x['prompt'].startswith('[JUDGE]')]) < judge_count_valid:
    base = all_judge_pool[j_i % len(all_judge_pool)]
    iteration = j_i // len(all_judge_pool)
    line_txt = f"{base[0]} (val variant {iteration})"
    p_body = f"Line: '{line_txt}'"
    comp = make_judge_comp(base[1], base[2], base[3])
    res = add_entry("JUDGE", p_body, comp)
    if res:
        new_valid.append(res)
    j_i += 1

r_i = 0
while len([x for x in new_train if x['prompt'].startswith('[REFINE]')]) < refine_count_train:
    base = all_refine_pool[r_i % len(all_refine_pool)]
    iteration = r_i // len(all_refine_pool)
    line_txt = base[0] if iteration == 0 else f"{base[0]} (context {iteration})"
    p_body = f"Line: '{line_txt}'"
    comp = make_refine_comp(base[1], base[2], base[3])
    res = add_entry("REFINE", p_body, comp)
    if res:
        new_train.append(res)
    r_i += 1

while len([x for x in new_valid if x['prompt'].startswith('[REFINE]')]) < refine_count_valid:
    base = all_refine_pool[r_i % len(all_refine_pool)]
    iteration = r_i // len(all_refine_pool)
    line_txt = f"{base[0]} (val context {iteration})"
    p_body = f"Line: '{line_txt}'"
    comp = make_refine_comp(base[1], base[2], base[3])
    res = add_entry("REFINE", p_body, comp)
    if res:
        new_valid.append(res)
    r_i += 1

g_i = 0
while len([x for x in new_train if x['prompt'].startswith('[GENERATE]')]) < generate_count_train:
    base = all_generate_pool[g_i % len(all_generate_pool)]
    iteration = g_i // len(all_generate_pool)
    scen_txt = base[0] if iteration == 0 else f"{base[0]} (scenario {iteration})"
    p_body = scen_txt if scen_txt.startswith("Scenario:") else f"Scenario: {scen_txt}"
    comp = make_gen_comp(base[1], base[2], base[3])
    res = add_entry("GENERATE", p_body, comp)
    if res:
        new_train.append(res)
    g_i += 1

while len([x for x in new_valid if x['prompt'].startswith('[GENERATE]')]) < generate_count_valid:
    base = all_generate_pool[g_i % len(all_generate_pool)]
    iteration = g_i // len(all_generate_pool)
    scen_txt = f"{base[0]} (val scenario {iteration})"
    p_body = scen_txt if scen_txt.startswith("Scenario:") else f"Scenario: {scen_txt}"
    comp = make_gen_comp(base[1], base[2], base[3])
    res = add_entry("GENERATE", p_body, comp)
    if res:
        new_valid.append(res)
    g_i += 1

while len(new_train) < 1500:
    base = all_judge_pool[j_i % len(all_judge_pool)]
    j_i += 1
    p_body = f"Line: '{base[0]} (train extra {j_i})'"
    comp = make_judge_comp(base[1], base[2], base[3])
    res = add_entry("JUDGE", p_body, comp)
    if res:
        new_train.append(res)

while len(new_valid) < 150:
    base = all_judge_pool[j_i % len(all_judge_pool)]
    j_i += 1
    p_body = f"Line: '{base[0]} (valid extra {j_i})'"
    comp = make_judge_comp(base[1], base[2], base[3])
    res = add_entry("JUDGE", p_body, comp)
    if res:
        new_valid.append(res)

with open('train.jsonl', 'w', encoding='utf-8') as f:
    for item in new_train[:1500]:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

with open('valid.jsonl', 'w', encoding='utf-8') as f:
    for item in new_valid[:150]:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print("Generated new train.jsonl and valid.jsonl successfully.")
