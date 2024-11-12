def clean_response(response_text):
    # List of tokens/markers to remove
    tokens_to_remove = [
            '<|assistant|>',
            '<|human|>',
            '```',
            '<|system|>',
            '<|user|>', "Point 1:", "For example:", "Position:", "Argument 1:", "join us", "example:"]
    
    # Remove all tokens
    for token in tokens_to_remove:
        response_text = response_text.replace(token, '')
    # Clean up any extra whitespace
    response_text = response_text.strip()
    # Remove any multiple consecutive newlines
    response_text = '\n'.join(line for line in response_text.splitlines() if line.strip())
            # Enforce word limit (130 words)
    words = response_text.split()
    if len(words) > 130:
        response_text = ' '.join(words[:130]) + '.'
            
    # Remove partial sentences at the end
    if response_text[-1] not in '.!?':
        last_sentence = response_text.rstrip().split('.')
        response_text = '.'.join(last_sentence[:-1]) + '.'

    return response_text
