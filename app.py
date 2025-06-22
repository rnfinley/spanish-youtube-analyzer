from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from collections import Counter
import re

app = Flask(__name__)

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_word_frequency(transcript_text):
    """Extract words and count their frequency"""
    # Convert to lowercase and extract words (letters only)
    words = re.findall(r'\b[a-záéíóúñü]+\b', transcript_text.lower())
    
    # Count frequency
    word_freq = Counter(words)
    
    # Sort by frequency (highest first)
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_words

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    try:
        data = request.get_json()
        youtube_url = data.get('url', '')
        
        # Extract video ID
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Get transcript list
        try:
            transcript_list = YouTubeTranscriptApi().list(video_id)
            available_languages = []
            
            # Track available transcripts
            for transcript in transcript_list:
                available_languages.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated
                })
            
            # Try to find and fetch Spanish transcript
            transcript_data = None
            language_used = None
            
            # First try to find any Spanish transcript
            for transcript in transcript_list:
                if transcript.language_code.startswith('es'):
                    transcript_data = transcript.fetch()
                    language_used = f"{transcript.language} ({transcript.language_code})"
                    break
            
            if not transcript_data:
                # If no Spanish found, return error with available languages
                return jsonify({
                    'error': 'No Spanish transcript found',
                    'available_languages': available_languages,
                    'message': 'This video does not have Spanish captions. Available languages are listed above.'
                }), 400
                
        except Exception as e:
            return jsonify({
                'error': 'Could not retrieve transcripts',
                'details': str(e),
                'message': 'This video might not have any captions enabled, or it might be private/age-restricted.'
            }), 400
        
        # Combine all transcript text
        full_text = ' '.join([entry.text for entry in transcript_data])
        
        # Get word frequency
        word_frequency = get_word_frequency(full_text)
        
        return jsonify({
            'success': True,
            'words': word_frequency[:100],  # Return top 100 words
            'total_unique_words': len(word_frequency),
            'video_id': video_id,
            'language_used': language_used
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Unexpected error occurred',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)