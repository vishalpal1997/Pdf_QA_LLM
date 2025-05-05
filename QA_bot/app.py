from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import fitz  # PyMuPDF
import subprocess
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.secret_key = 'your-secret-key-here'  # Needed for session

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(filepath):    
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_llama(context, question, conversation_history=None):
    # Build the prompt with context and conversation history
    prompt = f"Document Context:\n{context}\n\n"
    
    if conversation_history:
        prompt += "Conversation History:\n"
        for entry in conversation_history:
            prompt += f"Q: {entry['question']}\nA: {entry['answer']}\n\n"
    
    prompt += f"New Question: {question}\n\nAnswer:"
    
    result = subprocess.run(
        ['ollama', 'run', 'llama3', prompt],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout

def delete_uploaded_file():
    """Delete the currently uploaded PDF file if it exists"""
    if 'uploaded_file' in session and session['uploaded_file']:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['uploaded_file'])
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize session variables if they don't exist
    if 'conversation' not in session:
        session['conversation'] = []
    if 'uploaded_file' not in session:
        session['uploaded_file'] = None
    if 'document_text' not in session:
        session['document_text'] = None
    
    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return render_template('index.html', error="No file selected")
            
            if file and allowed_file(file.filename):
                # Delete previous file if exists
                delete_uploaded_file()
                
                # Clear previous conversation when new file is uploaded
                session['conversation'] = []
                session['uploaded_file'] = None
                session['document_text'] = None
                
                # Save the new file
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract and store text
                text = extract_text_from_pdf(filepath)
                session['document_text'] = text
                session['uploaded_file'] = filename
                
                return render_template('index.html', 
                                     text_extracted=True,
                                     filename=file.filename,
                                     conversation=session['conversation'])
        
        # Handle question submission
        if 'question' in request.form and session['document_text']:
            question = request.form['question'].strip()
            if question:
                # Get answer from LLaMA
                answer = ask_llama(
                    session['document_text'], 
                    question,
                    session['conversation']
                )
                
                # Add to conversation history
                session['conversation'].append({
                    'question': question,
                    'answer': answer
                })
                
                return render_template('index.html',
                                     text_extracted=True,
                                     filename=session['uploaded_file'],
                                     conversation=session['conversation'])
    
    return render_template('index.html',
                         text_extracted=session['document_text'] is not None,
                         filename=session['uploaded_file'],
                         conversation=session['conversation'])

@app.route('/clear', methods=['POST'])
def clear_conversation():
    # Clear the conversation history completely
    session['conversation'] = []
    session.modified = True  # Ensure the session is saved
    return jsonify({'status': 'success'})

@app.route('/delete_pdf', methods=['POST'])
def delete_pdf():
    """Delete the current PDF and reset the session"""
    try:
        # Delete the uploaded file
        delete_uploaded_file()
        
        # Clear all session data
        session.clear()
        
        return jsonify({'status': 'success', 'message': 'PDF deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)