import json
import concurrent.futures  # For parallel execution

# Define tool functions
class Tool:
    def __init__(self, name, description, function, inputs=None):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = self._build_parameters(inputs or {})
    
    def _build_parameters(self, inputs):
        """Build parameters with configurable types"""
        properties = {}
        for name, config in inputs.items():
            if isinstance(config, list):
                # Format: [type, description]
                param_type, description = config
                properties[name] = {
                    "type": param_type,
                    "description": description
                }
                
                # For arrays, add the items property
                if param_type == "array":
                    # Default to object items for arrays if not specified
                    properties[name]["items"] = {
                        "type": "object"
                    }
            elif isinstance(config, dict):
                properties[name] = config
            else:
                properties[name] = {
                    "type": "string",
                    "description": config
                }
        
        return {
            "type": "object",
            "properties": properties,
            "required": list(inputs.keys())
        }
    
    def execute(self, **kwargs):
        return self.function(**kwargs)

class ChatMemory:
    def __init__(self, max_messages=20):
        self.messages = []
        self.max_messages = max_messages
    
    def add_message(self, role, content, name=None):
        """Add a message to memory, ensuring content is string"""
        # Convert content to string if it's not already
        content = str(content) if not isinstance(content, str) else content
        
        message = {"role": role, "content": content}
        if role == "function" and name:
            message["name"] = name
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self):
        """Get all messages in memory"""
        return self.messages
    
    def clear(self):
        """Clear all messages"""
        self.messages = []

class Agent:
    def __init__(self, name, system_prompt, llm, model_name="gpt-4o", tools=None, verbose=False, memory=None):
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.tools = tools or []
        self.client = llm
        self.is_manager = False
        self.verbose = verbose
        # If no memory is provided, don't create a default one
        self.memory = memory
    
    def add_tool(self, tools):
        """Add one or more tools to the agent"""
        if isinstance(tools, list):
            self.tools.extend(tools)
        else:
            self.tools.append(tools)
    
    def get_tools_config(self):
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        } for tool in self.tools]
    
    def go(self, input_message, chat_history=None):
        if self.verbose:
            print(f"\n🤖 [{self.name}] Processing: {input_message}")
        
        # Only add to memory if memory exists
        if self.memory is not None:
            self.memory.add_message("user", input_message)
            
        # Start with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Use provided chat history, memory, or just current message
        if chat_history:
            messages.extend(chat_history)
        elif self.memory is not None:
            messages.extend(self.memory.get_messages())
        else:
            # If no memory and no chat_history, just use the current message
            messages.append({"role": "user", "content": input_message})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.get_tools_config(),
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        if assistant_message.content and self.memory is not None:
            self.memory.add_message("assistant", str(assistant_message.content))
        
        if assistant_message.tool_calls:
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                for tool in self.tools:
                    if tool.name == tool_call.function.name:
                        if self.verbose:
                            print(f"🔧 [{self.name}] Using tool: {tool.name}")
                        
                        arguments = json.loads(tool_call.function.arguments)
                        result = tool.execute(**arguments)
                        
                        # Convert result to string before storing
                        str_result = str(result)
                        if self.memory is not None:
                            self.memory.add_message("function", str_result, name=tool.name)
                        
                        if not self.is_manager:
                            if self.verbose:
                                print(f"✓ [{self.name}] Result: {str_result}")
                            return str_result
                        
                        tool_results.append({"tool": tool.name, "result": str_result})
            
            if self.is_manager:
                results_text = "\n\n".join([f"[{r['tool']}]: {r['result']}" for r in tool_results])
                final_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Synthesize this information:"},
                        {"role": "user", "content": results_text}
                    ]
                )
                result = final_response.choices[0].message.content
                self.memory.add_message("assistant", result)
                return result
        
        return assistant_message.content or "I couldn't generate a response."

