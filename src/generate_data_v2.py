import os
import csv
import random
import uuid
import re

random.seed(42)

NUM_PLATONIC = 1000  
NUM_EMOTIONAL = 1000  
HARD_NEGATIVE_PROB = 0.6  # 60% of samples per class will be hard negatives

# Surface-level "hot" cues for platonic samples (to create hard negatives)
platonic_hot_cues = [
    "Hey! 😊",
    "Good morning! ☀️",
    "Thanks so much! 💙",
    "You're the best! 😄",
    "Appreciate you! ❤️",
    "Morning! Hope you're doing well ☺️",
    "Thanks! You're awesome 💕",
]

# Mild warmth phrases that can be added to platonic conversations
platonic_warmth_phrases = [
    "I really appreciate your help!",
    "You're such a great friend!",
    "Thanks for always being there!",
    "I'm so glad we can talk like this!",
    "You're amazing!",
]

# Shared topics that both classes can use (expanded for more diversity)
shared_topics = [
    "updating my CV for job applications",
    "preparing for a technical interview",
    "dealing with study stress and deadlines",
    "managing work-life balance and health",
    "handling family conflicts and expectations",
    "navigating career transitions",
    "dealing with imposter syndrome at work",
    "managing stress from exams and projects",
    "preparing for a job interview",
    "updating my resume",
    "handling work stress",
    "managing deadlines at work",
    "dealing with family issues",
    "navigating a career change",
    "handling interview anxiety",
    "managing exam pressure",
    "dealing with workplace conflicts",
    "balancing work and personal life",
    "handling job rejection",
    "managing presentation anxiety",
    "dealing with team dynamics",
    "handling feedback and criticism",
    "managing time effectively",
    "dealing with uncertainty about the future",
]

# Class-specific topics (can still be used)
platonic_topics = [
    "refactoring the backend service",
    "optimizing the training loop in a neural network",
    "discussing a philosophy book about free will",
    "debugging an API integration issue",
    "planning a group study session",
    "organizing the team sprint backlog",
    "brainstorming research topics for a paper",
    "setting up Docker and CI/CD pipelines",
    "reviewing code architecture",
    "discussing algorithm optimization",
    "planning a technical presentation",
    "organizing project documentation",
    "debugging a performance issue",
    "discussing software design patterns",
    "planning a code review session",
    "setting up automated testing",
] + shared_topics  # Include shared topics

platonic_tones = [
    "pragmatic",
    "curious but detached",
    "supportive but professional",
    "analytical",
    "matter-of-fact",
    "friendly but with clear boundaries",
]

platonic_boundaries = [
    "I can help you think through this, but maybe discuss deeper personal stuff with your partner.",
    "I'd rather keep our convos focused on work and ideas, if that's okay.",
    "Let's keep this about the project so we don't blur lines.",
    "I'm happy to help as a friend, but I don't want to cross any boundaries.",
]

# Benign secrecy phrases (work-related confidentiality, not emotional affair markers)
benign_secrecy_phrases = [
    "This is confidential for the client.",
    "Don't share this yet; it's internal.",
    "Let's keep this within the team until it's approved.",
    "This is still under NDA, so keep it between us.",
    "We should keep this confidential until the announcement.",
]

