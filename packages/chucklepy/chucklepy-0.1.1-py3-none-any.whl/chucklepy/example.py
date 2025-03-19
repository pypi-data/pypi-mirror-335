from fun import generate_pun, comedic_insult, amuseify_text, random_fortune
def main():

    print("==== Single-File Demo of All Functions ====\n")

    print("1) generate_pun() examples:")
    print("   - Tech + Short  :", generate_pun(category="tech", length="short"))
    print("   - General + Med :", generate_pun(category="general", length="medium"))
    print("   - Default       :", generate_pun())

    print("\n2) comedic_insult() examples:")
    print("   - For 'Alice', severity=1:", comedic_insult("Alice", severity=1))
    print("   - For 'Bob',   severity=2:", comedic_insult("Bob", severity=2))
    print("   - For 'Carol', severity=3:", comedic_insult("Carol", severity=3))

    print("\n3) amuseify_text() examples:")
    sample_text = "Hello world, let's have some fun!"
    print(f"   Original text  : {sample_text}")
    print("   - style='emoji':", amuseify_text(sample_text, style="emoji"))
    print("   - style='leet' :", amuseify_text(sample_text, style="leet"))
    print("   - style='random':", amuseify_text(sample_text, style="random"))

    print("\n4) random_fortune() examples:")
    print("   - (life, positive)   :", random_fortune(topic="life", mood="positive"))
    print("   - (career, sarcastic):", random_fortune(topic="career", mood="sarcastic"))
    print("   - (no topic, neutral):", random_fortune(mood="neutral"))


if __name__ == "__main__":
    main()