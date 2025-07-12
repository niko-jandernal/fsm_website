# FSM – Fashion Social Media Platform 
*An interactive platform built with Django, designed specifically for fashion enthusiasts.*
## 1. About the Project
FSM (Fashion Social Media) is a fashion-focused social media platform I built as my projects during the Bachelor's and Masters dissertations of my Computer Science degree at Newcastle University.

The idea came from a simple observation: most social media platforms are cluttered with noise and don’t offer dedicated spaces for communities like fashion lovers to interact meaningfully. FSM aims to fill that gap — offering a cleaner, more focused space where users can:

- Share fashion photos
- Create and vote in interactive polls
- Participate in topic-based discussions
- Curate themed photo albums

The platform is built using the Django web framework and incorporates frontend optimisations like lazy loading, infinite scroll, and AJAX interactions for a smooth and responsive user experience.

## 2. Key Features

### 2.1 Albums  
Users can create and manage photo albums around themes like “Streetwear” or “Runway Looks”.  
- Add, remove, and reorder images  
- Responsive layouts and lazy loading

### 2.2 Discussions  
Structured discussion boards support fashion talk, advice, and community engagement.  
- Threaded conversations under named topics  
- Likes and real-time replies

### 2.3 Polls  
Fashion-based questions can be posted and voted on by the community.  
- Real-time bar chart updates  
- AJAX voting and commenting  
- Prevents duplicate voting

### 2.4 Admin Dashboard  
Admins have full moderation capabilities via Django’s built-in admin panel.

---

## 3. Technology Used

- **Framework**: Django 5.x (Python)
- **Frontend**: HTML, Bootstrap, JavaScript (AJAX & Intersection Observer)
- **Database**: SQLite (local dev)
- **Performance**: Native lazy loading, static compression, infinite scroll
- **Testing**: Unit tests via Django’s test framework, Lighthouse audits for performance

---

## 4. How to Run This Project Locally

Here’s how to get it running on your own machine:

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git
- A code editor (like VS Code or PyCharm)

### Setup Instructions

### 1. Clone the repository
git clone https://github.com/niko-jandernal/fsm_webiste.git
cd fsm_webiste

### 2. Create a virtual environment
python -m venv env
source env/bin/activate   # On Windows: env\Scripts\activate

### 3. Install the dependencies
pip install -r requirements.txt

### 4. Apply database migrations
python manage.py migrate

### 5. Create a superuser account for admin access
python manage.py createsuperuser

### 6. Start the development server
python manage.py runserver