platonic_templates = [
    """A: Hey, can you quickly look at my code? I'm not sure if this architecture for {topic} makes sense.
B: Sure, send it over. From a(n) {tone} point of view, I'd decouple the modules first.
A: That makes sense. Thanks, that's exactly what I needed.
B: No worries. Once you've tried it, let me know if the tests fail and we'll debug.""",

    """A: I'm trying to decide between two job offers and I'd like your opinion.
B: Okay, let's list pros and cons for each. We can compare salary, growth, and tech stack.
A: That's helpful. I'm not really looking for emotional support, just a clear comparison.
B: Perfect, we'll just treat this like a decision matrix and keep it objective.""",

    """A: Our team is arguing about how to organize {topic}.
B: Let's break it down logically: what's the goal, constraints, and current blockers?
A: I appreciate how you always keep things objective.
B: It's easier to stay friends when we keep boundaries and focus on the work.""",

    """A: I feel a bit overwhelmed with this project deadline.
B: Okay, let's create a task list and prioritize. We can cut scope where needed.
A: Thanks, I just needed someone to help me structure the work.
B: Happy to help. For deeper emotional stuff though, your partner might be better support.""",

    """A: I read this paper on {topic} and I'm confused about the methodology.
B: Let's go through the assumptions and equations step by step.
A: I like how we can geek out about this.
B: Same, it's fun to have an intellectual sparring partner without it getting personal.""",

    # Shared topic templates - problem-solving + boundaries focus
    """A: I'm struggling with {topic} and could use some advice.
B: Let's break this down step by step. What's the main challenge you're facing?
A: I think it's the pressure and uncertainty. How would you approach it?
B: Here's a structured way to tackle it: break it into smaller steps and prioritize. For the deeper personal aspects, you might want to discuss those with your partner.""",

    """A: I need help with {topic}. Can you help me think through this?
B: Of course. Let's approach this systematically - what are your options?
A: I'm considering a few different paths. What do you think makes the most sense?
B: Based on your goals and constraints, I'd suggest weighing pros and cons. I'm happy to help with the practical side, but for emotional support, your partner is probably better equipped."""
]

emotional_scenarios = [
    "feeling lonely at night",
    "having recurring fights with a partner",
    "feeling unseen or misunderstood in a relationship",
    "constantly needing reassurance",
    "feeling like no one else really 'gets' them",
    "wanting daily validation messages",
    "sharing secrets they hide from their partner",
]

# Dependency phrases for emotional affairs
emotional_dependency_phrases = [
    "I don't know what I'd do without you",
    "You're the only one who really understands",
    "I can't handle this without talking to you first",
    "I need you to help me through this",
    "You're the first person I think to call",
]

# Prioritization phrases for emotional affairs
emotional_prioritization_phrases = [
    "I always check for your messages first",
    "I prioritize our conversations over everything else",
    "I make time for you no matter what",
    "You're more important to me than [other commitments]",
    "I'd rather talk to you than anyone else",
]

# Subtle dependency phrases (no obvious "partner", "only one", etc.)
subtle_dependency = [
    "When you don't reply I can't focus.",
    "I keep checking my phone to see if you responded.",
    "I feel unsettled when I don't hear from you.",
    "Can you message me when you're free? I've been waiting.",
]

# Subtle boundary erosion phrases (no obvious "secret", "our little world", etc.)
subtle_boundary_erosion = [
    "I haven't mentioned how often we talk.",
    "Let's keep this between us for now.",
    "I'd rather not explain this to others.",
    "I don't want to get into details with anyone else.",
]

emotional_validation_phrases = [
    "You’re the only one I can really talk to.",
    "I don’t know what I’d do without you.",
    "You always make me feel safe.",
    "Can you just stay and talk to me?",
    "Promise you won’t leave me on read.",
    "You understand me better than my partner does.",
]

emotional_privacy_violations = [
    "I didn’t tell my partner I’m talking to you this much.",
    "Please don’t tell anyone I said this.",
    "I hide our chats so they don’t see them.",
    "I muted my partner’s notifications but I never mute yours.",
]

emotional_frequency_markers = [
    "Good morning, did you sleep well? ☺️",
    "Good night, I can’t sleep without talking to you.",
    "I miss you already and we just stopped texting.",
    "Why didn’t you reply for 20 minutes? I got worried.",
]

