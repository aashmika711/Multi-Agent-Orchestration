%%capture
!pip install autogen==0.9.9 openai==1.101.0
import re
from autogen import ConversableAgent, GroupChat, GroupChatManager
from openai import OpenAI
import logging
import warnings
import os
os.environ["OPENAI_API_KEY"] = "API key here"
# Suppress autogen and other deprecation/user warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Suppress warnings from autogen.oai.client
logging.getLogger("autogen.oai.client").setLevel(logging.ERROR)
client = OpenAI()
def make_llm_config():
    """
    Create a robust LLM configuration with a primary and backup model.
    Automatically switches to the backup model if the primary fails.
    """

    # Define the preferred and fallback models
    primary_model = "gpt-5-nano"
    backup_model = "gpt-4o-mini"

    # Prepare the config list for autogen-style agents
    config_list = [
        {"model": primary_model},
        {"model": backup_model},  # <-- fallback
    ]

    # Return complete LLM config
    llm_config = {
        "config_list": config_list,
        "temperature": 1.0,
        "timeout": 140,
        "max_tokens": 5000,
    }

    return llm_config
 class OpenAIConversableAgent(ConversableAgent):
    def initiate_chat(self, manager, message):
        """
        Send a message using the primary model.
        If it fails, automatically retry with the backup model.
        """

        messages = [{"role": "user", "content": message}]
        llm_config = make_llm_config()
        config_list = llm_config.get("config_list", [])
        temperature = llm_config.get("temperature", 1.0)
        max_tokens = llm_config.get("max_tokens", 2048)

        # ✅ Sanity check
        if not config_list:
            print("⚠️ No models found in LLM config. Please check make_llm_config().")
            return None

        for config in config_list:
            model = config.get("model", "unknown")
            try:
                print(f"\n🔹 Trying model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=temperature,
                )

                if response and hasattr(response, "choices") and response.choices:
                    print(f"✅ Response generated using {model}")
                    return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"⚠️ {model} failed with error: {e}. Trying fallback model...")

        print("❌ All models failed to generate a response.")
        return None
def build_agents(llm_config):
    author_agent = OpenAIConversableAgent(
        name="author",
        system_message=("You are the person providing a poem theme and preferences. You only speak once to kick things off."),
        llm_config=llm_config,
    )
    muse_agent = OpenAIConversableAgent(
        name="muse",
        system_message=(
            "You propose 3 distinct poetic directions for the given theme. "
            "For each: Title (<=5 words), Vibe (a short phrase), and one-sentence concept. "
            "Then clearly mark exactly one as Selected with a short rationale. Respond once."
        ),
        llm_config=llm_config,
    )
    verse_agent = OpenAIConversableAgent(
        name="verse",
        system_message=(
            "You write the full poem from the Selected idea. "
            "Respect any requested form, tone, and language. "
            "Use crisp line breaks and concrete imagery. Respond once."
        ),
        llm_config=llm_config,
    )
    editor_agent = OpenAIConversableAgent(
        name="editor",
        system_message=(
            "You lightly polish the poem for rhythm and clarity while preserving meaning and length. "
            "Output ONLY the revised poem and end your response with the token: POEM_COMPLETE"
        ),
        llm_config=llm_config,
    )
    return author_agent, muse_agent, verse_agent, editor_agent
def run_session():
    llm_config = make_llm_config()
    print("********** llm config is******",llm_config)
    author_agent, muse_agent, verse_agent, editor_agent = build_agents(llm_config)
    
    # ✅ Include all agents in the groupchat
    groupchat = GroupChat(
        agents=[author_agent, muse_agent, verse_agent, editor_agent],
        messages=[],
        max_round=5,
        speaker_selection_method="auto",
    )
    manager = GroupChatManager(name="manager", groupchat=groupchat, llm_config=llm_config)

    print(f"\n🎭 Welcome to the AI Poetry Studio! (Using gpt-5-nano)\n")

    # Collect user inputs
    language = input("🗣️ Language (e.g., English, Hindi — or blank): ").strip()
    theme = input("✨ Theme (e.g., 'monsoon nostalgia', 'startup hustle'): ").strip()
    form = input("📏 Poetic form (free verse / haiku / sonnet — or blank): ").strip()
    tone = input("🎨 Tone (e.g., witty, romantic, contemplative — or blank): ").strip()

    # Build constraints section
    constraints = []
    if form:
        constraints.append(f"Form: {form}")
    if tone:
        constraints.append(f"Tone: {tone}")
    if language:
        constraints.append(f"Language: {language}")
    constraints_text = "\n".join(constraints) if constraints else "No special constraints."

    # Construct the main message
    message = (
        f"Theme: {theme}\n"
        f"{constraints_text}\n\n"
        "Muse: please propose ideas and select one.\n"
        "Verse: write the full poem from the selected concept.\n"
        "Editor: lightly polish the poem and ensure the LAST line is exactly 'POEM_COMPLETE'."
    )

    print("\n📝 Generating your poem...\n")

    try:
        # Initiate the chat
        final_response = author_agent.initiate_chat(manager, message=message)

        # ✅ Handle different return types
        if final_response is None:
            if manager.groupchat.messages:
                final_text = manager.groupchat.messages[-1]["content"]
            else:
                raise RuntimeError("No response and no messages from groupchat.")
        elif isinstance(final_response, list):
            final_text = final_response[-1]["content"]
        else:
            final_text = str(final_response)

        # ✅ Improved formatted output
        print("\n" + "=" * 50)
        print("🌟 FINAL OUTPUT 🌟")
        print("=" * 50 + "\n")

        # Split into sections for cleaner formatting
        lines = final_text.splitlines()
        section = None

        for line in lines:
            if line.lower().startswith("muse:"):
                section = "muse"
                print("🎨 Muse — Proposed Ideas:\n")
            elif line.lower().startswith("selected concept"):
                section = "concept"
                print("\n✅ Selected Concept:\n")
            elif line.lower().startswith("verse:"):
                section = "verse"
                print("\n📝 Verse — Generated Poem:\n")
            elif line.lower().startswith("editor:"):
                section = "editor"
                print("\n✨ Editor — Polished Version:\n")
            elif "POEM_COMPLETE" in line:
                print(line.strip())
                print("\n" + "=" * 50)
                print("✅ Poem generation complete!\n")
                break
            else:
                print(line.strip())

        print("(Scroll to the end for 'POEM_COMPLETE').\n")

    except Exception as e:
        print(f"\n⚠️ Error during generation: {e}")
        print("Please try again or check your model configuration.")

        # ✅ Debug: show all messages if something fails
        if manager.groupchat.messages:
            print("\n--- DEBUG: All Messages ---")
            for msg in manager.groupchat.messages:
                print(f"{msg['role']}: {msg['content']}")

if __name__ == "__main__":
    run_session()
