from slimagents import Agent





# pdf_converter = Agent(
#     instructions="Your task is to convert PDF files to Markdown.",
#     model="gemini/gemini-2.0-flash",
# )

# # response = agent.run_sync("Who are you?")
# # print(response.value)

# with open("./temp/Enchiladas med salat.pdf", "rb") as pdf_file:
#     response = pdf_converter.run_sync(pdf_file)
#     print(response.value)



# def foo(a, b, c=3, /, *, d):
#     print(a, b, c)

# foo(1, 2, 3)

class OrderAgent(Agent):
    def __init__(self):
        super().__init__(tools=[print])

order_agent = OrderAgent()
print(order_agent.name)