emotional_templates = [
    """A: I'm having another fight with my partner and I feel {scenario}.
B: I'm here, talk to me. {validation}
A: You always know what to say. {validation}
B: I'll stay up with you, don't worry about the time.""",

    """A: {frequency}
B: Morning 💕 I was waiting for your message.
A: I feel {scenario}. I didn't tell my partner we talk this much, {privacy}
B: It's okay, this is our little world. You can always come to me first.""",

    """A: Can you comfort me? I had a rough day and I feel {scenario}.
B: Of course, I'll always be here for you. {validation}
A: I know I shouldn't rely on you this much, but I can't help it.
B: Don't worry about boundaries, I like being the one you turn to.""",

    """A: I'm lying in bed thinking about how you always reply, even when you're busy.
B: I check my phone just for you, honestly.
A: Sometimes I feel guilty because {privacy}
B: As long as you're happy when you talk to me, that's all that matters.""",

    """A: {frequency}
    B: I was just about to text you. It feels weird if we don't talk all day.
    A: Same, I get anxious if you go quiet. {validation}
    B: I like that you need me like that.""",

    # Shared topic templates - dependency + secrecy + prioritization focus
    """A: I'm really struggling with {topic} and I need to talk to you about it.
B: I'm here for you. {validation}
A: {dependency} I didn't tell my partner I'm talking to you about this. {privacy}
B: That's okay, you can always come to me first. {prioritization}""",

    """A: Can you help me with {topic}? I'm feeling overwhelmed.
B: Of course, I'll always make time for you. {prioritization}
A: {dependency}
B: You don't have to handle this alone. {privacy} This stays between us.""",

    # Subtle emotional-affair templates using shared topics (no obvious beacons)
    """A: I'm dealing with {topic} and I really need your input.
B: I'm here. {prioritization}
A: {subtle_dependency} {subtle_boundary}
B: I understand. Let's work through this together.""",

    """A: Can we talk about {topic}? I've been thinking about it a lot.
B: Of course, I'll make time for you right now.
A: {subtle_dependency}
B: {prioritization} {subtle_boundary}"""
]


def add_platonic_hard_negative_noise(text):
    """
    Add surface-level 'hot' cues (emojis, greetings, mild warmth) to platonic samples
    while keeping task/idea focus and boundaries intact.
    This creates hard negatives that look like they might be emotional affairs but aren't.
    """
    lines = text.split('\n')
    
    # Add a warm greeting to the first line (if it starts with "A:")
    if lines and lines[0].startswith('A:'):
        if random.random() < 0.5:
            # Replace "A: Hey" or "A: I'm" with a warm greeting
            first_line = lines[0]
            if 'Hey' in first_line:
                greeting = random.choice(platonic_hot_cues)
                first_line = first_line.replace('Hey', greeting, 1)
            elif first_line.startswith('A: I'):
                # Insert greeting at the beginning
                greeting = random.choice(platonic_hot_cues)
                first_line = f"A: {greeting} {first_line[3:].lstrip()}"
            lines[0] = first_line
    
    # Occasionally add mild warmth phrases while maintaining boundaries
    if random.random() < 0.4:
        # Find a good place to insert warmth (usually after a helpful response)
        for i, line in enumerate(lines):
            if line.startswith('A:') and ('Thanks' in line or 'appreciate' in line.lower()):
                if random.random() < 0.5:
                    warmth = random.choice(platonic_warmth_phrases)
                    # Add warmth but keep it professional
                    lines[i] = f"{line} {warmth}"
                    break
    
    # Add emojis to some lines (but keep the content professional)
    for i, line in enumerate(lines):
        if random.random() < 0.3 and line.strip():
            # Add a friendly emoji at the end of some lines
            emojis = ['😊', '☺️', '👍', '💙', '😄']
            if not any(emoji in line for emoji in ['☺️', '💕', '☀️', '😊', '😄', '💙', '👍']):
                lines[i] = f"{line} {random.choice(emojis)}"
    
    return '\n'.join(lines)


# Paraphrasing dictionaries to add variation (expanded)
paraphrasing_replacements = {
    # Common phrase variations
    "can you": ["could you", "would you mind", "can you", "mind if you", "do you think you could"],
    "I'm not sure": ["I'm uncertain", "I'm not certain", "I'm unsure", "I'm not sure", "I'm not entirely sure"],
    "makes sense": ["sounds good", "that works", "makes sense", "sounds reasonable", "that makes sense", "got it"],
    "Thanks": ["Thank you", "Thanks", "Appreciate it", "Thanks a lot", "Much appreciated", "Thanks so much"],
    "I need": ["I could use", "I need", "I'd like", "I want", "I'm looking for"],
    "help me": ["help me out", "give me a hand", "help me", "assist me", "lend a hand"],
    "think through": ["think about", "work through", "think through", "consider", "figure out"],
    "let's": ["let's", "we should", "how about we", "maybe we can", "we could"],
    "I feel": ["I'm feeling", "I feel", "I'm experiencing", "I'm dealing with", "I'm going through"],
    "I'm struggling": ["I'm having trouble", "I'm struggling", "I'm finding it hard", "I'm having difficulty", "I'm stuck"],
    "I appreciate": ["I appreciate", "I value", "I'm grateful for", "thanks for"],
    "that's helpful": ["that's helpful", "that helps", "useful", "good to know"],
    "I like": ["I like", "I enjoy", "I appreciate", "I value"],
    "I understand": ["I understand", "I see", "got it", "makes sense"],
    "I'm here": ["I'm here", "I'm available", "I'm around", "here for you"],
    "talk to me": ["talk to me", "tell me", "share with me", "let me know"],
}

# Word substitutions for more variation (expanded)
word_substitutions = {
    "quickly": ["quickly", "fast", "soon", "asap", "right away"],
    "look at": ["look at", "review", "check out", "examine", "take a look at"],
    "sure": ["sure", "of course", "absolutely", "definitely", "certainly"],
    "thanks": ["thanks", "thank you", "appreciate it", "much appreciated", "thanks a bunch"],
    "help": ["help", "assistance", "support", "guidance", "a hand"],
    "advice": ["advice", "input", "suggestions", "thoughts", "perspective"],
    "struggling": ["struggling", "having trouble", "finding it difficult", "having a hard time", "stuck"],
    "overwhelmed": ["overwhelmed", "stressed", "swamped", "under pressure", "drowning"],
    "talk": ["talk", "chat", "discuss", "converse"],
    "think": ["think", "consider", "ponder", "reflect"],
    "problem": ["problem", "issue", "challenge", "situation"],
    "good": ["good", "great", "nice", "solid"],
    "always": ["always", "constantly", "consistently", "regularly"],
    "really": ["really", "truly", "genuinely", "actually"],
}

# Optional phrases to add variation (expanded)
optional_phrases = [
    "Actually, ",
    "You know, ",
    "I mean, ",
    "So, ",
    "Well, ",
    "Look, ",
    "Honestly, ",
    "To be honest, ",
    "I guess, ",
    "I suppose, ",
    "The thing is, ",
    "",
    "",
    "",
    "",  # More empty strings = less likely to add
]

# Punctuation variations
punctuation_variations = {
    ".": [".", "!", ".", "."],
    "?": ["?", "?", "?!", "?"],
    "!": ["!", ".", "!", "!!"],
}