class ManagerAgent(Agent):
    """
    A manager agent that treats other agents as tools.
    Each agent becomes available as a tool that the manager can call.
    """
    def __init__(self, name, system_prompt, llm, model_name="gpt-4o", agents=None, parallel=False, verbose=False, memory=None):
        # Don't create a default memory if none is provided
        super().__init__(name, system_prompt, llm, model_name, verbose=verbose, memory=memory)
        self.agent_tools = []
        self.is_manager = True
        self.parallel = parallel
        if agents:
            self.register_agents([agent[0] for agent in agents], 
                               {agent[0].name: agent[1] for agent in agents})
    
    def register_agent(self, agent, description=None):
        if description is None:
            description = f"Use the {agent.name} for tasks related to its expertise"
        
        def call_agent(query, chat_history=None):
            print(f"\n📣 [{self.name}] Calling {agent.name} with query: {query[:30]}...")
            
            # Call the agent with optional chat history
            if chat_history:
                result = agent.go(query, chat_history=chat_history)
            else:
                result = agent.go(query)
            
            print(f"📣 [{agent.name}] Responded with: {result[:30]}...")
            
            # Remove the prefix if present
            return result.replace(f"[{agent.name}]: ", "") if isinstance(result, str) else result
        
        # Create a tool for this agent
        agent_tool = Tool(
            name=agent.name,
            description=description,
            function=call_agent,
            inputs={
                "query": f"The question or task to ask the {agent.name}",
                "chat_history": {
                    "type": "array",
                    "description": "Optional chat history to provide context",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["user", "assistant", "system", "function"]
                            },
                            "content": {
                                "type": "string"
                            },
                            "name": {
                                "type": "string"
                            }
                        },
                        "required": ["role", "content"]
                    }
                }
            }
        )
        
        print(f"🔧 [{self.name}] Registered {agent.name} as a tool")
        self.add_tool(agent_tool)
        self.agent_tools.append(agent_tool)
        return self
        
    def register_agents(self, agents, descriptions=None):
        """
        Register multiple agents at once
        """
        if descriptions is None:
            descriptions = {}
            
        for agent in agents:
            self.register_agent(agent, descriptions.get(agent.name))
            
        return self
    
    def go(self, input_message, chat_history=None):
        if self.verbose:
            print(f"\n🤖 [{self.name}] Processing: {input_message}")
        
        # Store the user message in memory if it exists
        if self.memory is not None:
            self.memory.add_message("user", input_message)
        
        # Set up messages with system prompt
        messages = [
            {
                "role": "system",
                "content": f"""You are a manager agent that performs two steps:

1. Planning Step:
Analyze the user query and determine if it contains multiple distinct requests.
Break down the query into separate tasks. For each task, identify which agent 
({', '.join([tool.name for tool in self.agent_tools])}) should handle it.

2. Execution Step:
After planning, proceed to execute the tasks using the appropriate agents.
Provide a comprehensive response using the identified agents efficiently.

{self.system_prompt}"""
            }
        ]
        
        # Add chat history if provided, otherwise use memory
        if (chat_history):
            messages.extend(chat_history)
        elif self.memory is not None:
            messages.extend(self.memory.get_messages())
        else:
            messages.append({"role": "user", "content": input_message})
        
        # Make sure the last message is the current input if it's not already included
        if not any(msg.get("role") == "user" and msg.get("content") == input_message for msg in messages):
            messages.append({"role": "user", "content": input_message})
        
        # Debug output
        print(f"Sending {len(messages)} messages to LLM, with {len(self.get_tools_config())} tools")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.get_tools_config(),
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Store the tool calls for debugging
        self.last_tool_calls = assistant_message.tool_calls
        
        if assistant_message.content and self.memory is not None:
            self.memory.add_message("assistant", assistant_message.content)
        
        if assistant_message.tool_calls:
            # Debug output
            print(f"Tool calls received: {[t.function.name for t in assistant_message.tool_calls]}")
            
            # Handle parallel execution if enabled
            if self.parallel and len(assistant_message.tool_calls) > 1:
                result = self._execute_parallel(assistant_message.tool_calls, input_message)
            else:
                # Sequential execution (original behavior)
                result = self._execute_sequential(assistant_message.tool_calls, input_message)
            
            # Save the final result to memory if it exists
            if self.memory is not None:
                self.memory.add_message("assistant", result)
            return result
        
        return assistant_message.content or "I couldn't generate a response."
    
    def _execute_sequential(self, tool_calls, original_query):
        """Execute tool calls sequentially (original behavior)"""
        results = []
        
        for tool_call in tool_calls:
            for tool in self.tools:
                if tool.name == tool_call.function.name:
                    arguments = json.loads(tool_call.function.arguments)
                    result = tool.execute(**arguments)
                       
                    # Save the function result to memory if memory exists
                    if self.memory is not None:
                        self.memory.add_message("function", result, name=tool.name)
                      
                    # Include agent name with result for better context
                    results.append(f"[{tool.name}]: {result}")
        
        # Combine results
        combined_result = "\n\n".join(results)
            
        # Generate natural summary of the combined results
        final_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system", 
                    "content": "Synthesize the information from multiple agents into a cohesive response that addresses all parts of the user's original query."
                },
                {"role": "user", "content": f"Original query: {original_query}\n\nAgent responses:\n{combined_result}"}
            ]
        )
        
        return final_response.choices[0].message.content
    
    def _execute_parallel(self, tool_calls, original_query):
        """Execute tool calls in parallel using ThreadPoolExecutor"""
        tasks = []
        tool_names = []
        
        # Prepare all tasks
        print("\n=== Starting Parallel Execution ===")
        for tool_call in tool_calls:
            for tool in self.tools:
                if tool.name == tool_call.function.name:
                    arguments = json.loads(tool_call.function.arguments)
                    tasks.append((tool, arguments))
                    tool_names.append(tool.name)
                    print(f"✓ Prepared task for: {tool.name}")
        
        results = []
        
        # Execute tasks in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print("\n=== Executing Tasks in Parallel ===")
            futures = []
            for task, args in tasks:
                future = executor.submit(task.execute, **args)
                futures.append((future, task.name))
                print(f"▶ Started: {task.name}")
            
            # Wait for completion
            for future, name in futures:
                try:
                    result = future.result()
                    print(f"✓ Completed: {name}")
                    results.append(f"[{name}]: {result}")
                except Exception as e:
                    print(f"✗ Failed: {name} - {str(e)}")
                    results.append(f"[{name}] Error: {str(e)}")
        
        print("\n=== All Tasks Completed ===")
        return self._summarize_results(results, original_query)

    def _summarize_results(self, results, original_query):
        """Summarize results from parallel execution"""
        combined_result = "\n".join(results)
        
        final_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system", 
                    "content": "Synthesize the information from multiple agents into a cohesive response."
                },
                {"role": "user", "content": f"Original query: {original_query}\n\nAgent responses:\n{combined_result}"}
            ]
        )
        
        return final_response.choices[0].message.content
