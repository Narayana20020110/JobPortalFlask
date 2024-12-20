from flask import render_template, redirect, url_for, request, flash,send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from models import Seeker, Provider
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def register_routes(app, db):
    # Home Route
    @app.route('/')
    def home():
        return render_template('index.html')

    # Register Route (Handles Seeker and Provider based on 'role' param)
    @app.route('/register/<role>', methods=['GET', 'POST'])
    def register(role):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            if role == 'seeker':
                new_user = Seeker(email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('dashboard'))

            elif role == 'provider':
                website_url = request.form['website_url']
                new_user = Provider(email=email, password=hashed_password, website_url=website_url)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('dashboard'))

            flash('Registration failed. Please try again.', 'danger')

        return render_template('register.html', role=role)

    # Login Route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Check if the user is a job seeker
            seeker = Seeker.query.filter_by(email=email).first()
            if seeker and check_password_hash(seeker.password, password):
                login_user(seeker)
                return redirect(url_for('dashboard'))

            # Check if the user is a job provider
            provider = Provider.query.filter_by(email=email).first()
            if provider and check_password_hash(provider.password, password):
                login_user(provider)
                return redirect(url_for('dashboard'))

            flash('Invalid credentials. Please try again.', 'danger')

        return render_template('login.html')

      

# Job Listings Dashboard for Seeker
@app.route('/jobslistingdashboard')
@login_required
def jobs_listing_dashboard():
    # Check if the current user is a seeker
    if isinstance(current_user, Seeker):
        jobs = Jobs.query.all()  # Fetch all jobs
        return render_template('jobslistingdashboard.html', jobs=jobs)
    else:
        return redirect(url_for('home'))



# Apply for a Job - Show Submission Form
@app.route('/apply/<int:jid>', methods=['GET', 'POST'])
@login_required
def apply_job(jid):
    # Check if the current user is a seeker
    if isinstance(current_user, Seeker):
        job = Jobs.query.get_or_404(jid)  # Get the job by ID
        if request.method == 'POST':
            email = request.form['email']
            file = request.files['file']
            
            # Handle resume file
            if file:
                resume = secure_filename(file.filename)
                UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
                filepath = os.path.join(UPLOAD_FOLDER, resume)
                file.save(filepath)

                # Create a new submission
                submission = Submissions(seeker_id=current_user.id, job_id=job.id, email=email, resume=resume)
                db.session.add(submission)
                db.session.commit()

                flash('Your application has been submitted successfully.', 'success')
                return redirect(url_for('jobs_listing_dashboard'))

        return render_template('submission_form.html', job=job)
    else:
        return redirect(url_for('home'))

   @app.route('/jobsdashboard', methods=['GET', 'POST'])
@login_required
def jobs_dashboard():
    # Check if the current user is a provider
    if isinstance(current_user, Provider):
        # Handle job deletion
        if request.method == 'POST' and 'delete_job' in request.form:
            job_id = request.form.get('delete_job')
            job_to_delete = Jobs.query.get(job_id)
            if job_to_delete and job_to_delete.cemail == current_user.email:
                db.session.delete(job_to_delete)
                db.session.commit()
                flash('Job deleted successfully.', 'success')
            else:
                flash('You can only delete your own jobs.', 'danger')
            return redirect(url_for('jobs_dashboard'))

        # Fetch jobs posted by the current provider using their email
        jobs = Jobs.query.filter_by(cemail=current_user.email).all()
        return render_template('jobsdashboard.html', jobs=jobs)
    else:
        return redirect(url_for('home'))

# Job Posting Form
@app.route('/postjob', methods=['GET', 'POST'])
@login_required
def post_job():
    if isinstance(current_user, Provider):
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            cemail = current_user.email  # Use the current user's email as the company email

            # Create a new job entry
            new_job = Jobs(title=title, description=description, cemail=cemail, provider_id=current_user.id)
            db.session.add(new_job)
            db.session.commit()

            flash('Job posted successfully.', 'success')
            return redirect(url_for('jobs_dashboard'))

        return render_template('postjob.html')
    else:
        return redirect(url_for('home'))
@app.route('/matchedprofiles', methods=['GET'])
@login_required
def matched_profiles():
    # Check if the current user is a provider
    if isinstance(current_user, Provider):
        # Get all jobs posted by the current provider
        provider_jobs = Jobs.query.filter_by(cemail=current_user.email).all()
        provider_job_ids = [job.id for job in provider_jobs]

        # Get all submissions for the provider's jobs
        matched_submissions = Submissions.query.filter(Submissions.jid.in_(provider_job_ids)).all()

        return render_template('matchedprofiles.html', submissions=matched_submissions)
    else:
        return redirect(url_for('home'))


@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_resume(filename):
    # Ensure the user is authorized to access this functionality
    if isinstance(current_user, Provider):
        return send_from_directory('uploads', filename, as_attachment=True)
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))
    # Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))
