from claudine.tokens.models import TokenUsage, TokenUsageInfo
from claudine.tokens.tracking import TokenTracker

# Create a token tracker and add some test messages
tracker = TokenTracker()
tracker.add_message('msg1', 100, 200, is_tool_related=False)
tracker.add_message('msg2', 150, 250, is_tool_related=True, tool_name='calculator')

# Get the token usage information
usage_info = tracker.get_token_usage()

# Print the results
print("=== Token Usage Test ===")
print(f"Text usage: {usage_info.text_usage.input_tokens} input, {usage_info.text_usage.output_tokens} output, {usage_info.text_usage.total_tokens} total")
print(f"Tools usage: {usage_info.tools_usage.input_tokens} input, {usage_info.tools_usage.output_tokens} output, {usage_info.tools_usage.total_tokens} total")
print(f"Total usage: {usage_info.total_usage.input_tokens} input, {usage_info.total_usage.output_tokens} output, {usage_info.total_usage.total_tokens} total")

print("\n=== By Tool ===")
for tool_name, usage in usage_info.by_tool.items():
    print(f"Tool: {tool_name}")
    print(f"  Input tokens: {usage.input_tokens}")
    print(f"  Output tokens: {usage.output_tokens}")
    print(f"  Total tokens: {usage.total_tokens}")
