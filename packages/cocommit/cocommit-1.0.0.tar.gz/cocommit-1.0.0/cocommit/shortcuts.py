shortcuts = {
    'bedrock-claude37': {
        "model_provider": "bedrock",
        "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "region_name": "us-east-1"
    },
    'gpt4o': {
        'model_provider':'openai',
        'model':'gpt-4o'
    }
}

def get_shortcut(name):
    return shortcuts.get(name, {})
