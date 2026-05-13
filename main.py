from orchestrator import graph

def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        response = graph.invoke({"user_input": user_input})
        print("Execution Path:", response["execution_path"])
        print("AI:", response["tool_result"])

if __name__ == "__main__":
    main()