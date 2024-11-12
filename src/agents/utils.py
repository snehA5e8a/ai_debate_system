def clean_response(response_text):
    if not response_text:
        return ""
        
    try:
        # List of tokens/markers to remove
        tokens_to_remove = [
            '<|assistant|>',
            '<|human|>',
            '```',
            '<|system|>',
            '<|user|>', 
            "Point 1:", 
            "For example:", 
            "Position:", 
            "Argument 1:", 
            "join us", 
            "example:"
        ]
        
        # Remove all tokens
        for token in tokens_to_remove:
            response_text = response_text.replace(token, '')
            
        # Clean up any extra whitespace
        response_text = response_text.strip()
        
        # Remove any multiple consecutive newlines while preserving paragraph structure
        response_text = '\n\n'.join(para.strip() for para in response_text.split('\n') if para.strip())
        
        # Check if the text ends with an incomplete sentence
        last_period = response_text.rfind('.')
        last_question = response_text.rfind('?')
        last_exclamation = response_text.rfind('!')
        
        # Find the last complete sentence
        last_sentence_end = max(last_period, last_question, last_exclamation)
        
        # If we have an incomplete sentence at the end, truncate to the last complete one
        if last_sentence_end != -1 and last_sentence_end < len(response_text) - 1:
            incomplete_part = response_text[last_sentence_end + 1:].strip()
            # Only truncate if the remaining part is an incomplete sentence
            if incomplete_part and not any(incomplete_part.endswith(x) for x in ['.', '!', '?']):
                response_text = response_text[:last_sentence_end + 1]
        
        return response_text.strip()
    except Exception as e:
        print(f"Error in clean_response: {str(e)}")  # Debug print
        return response_text  # Return original text if cleaning fails