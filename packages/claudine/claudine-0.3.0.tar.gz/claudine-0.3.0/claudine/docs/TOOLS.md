# Tool Use with Claude

This document provides information about tool use with Claude, based on the [Anthropic documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview).

## Controlling Claude's Output

### Forcing Tool Use

In some cases, you may want Claude to use a specific tool to answer the user's question, even if Claude thinks it can provide an answer without using a tool. You can do this by specifying the tool in the `tool_choice` field:

```python
tool_choice = {"type": "tool", "name": "get_weather"}
```

When working with the `tool_choice` parameter, there are four possible options:
- `auto`: Allows Claude to decide whether to call any provided tools or not. This is the default value when tools are provided.
- `any`: Tells Claude that it must use one of the provided tools, but doesn't force a particular tool.
- `tool`: Allows us to force Claude to always use a particular tool.
- `none`: Prevents Claude from using any tools. This is the default value when no tools are provided.

Note that when you have `tool_choice` as `any` or `tool`, Claude will not emit a chain-of-thought text content block before `tool_use` content blocks, even if explicitly asked to do so.

If you would like to keep chain-of-thought (particularly with Opus) while still requesting that the model use a specific tool, you can use `{"type": "auto"}` for `tool_choice` (the default) and add explicit instructions in a user message. For example: "What's the weather like in London? Use the get_weather tool in your response."

### Chain of Thought

When using tools, Claude will often show its "chain of thought", i.e. the step-by-step reasoning it uses to break down the problem and decide which tools to use. The Claude 3 Opus model will do this if `tool_choice` is set to `auto` (the default value), and Sonnet and Haiku can be prompted into doing it.

For example, given the prompt "What's the weather like in San Francisco right now, and what time is it there?", Claude might respond with:

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "<thinking>To answer this question, I will: 1. Use the get_weather tool to get the current weather in San Francisco. 2. Use the get_time tool to get the current time in the America/Los_Angeles timezone, which covers San Francisco, CA.</thinking>"
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": {"location": "San Francisco, CA"}
    }
  ]
}
```

It's important to note that while the `<thinking>` tags are a common convention Claude uses to denote its chain of thought, the exact format may change over time. Your code should treat the chain of thought like any other assistant-generated text, and not rely on the presence or specific formatting of the `<thinking>` tags.

### Parallel Tool Use

By default, Claude may use multiple tools to answer a user query. You can disable this behavior by setting `disable_parallel_tool_use=true` in the `tool_choice` field:

```python
tool_choice = {
    "type": "auto",
    "disable_parallel_tool_use": True
}
```

- When `tool_choice` type is `auto`, this ensures that Claude uses at most one tool
- When `tool_choice` type is `any` or `tool`, this ensures that Claude uses exactly one tool

#### Parallel Tool Use with Claude 3.7 Sonnet

Claude 3.7 Sonnet may be less likely to make parallel tool calls in a response, even when you have not set `disable_parallel_tool_use`. To work around this, Anthropic recommends introducing a "batch tool" that can act as a meta-tool to wrap invocations to other tools simultaneously. If this tool is present, the model will use it to simultaneously call multiple tools in parallel.

See [this example](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/parallel_tools_claude_3_7_sonnet.ipynb) in the Anthropic cookbook for how to use this workaround.
