from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from collections import Counter
import re
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Models ---
class Video(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(200), nullable=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), unique=True, nullable=False)
    frequency = db.Column(db.Integer, default=1, nullable=False)

with app.app_context():
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    db.create_all()

SPANISH_STOP_WORDS = [
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'un', 'por', 'con', 'no', 'una', 'su', 'para', 'es',
    'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'ha', 'sí', 'porque', 'esta', 'son', 'entre',
    'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos',
    'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'esto', 'mí', 'antes',
    'algunos', 'qué', 'nada', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'vosotros', 'vosotras',
    'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro',
    'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estos', 'estas',
    'aquel', 'aquella', 'aquellos', 'aquellas', 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté',
    'estés', 'estemos', 'estéis', 'estén', 'estar', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis',
    'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses',
    'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada', 'estados', 'estadas', 'estad', 'he',
    'has', 'ha', 'hemos', 'habéis', 'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá',
    'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 'había', 'habías',
    'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera',
    'hubieras', 'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen',
    'habiendo', 'habido', 'habida', 'habidos', 'habidas', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas',
    'seamos', 'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería', 'serías', 'seríamos',
    'seríais', 'serían', 'era', 'eras', 'éramos', 'erais', 'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis',
    'fueron', 'fuera', 'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen',
    'sintiendo', 'sentido', 'sentida', 'sentidos', 'sentidas', 'siente', 'sentid', 'tengo', 'tienes', 'tiene',
    'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás', 'tendrá',
    'tendremos', 'tendréis', 'tendrán', 'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía',
    'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron',
    'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis',
    'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'
]

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

def get_word_frequency(transcript_text, filter_stop_words=False):
    """Extract words and count their frequency"""
    # Convert to lowercase and extract words (letters only)
    words = re.findall(r'\b[a-záéíóúñü]+\b', transcript_text.lower())
    
    if filter_stop_words:
        words = [word for word in words if word not in SPANISH_STOP_WORDS]

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
        filter_stop_words = data.get('filterStopWords', False)
        
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
        word_frequency = get_word_frequency(full_text, filter_stop_words)
        
        # --- Save to Database ---
        # Check if video already exists
        video = Video.query.get(video_id)
        if not video:
            # Attempt to get video title (optional, might fail)
            try:
                # This is a bit of a workaround to get video details without a full API client
                transcript_list = YouTubeTranscriptApi().list_transcripts(video_id)
                video_title = transcript_list._video_title or "Title not found"
            except Exception:
                video_title = "Title not available"

            video = Video(id=video_id, title=video_title)
            db.session.add(video)

        # Add or update words
        for word_text, freq in word_frequency:
            word = Word.query.filter_by(text=word_text).first()
            if word:
                word.frequency += freq
            else:
                new_word = Word(text=word_text, frequency=freq)
                db.session.add(new_word)
        
        db.session.commit()
        # --- End of Database Logic ---

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

@app.route('/words')
def words_list():
    all_words = Word.query.order_by(Word.frequency.desc()).all()
    return render_template('words.html', words=all_words)

if __name__ == '__main__':
    app.run(debug=True)