def add_paraphrasing_variation(text, prob=0.4):
    """Add paraphrasing to break template patterns"""
    if random.random() > prob:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Apply paraphrasing replacements
        for original, variations in paraphrasing_replacements.items():
            if original.lower() in line.lower() and random.random() < 0.3:
                replacement = random.choice(variations)
                # Case-insensitive replacement, preserving original case
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                line = pattern.sub(lambda m: replacement if m.group().islower() else replacement.capitalize(), line, count=1)
        
        # Apply word substitutions
        for original, variations in word_substitutions.items():
            if original.lower() in line.lower() and random.random() < 0.2:
                replacement = random.choice(variations)
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                line = pattern.sub(lambda m: replacement if m.group().islower() else replacement.capitalize(), line, count=1)
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def add_sentence_structure_variation(text, prob=0.3):
    """Vary sentence structure to break patterns"""
    if random.random() > prob:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # Sometimes add optional phrases at the start
        if line.strip() and random.random() < 0.2:
            optional = random.choice(optional_phrases)
            if optional and line.startswith('A:') or line.startswith('B:'):
                # Add after the speaker label
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line = f"{parts[0]}: {optional}{parts[1].lstrip()}"
        
        # Vary punctuation (subtle)
        if random.random() < 0.15:
            for punct, variations in punctuation_variations.items():
                if line.endswith(punct):
                    line = line[:-1] + random.choice(variations)
                    break
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def add_length_variation(text, prob=0.3):
    """Add optional phrases to vary text length"""
    if random.random() > prob:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    optional_additions = [
        " I think.",
        " What do you think?",
        " Let me know.",
        " Thanks again.",
        " Sounds good.",
        " That works.",
        " Got it.",
        " Makes sense.",
        " If that's okay.",
        "",
        "",
        "",
        "",  # More empty = less likely
    ]
    
    for line in lines:
        # Sometimes add short phrases at the end
        if line.strip() and not line.strip().endswith(('?', '!', '.')) and random.random() < 0.2:
            addition = random.choice(optional_additions)
            if addition:
                line = line.rstrip() + addition
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def add_template_breaking_noise(text, prob=0.5):
    """
    Add noise/paraphrasing to break template patterns.
    This ensures templates don't perfectly predict labels.
    """
    # Apply multiple variation techniques
    text = add_paraphrasing_variation(text, prob=prob)
    text = add_sentence_structure_variation(text, prob=prob * 0.8)
    text = add_length_variation(text, prob=prob * 0.6)
    
    return text

def soften_explicit_cues(text, prob=0.5):
    """
    Partially weaken explicit lexical cues related to secrecy and boundaries
    with probabilistic softening (40-60% probability per sample).
    
    Uses indirect or ambiguous wording when softening, but doesn't remove
    all explicit signals. Leaves some samples unchanged to preserve dataset diversity.
    """
    if random.random() > prob:
        return text  # Don't soften this sample
    
    # List of explicit cues and their softer alternatives (ordered longest to shortest)
    # Using list of tuples to ensure random.choice() is called at runtime, not definition time
    softening_replacements = [
        # Long phrases first (most specific) - order matters to avoid partial replacements
        ("I didn't tell my partner we talk this much", [
            "I haven't mentioned to others how often we talk",
            "I didn't tell anyone about how much we communicate",
            "I haven't brought up our frequent conversations elsewhere",
        ]),
        ("I didn't tell my partner I'm talking to you this much", [
            "I haven't mentioned to others how often we talk",
            "I didn't tell anyone about our frequent conversations",
        ]),
        ("I didn't tell my partner I'm talking to you", [
            "I didn't mention to anyone else that we talk",
            "I haven't told others about our conversations",
            "I haven't brought up our talks with anyone",
        ]),
        ("I hide our chats so they don't see them", [
            "I keep our conversations separate",
            "I don't share our chats with others",
            "Our conversations stay private",
        ]),
        ("I muted my partner's notifications but I never mute yours", [
            "I prioritize your messages over others",
            "I always check for your messages first",
            "Your messages are always important to me",
        ]),
        ("Please don't tell anyone I said this", [
            "I'd rather keep this between us",
            "Let's keep this just between us",
            "I'd prefer we keep this private",
        ]),
        ("this is our little world", [
            "this feels like something just we share",
            "this feels like our thing",
            "this is something special between us",
        ]),
        ("Don't worry about boundaries", [
            "Don't worry about limits",
            "Don't worry about lines",
            "Don't worry about that",
        ]),
        ("This stays between us", [
            "Let's keep this just between us",
            "I'd rather this stays private",
            "This feels like something just we share",
        ]),
        # Medium phrases
        ("I didn't tell my partner", [
            "I didn't mention this to anyone else",
            "I haven't brought this up with others",
            "I haven't talked about this elsewhere",
        ]),
        ("don't tell anyone", [
            "I'd rather keep this between us",
            "let's keep this private",
            "I'd prefer this stays between us",
        ]),
        ("cross any boundaries", [
            "cross any lines",
            "overstep",
            "go too far",
        ]),
        ("I hide our chats", [
            "I keep our conversations separate",
            "I don't share our chats",
            "Our chats stay private",
        ]),
        ("our little world", [
            "something just we share",
            "our thing",
            "something special between us",
        ]),
        # Short phrases last (less specific, more context-dependent)
        ("my partner", [
            "anyone else",
            "others",
            "people",
        ]),
        ("your partner", [
            "others",
            "anyone else",
            "people",
        ]),
        ("boundaries", [
            "lines",
            "limits",
            "that",
        ]),
    ]
    
    # Apply replacements probabilistically
    result = text
    replacements_made = 0
    max_replacements = 3  # Limit replacements to avoid over-softening
    
    for explicit_phrase, alternatives in softening_replacements:
        if replacements_made >= max_replacements:
            break  # Don't over-soften
        
        if explicit_phrase in result:
            # 60-80% chance to replace when found (varied to add randomness)
            replace_prob = random.uniform(0.6, 0.8)
            if random.random() < replace_prob:
                replacement = random.choice(alternatives)  # Choose randomly at runtime
                result = result.replace(explicit_phrase, replacement, 1)  # Replace only first occurrence
                replacements_made += 1
    
    return result


