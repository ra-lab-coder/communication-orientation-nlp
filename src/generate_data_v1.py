import os
import csv
import random
import uuid

random.seed(42)

NUM_PLATONIC = 250
NUM_EMOTIONAL = 250

platonic_topics = [
    "refactoring the backend service",
    "optimizing the training loop in a neural network",
    "career planning for the next 3 years",
    "preparing for a technical interview",
    "discussing a philosophy book about free will",
    "debugging an API integration issue",
    "planning a group study session",
    "organizing the team sprint backlog",
    "brainstorming research topics for a paper",
    "setting up Docker and CI/CD pipelines",
]

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
    "I’d rather keep our convos focused on work and ideas, if that’s okay.",
    "Let’s keep this about the project so we don’t blur lines.",
    "I’m happy to help as a friend, but I don’t want to cross any boundaries.",
]

platonic_templates = [
    """A: Hey, can you quickly look at my code? I'm not sure if this architecture for {topic} makes sense.
B: Sure, send it over. From a(n) {tone} point of view, I'd decouple the modules first.
A: That makes sense. Thanks, that's exactly what I needed.
B: No worries. Once you’ve tried it, let me know if the tests fail and we’ll debug.""",

    """A: I’m trying to decide between two job offers and I’d like your opinion.
B: Okay, let's list pros and cons for each. We can compare salary, growth, and tech stack.
A: That’s helpful. I’m not really looking for emotional support, just a clear comparison.
B: Perfect, we’ll just treat this like a decision matrix and keep it objective.""",

    """A: Our team is arguing about how to organize {topic}.
B: Let's break it down logically: what's the goal, constraints, and current blockers?
A: I appreciate how you always keep things objective.
B: It's easier to stay friends when we keep boundaries and focus on the work.""",

    """A: I feel a bit overwhelmed with this project deadline.
B: Okay, let’s create a task list and prioritize. We can cut scope where needed.
A: Thanks, I just needed someone to help me structure the work.
B: Happy to help. For deeper emotional stuff though, your partner might be better support.""",

    """A: I read this paper on {topic} and I’m confused about the methodology.
B: Let's go through the assumptions and equations step by step.
A: I like how we can geek out about this.
B: Same, it's fun to have an intellectual sparring partner without it getting personal."""
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
    """A: I’m having another fight with my partner and I feel {scenario}.
B: I’m here, talk to me. {validation}
A: You always know what to say. {validation}
B: I’ll stay up with you, don't worry about the time.""",

    """A: {frequency}
B: Morning 💕 I was waiting for your message.
A: I feel {scenario}. I didn’t tell my partner we talk this much, {privacy}
B: It’s okay, this is our little world. You can always come to me first.""",

    """A: Can you comfort me? I had a rough day and I feel {scenario}.
B: Of course, I’ll always be here for you. {validation}
A: I know I shouldn’t rely on you this much, but I can’t help it.
B: Don’t worry about boundaries, I like being the one you turn to.""",

    """A: I’m lying in bed thinking about how you always reply, even when you’re busy.
B: I check my phone just for you, honestly.
A: Sometimes I feel guilty because {privacy}
B: As long as you’re happy when you talk to me, that’s all that matters.""",

    """A: {frequency}
B: I was just about to text you. It feels weird if we don’t talk all day.
A: Same, I get anxious if you go quiet. {validation}
B: I like that you need me like that."""
]


def make_platonic_example():
    topic = random.choice(platonic_topics)
    tone = random.choice(platonic_tones)
    template = random.choice(platonic_templates)
    # Occasionally inject an explicit boundary sentence
    if random.random() < 0.4:
        boundary_line = random.choice(platonic_boundaries)
        # Potential improvement of the dataset
        # It doesn't have to be 'A' to say the boundary sentence
        template += f"\nA: {boundary_line}"
    text = template.format(topic=topic, tone=tone)
    return text.strip()


def make_emotional_example():
    scenario = random.choice(emotional_scenarios)
    validation = random.choice(emotional_validation_phrases)
    privacy = random.choice(emotional_privacy_violations)
    frequency = random.choice(emotional_frequency_markers)
    template = random.choice(emotional_templates)
    text = template.format(
        scenario=scenario,
        validation=validation,
        privacy=privacy,
        frequency=frequency,
    )
    return text.strip()


def main():
    rows = []

    # Generate platonic examples (label 0)
    for _ in range(NUM_PLATONIC):
        text = make_platonic_example()
        rows.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "label": 0,
            "label_name": "platonic_cold"
        })

    # Generate emotional-affair examples (label 1)
    for _ in range(NUM_EMOTIONAL):
        text = make_emotional_example()
        rows.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "label": 1,
            "label_name": "emotional_affair_hot"
        })

    random.shuffle(rows)

    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)
    OUTPUT_PATH = os.path.join(DATA_DIR, "deepsea_conversations.csv")
    
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "label", "label_name"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Generated {len(rows)} examples into {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
