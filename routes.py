import os
import logging
import uuid
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app import app, db, socketio
from models import Admin, Question, Option, Vote
from forms import LoginForm, ImageUploadForm, VoteForm, ManualQuestionForm
from utils import extract_text_from_image, parse_options

# Login and Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('admin'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    image_form = ImageUploadForm()
    manual_form = ManualQuestionForm()
    
    if image_form.validate_on_submit():
        try:
            # Process question image
            question_text = extract_text_from_image(image_form.question_image.data, 'question')
            if question_text.startswith('Error:'):
                flash(f'Failed to process question image: {question_text}', 'danger')
                return redirect(url_for('admin'))
            
            # Save question image if it's a diagrammatic question
            question_image_filename = None
            if image_form.is_diagram.data:
                # Create uploads directory if it doesn't exist
                if not os.path.exists('static/uploads'):
                    os.makedirs('static/uploads')
                
                question_image = image_form.question_image.data
                question_image_filename = secure_filename(f"question_{uuid.uuid4().hex}.jpg")
                question_image.save(os.path.join('static/uploads', question_image_filename))
            
            # Process options image
            options_text = extract_text_from_image(image_form.options_image.data, 'options')
            if options_text.startswith('Error:'):
                flash(f'Failed to process options image: {options_text}', 'danger')
                return redirect(url_for('admin'))
            
            # Parse the options into a list
            option_list = parse_options(options_text)
            
            if image_form.answer_type.data == 'option' and len(option_list) < 2:
                flash('At least two options are required for multiple choice questions.', 'warning')
                return redirect(url_for('admin'))
            
            # Deactivate all current active questions
            active_questions = Question.query.filter_by(active=True).all()
            for question in active_questions:
                question.active = False
            
            # Create new question
            new_question = Question(
                text=question_text, 
                active=True,
                question_image_filename=question_image_filename,
                is_diagram=image_form.is_diagram.data,
                answer_type=image_form.answer_type.data
            )
            db.session.add(new_question)
            db.session.flush()  # Assign ID without committing
            
            # Create options for the question if it's multiple choice
            if image_form.answer_type.data == 'option':
                for option_text in option_list:
                    new_option = Option(text=option_text, question_id=new_question.id)
                    db.session.add(new_option)
            
            # Commit changes
            db.session.commit()
            
            flash('Question and options created successfully!', 'success')
            
            # Emit socket event to update all clients
            question_data = {
                'id': new_question.id,
                'text': new_question.text,
                'answer_type': new_question.answer_type,
                'options': [{'id': opt.id, 'text': opt.text, 'votes': 0} for opt in new_question.options] if new_question.answer_type == 'option' else []
            }
            socketio.emit('question_update', question_data)
            
            return redirect(url_for('admin'))
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating question from images: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin'))
    
    elif manual_form.validate_on_submit():
        try:
            # Save question image if provided
            question_image_filename = None
            if manual_form.question_image.data:
                # Create uploads directory if it doesn't exist
                if not os.path.exists('static/uploads'):
                    os.makedirs('static/uploads')
                
                question_image = manual_form.question_image.data
                question_image_filename = secure_filename(f"question_{uuid.uuid4().hex}.jpg")
                question_image.save(os.path.join('static/uploads', question_image_filename))
            
            # Deactivate all current active questions
            active_questions = Question.query.filter_by(active=True).all()
            for question in active_questions:
                question.active = False
            
            # Create new question
            new_question = Question(
                text=manual_form.question_text.data, 
                active=True,
                question_image_filename=question_image_filename,
                is_diagram=manual_form.is_diagram.data,
                answer_type=manual_form.answer_type.data
            )
            db.session.add(new_question)
            db.session.commit()
            
            flash('Question created successfully! You can now add options if needed.', 'success')
            
            # No socket event emission yet since we need options for multiple choice questions
            return redirect(url_for('admin'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating manual question: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin'))
    
    # Get all questions for display, most recent first
    questions = Question.query.order_by(Question.created_at.desc()).all()
    
    return render_template('admin.html', 
                          image_form=image_form, 
                          manual_form=manual_form, 
                          questions=questions)

@app.route('/admin/activate/<int:question_id>')
@login_required
def activate_question(question_id):
    try:
        # Deactivate all questions first
        Question.query.update({Question.active: False})
        
        # Activate the selected question
        question = Question.query.get_or_404(question_id)
        question.active = True
        db.session.commit()
        
        flash(f'Question "{question.text}" activated successfully!', 'success')
        
        # Emit socket event to update all clients
        question_data = {
            'id': question.id,
            'text': question.text,
            'options': [{'id': opt.id, 'text': opt.text, 'votes': opt.vote_count} for opt in question.options]
        }
        socketio.emit('question_update', question_data)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error activating question: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:question_id>')
@login_required
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
        
        # If there's still an active question, emit update
        active_question = Question.query.filter_by(active=True).first()
        if active_question:
            question_data = {
                'id': active_question.id,
                'text': active_question.text,
                'answer_type': active_question.answer_type,
                'options': [{'id': opt.id, 'text': opt.text, 'votes': opt.vote_count} for opt in active_question.options]
            }
            socketio.emit('question_update', question_data)
        else:
            # If no active question, emit empty data
            socketio.emit('question_update', {'id': None})
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/admin/manage_options/<int:question_id>', methods=['GET', 'POST'])
@login_required
def manage_options(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        try:
            option_text = request.form.get('option_text')
            if not option_text:
                flash('Option text is required', 'warning')
                return redirect(url_for('manage_options', question_id=question_id))
            
            # Create new option
            new_option = Option(
                text=option_text,
                question_id=question_id
            )
            db.session.add(new_option)
            db.session.commit()
            
            flash('Option added successfully!', 'success')
            
            # Update active question if this is the active one
            if question.active:
                question_data = {
                    'id': question.id,
                    'text': question.text,
                    'answer_type': question.answer_type,
                    'options': [{'id': opt.id, 'text': opt.text, 'votes': opt.vote_count} for opt in question.options]
                }
                socketio.emit('question_update', question_data)
            
            return redirect(url_for('manage_options', question_id=question_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding option: {str(e)}', 'danger')
    
    return render_template('manage_options.html', question=question)

@app.route('/admin/delete_option/<int:option_id>')
@login_required
def delete_option(option_id):
    option = Option.query.get_or_404(option_id)
    question_id = option.question_id
    question = Question.query.get(question_id)
    
    try:
        db.session.delete(option)
        db.session.commit()
        flash('Option deleted successfully!', 'success')
        
        # Update active question if this is the active one
        if question and question.active:
            question_data = {
                'id': question.id,
                'text': question.text,
                'answer_type': question.answer_type,
                'options': [{'id': opt.id, 'text': opt.text, 'votes': opt.vote_count} for opt in question.options]
            }
            socketio.emit('question_update', question_data)
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting option: {str(e)}', 'danger')
    
    return redirect(url_for('manage_options', question_id=question_id))

# Voter Routes
@app.route('/')
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    # Ensure user has a session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Get active questions
    active_questions = Question.query.filter_by(active=True).all()
    
    if not active_questions:
        return render_template('vote.html', questions=None)
    
    # Check if user already voted on these questions
    existing_votes = Vote.query.filter(
        Vote.session_id == session['session_id'],
        Vote.question_id.in_([q.id for q in active_questions])
    ).all()
    existing_vote_question_ids = {vote.question_id for vote in existing_votes}
    
    # Create vote forms for each active question
    forms = []
    for question in active_questions:
        form = VoteForm()
        if question.answer_type == 'option':
            form.option.choices = [(option.id, option.text) for option in question.options]
        forms.append((question, form))
    
    if request.method == 'POST':
        for question, form in forms:
            if form.validate_on_submit():
                try:
                    # Handle different answer types
                    if question.answer_type == 'option':
                        # Get the selected option to check if it belongs to the active question
                        selected_option = Option.query.get(form.option.data)
                        if not selected_option or selected_option.question_id != question.id:
                            flash('Invalid option selected!', 'danger')
                            return redirect(url_for('vote'))
                        
                        # Create a new vote with session ID for multiple choice
                        new_vote = Vote(
                            option_id=form.option.data,
                            session_id=session['session_id'],
                            question_id=question.id
                        )
                        
                        # Emit socket event with updated vote counts for multiple choice
                        db.session.add(new_vote)
                        db.session.commit()
                        
                        option_votes = {}
                        for opt in question.options:
                            option_votes[opt.id] = len(opt.votes)
                        
                        socketio.emit('vote_update', {
                            'question_id': question.id,
                            'option_votes': option_votes
                        })
                        
                    elif question.answer_type == 'text':
                        # Validate that text input is provided
                        if not form.text_answer.data:
                            flash('Please provide an answer', 'warning')
                            return redirect(url_for('vote'))
                        
                        # Create a new vote with session ID for text answer
                        new_vote = Vote(
                            option_id=None,  # No option for text answers
                            text_answer=form.text_answer.data,
                            session_id=session['session_id'],
                            question_id=question.id
                        )
                        db.session.add(new_vote)
                        db.session.commit()
                        
                        # No need to emit option votes for text answers
                    
                    flash('Response submitted successfully!', 'success')
                    return redirect(url_for('results'))
                    
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error submitting response: {str(e)}")
                    flash(f'Error submitting response: {str(e)}', 'danger')
    
    return render_template('vote.html', forms=forms, questions=active_questions, existing_vote_question_ids=existing_vote_question_ids)

# Results Route
@app.route('/results')
def results():
    # Ensure user has a session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Get the active questions
    active_questions = Question.query.filter_by(active=True).all()
    
    if not active_questions:
        return render_template('results.html', questions=None, has_voted=False)
    
    results_data = []
    for question in active_questions:
        # Check if user has voted on this question
        user_vote = None
        if 'session_id' in session:
            user_vote = Vote.query.filter_by(
                session_id=session['session_id'],
                question_id=question.id
            ).first()
        
        # Handle results differently based on answer type
        if question.answer_type == 'option':
            # Gather vote counts for each option
            options_with_votes = []
            total_votes = 0
            user_selected_option_id = None
            
            if user_vote:
                user_selected_option_id = user_vote.option_id
            
            for option in question.options:
                vote_count = len(option.votes)
                total_votes += vote_count
                options_with_votes.append({
                    'id': option.id,
                    'text': option.text,
                    'votes': vote_count,
                    'is_user_vote': option.id == user_selected_option_id,
                    'is_image_option': option.is_image_option,
                    'image_filename': option.image_filename
                })
            
            # Calculate percentages
            for option in options_with_votes:
                if total_votes > 0:
                    option['percentage'] = round((option['votes'] / total_votes) * 100)
                else:
                    option['percentage'] = 0
            
            # Get the user's selected answer for display
            user_answer = None
            if user_vote and user_vote.option_id:
                selected_option = Option.query.get(user_vote.option_id)
                if (selected_option):
                    user_answer = selected_option.text
            
            results_data.append({
                'question': question,
                'options': options_with_votes,
                'total_votes': total_votes,
                'has_voted': user_vote is not None,
                'user_answer': user_answer,
                'text_answers': None
            })
        
        elif question.answer_type == 'text':
            # For text-based answers, collect all answers
            text_votes = Vote.query.filter_by(question_id=question.id).order_by(Vote.created_at.desc()).all()
            text_answers = []
            
            for vote in text_votes:
                if vote.text_answer:  # Only include votes with text answers
                    text_answers.append({
                        'text': vote.text_answer,
                        'is_user_vote': vote.session_id == session.get('session_id')
                    })
            
            # Get the user's entered text answer
            user_answer = None
            if user_vote:
                user_answer = user_vote.text_answer
            
            results_data.append({
                'question': question,
                'options': None,
                'total_votes': len(text_answers),
                'has_voted': user_vote is not None,
                'user_answer': user_answer,
                'text_answers': text_answers
            })
    
    return render_template('results.html', results_data=results_data)

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    logging.debug('Client connected')
    
    # Send current question data to the newly connected client
    active_question = Question.query.filter_by(active=True).first()
    if active_question:
        question_data = {
            'id': active_question.id,
            'text': active_question.text,
            'answer_type': active_question.answer_type,
            'is_diagram': active_question.is_diagram,
            'question_image_filename': active_question.question_image_filename,
            'options': [
                {
                    'id': opt.id, 
                    'text': opt.text, 
                    'votes': len(opt.votes),
                    'is_image_option': opt.is_image_option,
                    'image_filename': opt.image_filename
                } for opt in active_question.options
            ]
        }
        # Individual emit to the client that just connected
        socketio.emit('question_update', question_data)

@socketio.on('disconnect')
def handle_disconnect():
    logging.debug('Client disconnected')

# Background task to check for new questions every 10 seconds
def check_for_new_questions():
    last_question_id = None
    while True:
        active_question = Question.query.filter_by(active=True).first()
        if active_question and active_question.id != last_question_id:
            last_question_id = active_question.id
            socketio.emit('new_question', {'id': active_question.id, 'text': active_question.text})
        socketio.sleep(10)

# Start the background task
socketio.start_background_task(check_for_new_questions)

# Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="404 - Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="500 - Internal Server Error"), 500