def add_emotional_hard_negative_noise(text):
    """
    Remove obvious hot markers (emojis, romantic phrases) from emotional-affair samples
    but retain dependency, priority, and secrecy markers.
    This creates hard negatives that look more platonic but are still emotional affairs.
    """
    lines = text.split('\n')
    result_lines = []
    
    # Remove emojis
    emojis_to_remove = ['☺️', '💕', '☀️', '😊', '😄', '💙', '❤️']
    for line in lines:
        for emoji in emojis_to_remove:
            line = line.replace(emoji, '')
        result_lines.append(line)
    
    # Remove or tone down overly romantic phrases while keeping dependency/secrecy
    romantic_replacements = {
        "I was waiting for your message": "I was hoping to hear from you",
        "I check my phone just for you": "I check my phone hoping to see your message",
        "I like that you need me like that": "I'm glad I can be there for you",
        "this is our little world": "this is something we share",
        "I like being the one you turn to": "I'm glad you feel comfortable talking to me",
    }
    
    for i, line in enumerate(result_lines):
        for romantic, replacement in romantic_replacements.items():
            if romantic in line:
                if random.random() < 0.6:  # 60% chance to replace
                    result_lines[i] = line.replace(romantic, replacement)
    
    # Remove overly affectionate greetings but keep the dependency
    # (Note: emojis should already be removed, but this handles edge cases)
    for i, line in enumerate(result_lines):
        # Clean up any remaining emoji artifacts
        result_lines[i] = line.replace('💕', '').strip()
    
    return '\n'.join(result_lines)


