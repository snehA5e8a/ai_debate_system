def clean_response(response_text: str) -> str:
    """Clean and format response text"""
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
    
    # Clean up whitespace
    response_text = response_text.strip()
    
    # Remove multiple consecutive newlines
    response_text = '\n'.join(
        line for line in response_text.splitlines() 
        if line.strip()
    )
    
    # Enforce word limit (130 words)
    words = response_text.split()
    if len(words) > 130:
        response_text = ' '.join(words[:130]) + '.'
    
    # Remove partial sentences at the end
    if response_text[-1] not in '.!?':
        last_sentence = response_text.rstrip().split('.')
        response_text = '.'.join(last_sentence[:-1]) + '.'
    
    return response_text

def format_debate_summary(debate_log: list) -> str:
    """Format debate log into a readable summary"""
    summary = []
    for entry in debate_log:
        timestamp = entry.get('timestamp', '')
        event_type = entry.get('type', '')
        content = entry.get('content', '')
        
        formatted_entry = f"[{timestamp}] {event_type}:\n{content}\n"
        summary.append(formatted_entry)
    
    return "\n".join(summary)

def calculate_debate_metrics(debate_log: list) -> dict:
    """Calculate various metrics from debate log"""
    metrics = {
        'total_arguments': 0,
        'total_interventions': 0,
        'total_fact_checks': 0,
        'average_confidence': 0.0,
        'topic_adherence': 0.0
    }
    
    confidences = []
    for entry in debate_log:
        if entry['type'].endswith(('_REBUTTAL', '_CLOSING')):
            metrics['total_arguments'] += 1
            if 'metadata' in entry and 'confidence' in entry['metadata']:
                confidences.append(entry['metadata']['confidence'])
        
        elif entry['type'] == 'MODERATOR':
            if 'intervention' in str(entry.get('metadata', {})):
                metrics['total_interventions'] += 1
        
        elif entry['type'] == 'FACT_CHECK':
            metrics['total_fact_checks'] += 1
    
    if confidences:
        metrics['average_confidence'] = sum(confidences) / len(confidences)
    
    return metrics

def parse_llm_response(response: str) -> dict:
    """Parse structured responses from LLM"""
    sections = {}
    current_section = None
    current_content = []
    
    for line in response.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line.endswith(':'):
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[:-1].lower()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections