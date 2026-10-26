"""Talk to your agent: python -m support_agent.app (needs ANTHROPIC_API_KEY in .env)."""

import anthropic
from dotenv import load_dotenv

from .agent import SupportAgent


def main() -> None:
    load_dotenv()
    agent = SupportAgent(anthropic.Anthropic())
    print("Northwind support. Try: 'I'm dana@example.com, my headphones broke, can I get a refund?' (Ctrl+C to quit)")
    while True:
        try:
            text = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if text:
            print(f"\nagent > {agent.handle(text)}")


if __name__ == "__main__":
    main()