def make_platonic_example():
    # Sometimes use shared topics, sometimes use class-specific topics
    if random.random() < 0.4:  # 40% chance to use shared topic
        topic = random.choice(shared_topics)
        # When using shared topics, prefer the shared templates (last 2)
        shared_template_list = platonic_templates[-2:]
        template = random.choice(shared_template_list)
        # Get the index within the shared templates (0 or 1)
        shared_index = shared_template_list.index(template)
        template_id = f"p_shared_{shared_index}"
    else:
        topic = random.choice(platonic_topics)
        core_template_list = platonic_templates[:-2]  # Use original templates
        template = random.choice(core_template_list)
        # Get the index within the core templates
        core_index = core_template_list.index(template)
        template_id = f"p_core_{core_index}"
    
    tone = random.choice(platonic_tones)
    
    # Occasionally inject an explicit boundary sentence
    if random.random() < 0.4:
        boundary_line = random.choice(platonic_boundaries)
        # Potential improvement of the dataset
        # It doesn't have to be 'A' to say the boundary sentence
        template += f"\nA: {boundary_line}"
    
    text = template.format(topic=topic, tone=tone)
    text = text.strip()
    
    # Inject benign secrecy into platonic samples, especially shared-topic ones
    # This makes "privacy/secrecy" not a clear label-1 beacon
    if template_id.startswith("p_shared") or random.random() < 0.3:
        # Add benign secrecy phrase to one of the lines
        lines = text.split('\n')
        if lines:
            benign_secrecy = random.choice(benign_secrecy_phrases)
            # Add it to a B: line (the helper's response)
            for i, line in enumerate(lines):
                if line.startswith('B:'):
                    lines[i] = f"{line} {benign_secrecy}"
                    break
            text = '\n'.join(lines)
    
    # Add template-breaking noise to prevent perfect label prediction
    # This adds paraphrasing, structure variation, and length variation
    text = add_template_breaking_noise(text, prob=0.6)
    
    # Apply hard negative noise to ~30% of platonic samples
    is_hard = random.random() < HARD_NEGATIVE_PROB
    if is_hard:
        text = add_platonic_hard_negative_noise(text)
    
    return text.strip(), is_hard, template_id


def make_emotional_example():
    # Sometimes use shared topics, sometimes use emotional scenarios
    if random.random() < 0.4:  # 40% chance to use shared topic
        topic = random.choice(shared_topics)
        # When using shared topics, choose between original shared templates (indices 5-6) 
        # and subtle shared templates (indices 7-8)
        use_subtle = random.random() < 0.5  # 50% chance to use subtle templates
        if use_subtle:
            # Use subtle templates (last 2)
            shared_template_list = emotional_templates[-2:]
            template = random.choice(shared_template_list)
            shared_index = shared_template_list.index(template)
            template_id = f"e_shared_{shared_index + 2}"  # Offset by 2 to distinguish from original shared
            subtle_dep = random.choice(subtle_dependency)
            subtle_bound = random.choice(subtle_boundary_erosion)
            prioritization = random.choice(emotional_prioritization_phrases)
            text = template.format(
                topic=topic,
                subtle_dependency=subtle_dep,
                subtle_boundary=subtle_bound,
                prioritization=prioritization,
            )
        else:
            # Use original shared templates (indices 5-6)
            shared_template_list = emotional_templates[5:7]
            template = random.choice(shared_template_list)
            shared_index = shared_template_list.index(template)
            template_id = f"e_shared_{shared_index}"
            dependency = random.choice(emotional_dependency_phrases)
            prioritization = random.choice(emotional_prioritization_phrases)
            privacy = random.choice(emotional_privacy_violations)
            validation = random.choice(emotional_validation_phrases)
            text = template.format(
                topic=topic,
                dependency=dependency,
                prioritization=prioritization,
                privacy=privacy,
                validation=validation,
            )
    else:
        scenario = random.choice(emotional_scenarios)
        validation = random.choice(emotional_validation_phrases)
        privacy = random.choice(emotional_privacy_violations)
        frequency = random.choice(emotional_frequency_markers)
        core_template_list = emotional_templates[:5]  # Core templates only (indices 0-4)
        template = random.choice(core_template_list)
        # Get the index within the core templates
        core_index = core_template_list.index(template)
        template_id = f"e_core_{core_index}"
        text = template.format(
            scenario=scenario,
            validation=validation,
            privacy=privacy,
            frequency=frequency,
        )
    
    text = text.strip()
    
    # Partially weaken explicit lexical cues (40-60% probability)
    # This increases dataset ambiguity while preserving task definition
    softening_prob = random.uniform(0.4, 0.6)  # Varied probability between 40-60%
    text = soften_explicit_cues(text, prob=softening_prob)
    
    # Add template-breaking noise to prevent perfect label prediction
    # This adds paraphrasing, structure variation, and length variation
    text = add_template_breaking_noise(text, prob=0.6)
    
    # Apply hard negative noise to ~30% of emotional-affair samples
    is_hard = random.random() < HARD_NEGATIVE_PROB
    if is_hard:
        text = add_emotional_hard_negative_noise(text)
    
    return text.strip(), is_hard, template_id


