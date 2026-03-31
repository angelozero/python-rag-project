import os
from dotenv import load_dotenv
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langsmith import traceable

# Load environment variables from .env file
load_dotenv()

# Configuration constants retrieved from environment
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS"))


def get_chat_model():
    """
    Initializes and returns the Chat Model (LLM) instance.
    Uses LiteLLM proxy via OpenAI-compatible interface.
    """
    return init_chat_model(
        model=MODEL_NAME,
        model_provider="openai",
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0,
    )


def get_embeddings():
    """
    Initializes and returns the Embeddings instance.
    Configured to handle float encoding format for Ollama compatibility.
    """
    return init_embeddings(
        model=MODEL_NAME,
        provider="openai",
        api_key=API_KEY,
        base_url=BASE_URL,
        # Force float encoding to avoid LiteLLM/Ollama base64 errors
        model_kwargs={"encoding_format": "float"},
    )


@tool
def get_product_price(product: str) -> float:
    """Look up the price of a product in the catalog."""
    print(f"\n--> Executing @tool get_product_price (product = '{product}')")
    prices = {"laptop": 1299.99, "headphones": 149.95, "keyboard": 89.50}
    return prices.get(product, 0)


@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """
    Calculate the final price after discount.
    Input 'price' MUST be the exact float returned by get_product_price.
    Input 'discount_tier' MUST be one of: 'bronze', 'silver', or 'gold'.
    """
    print(
        f"\n--> Executing @tool apply_discount (price = '{price}', discount_tier = '{discount_tier}')"
    )
    discount_percentage = {"bronze": 5, "silver": 12, "gold": 23}
    discount = discount_percentage.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)


# ---------- #
# Agent Loop #
# ---------- #
@traceable(name="LangChain Agent Loop")
def run_agent(question: str):
    tools = [get_product_price, apply_discount]
    tools_dict = {t.name: t for t in tools}

    llm = get_chat_model()
    llm_with_tools = llm.bind_tools(tools)

    print(f"\nQuestion: {question}")
    print(f"=" * 65)
    print("")

    # ------------- #
    # Agent Thought #
    # ------------- #

    messages = [
        SystemMessage(
            content=(
                "You are a precise Shopping Assistant. You must follow this EXACT execution flow:\n\n"
                "1. PRICE LOOKUP: If the user asks about a product, you MUST call 'get_product_price'.\n"
                "   - DO NOT assume prices. \n"
                "   - DO NOT use prices from previous conversation steps unless 'get_product_price' was called in this session.\n\n"
                "2. DISCOUNT POLICY: \n"
                "   - If you have the price but NO discount tier (bronze, silver, gold), STOP and ask the user for their tier.\n"
                "   - DO NOT call 'apply_discount' with a guessed tier.\n\n"
                "3. CALCULATION: Once you have BOTH the price and the tier, call 'apply_discount' ONCE.\n"
                "   - NEVER perform math manually. \n"
                "   - NEVER call 'apply_discount' more than once for the same request.\n\n"
                "4. FINAL RESPONSE: After receiving the result from 'apply_discount', provide the final price and STOP. "
                "Do not suggest any further tool calls after the final price is calculated."
            )
        ),
        HumanMessage(question),
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):

        ai_message = llm_with_tools.invoke(messages)
        tool_calls = ai_message.tool_calls
        print(f"\nAI Message Content: {ai_message.content}")

        if not tool_calls:
            print(f"\nFinal Answer: {ai_message.content}")
            return ai_message.content

        tool_call = tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")

        print(f"\n[Tool Selected] {tool_name} with args: {tool_args}")

        tool_to_use = tools_dict.get(tool_name)
        if tool_to_use is None:
            raise ValueError(f"\nError: Tool '{tool_name} not found!")

        observation = tool_to_use.invoke(tool_args)

        # Verificação: se a ferramenta for apply_discount, ela só pode rodar UMA VEZ no histórico
        if tool_name == "apply_discount":
            already_applied = any(
                isinstance(m, ToolMessage)
                and m.tool_call_id
                in [
                    tc.get("id")
                    for m in messages
                    if hasattr(m, "tool_calls") and m.tool_calls
                    for tc in m.tool_calls
                    if tc.get("name") == "apply_discount"
                ]
                for m in messages
            )
            # Forma mais simples de ler o histórico:
            used_tools = [
                tc.get("name")
                for m in messages
                if hasattr(m, "tool_calls") and m.tool_calls
                for tc in m.tool_calls
            ]

            if "apply_discount" in used_tools:
                print(
                    f"\n[!] Bloqueio: O modelo tentou aplicar desconto novamente. Encerrando."
                )
                return f"The final price is {tool_args}. (Discount already applied)"

        messages.append(ai_message)
        messages.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call_id)
        )

        print("=" * 21)

    print(f"\nEnd")
    return None
