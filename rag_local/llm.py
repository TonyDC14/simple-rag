import os
import subprocess

import openai


def call_llm(prompt: str, provider: str = 'openai') -> str:
    if provider == 'gemini-cli':
        result = subprocess.run(
            ['gemini-cli', 'prompt', '--model', 'gemini-2.5-pro', prompt],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    elif provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError('OPENAI_API_KEY not set')
        openai.api_key = api_key
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return completion.choices[0].message['content']
    else:
        raise ValueError('Unknown provider')