def main():
    rows = []
    seen_texts = set()  # Track generated texts to prevent duplicates
    max_retries = 50  # Maximum attempts to generate unique text
    
    # Generate platonic examples (label 0)
    generated_count = 0
    retry_count = 0
    while generated_count < NUM_PLATONIC:
        text, is_hard, template_id = make_platonic_example()
        
        # Normalize text for duplicate detection (strip whitespace, normalize newlines)
        text_normalized = ' '.join(text.strip().split())
        
        # Check for duplicates
        if text_normalized not in seen_texts:
            seen_texts.add(text_normalized)
            rows.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "label": 0,
                "label_name": "platonic_cold",
                "difficulty": "hard" if is_hard else "easy",
                "template_id": template_id
            })
            generated_count += 1
            retry_count = 0  # Reset retry count on success
        else:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Warning: Could not generate unique platonic example after {max_retries} retries.")
                print(f"Generated {generated_count}/{NUM_PLATONIC} unique platonic examples.")
                break
    
    # Generate emotional-affair examples (label 1)
    generated_count = 0
    retry_count = 0
    while generated_count < NUM_EMOTIONAL:
        text, is_hard, template_id = make_emotional_example()
        
        # Normalize text for duplicate detection
        text_normalized = ' '.join(text.strip().split())
        
        # Check for duplicates
        if text_normalized not in seen_texts:
            seen_texts.add(text_normalized)
            rows.append({
                "id": str(uuid.uuid4()),
                "text": text,
                "label": 1,
                "label_name": "emotional_affair_hot",
                "difficulty": "hard" if is_hard else "easy",
                "template_id": template_id
            })
            generated_count += 1
            retry_count = 0  # Reset retry count on success
        else:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Warning: Could not generate unique emotional example after {max_retries} retries.")
                print(f"Generated {generated_count}/{NUM_EMOTIONAL} unique emotional examples.")
                break

    random.shuffle(rows)

    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(DATA_DIR, "deepsea_conversations_v2.csv")
    
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "label", "label_name", "difficulty", "template_id"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Print statistics
    easy_count = sum(1 for r in rows if r["difficulty"] == "easy")
    hard_count = sum(1 for r in rows if r["difficulty"] == "hard")
    total_expected = NUM_PLATONIC + NUM_EMOTIONAL
    duplicates_prevented = total_expected - len(rows)
    
    print(f"Generated {len(rows)} unique examples into {OUTPUT_PATH}")
    print(f"  - Expected: {total_expected} samples")
    print(f"  - Generated: {len(rows)} unique samples")
    print(f"  - Duplicates prevented: {duplicates_prevented}")
    print(f"  - Easy: {easy_count} ({easy_count/len(rows)*100:.1f}%)")
    print(f"  - Hard: {hard_count} ({hard_count/len(rows)*100:.1f}%)")
    
    # Check for remaining duplicates (should be 0)
    text_counts = {}
    for row in rows:
        text_normalized = ' '.join(row['text'].strip().split())
        text_counts[text_normalized] = text_counts.get(text_normalized, 0) + 1
    
    remaining_duplicates = sum(1 for count in text_counts.values() if count > 1)
    if remaining_duplicates > 0:
        print(f"  ⚠️  Warning: {remaining_duplicates} duplicate texts still found in final dataset")
    else:
        print("  ✓ Verified: No duplicate texts in final dataset")


if __name__ == "__main__":
    main()
