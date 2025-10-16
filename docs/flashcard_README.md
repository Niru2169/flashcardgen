# LearnQuest: A Gamified Learning Platform

This document provides an overview of the LearnQuest project, including its features, database schema, application logic, and file structure.

## Features Implemented

*   **User Authentication:**
    *   Users can sign up for a new account, log in, and log out.
    *   The application uses Django's built-in authentication system.

*   **Dashboard:**
    *   A central dashboard serves as the main landing page after login.
    *   A collapsible sidebar provides navigation to all the main features of the application.

*   **Stats Page:**
    *   Displays the user's current stats, including:
        *   Health Points (HP)
        *   Mana
        *   Experience Points (XP)
        *   Level
        *   Coins
    *   The stats are displayed using progress bars for a more visual representation.

*   **Flashcard Generator:**
    *   Users can enter a URL to a webpage.
    *   The application will scrape the text content from the URL and generate a downloadable `.txt` file, which can be used as a starting point for creating flashcards.

*   **Notes Page (SWOT Analysis):**
    *   Provides a 2x2 grid for users to perform a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.
    *   The notes are saved to the database and are unique to each user.

## Database Schema Design

The database schema is defined in `core/models.py` and consists of the following models:

*   **`User` (Django's built-in model):**
    *   Stores the essential user authentication data like username, password, and email.

*   **`Student`:**
    *   Extends the built-in `User` model with a one-to-one relationship.
    *   Stores the gamified stats for each user.
    *   **Fields:**
        *   `user`: A one-to-one link to the `User` model.
        *   `xp`: Integer, defaults to 0.
        *   `hp`: Integer, defaults to 100.
        *   `level`: Integer, defaults to 1.
        *   `coins`: Integer, defaults to 0.
        *   `mana`: Integer, defaults to 0.

*   **`Quiz`:**
    *   Designed to store information about quizzes.
    *   **Fields:**
        *   `title`: A character field for the quiz title.
        *   `max_score`: An integer field for the maximum possible score.

*   **`Score`:**
    *   Stores the scores that students achieve on quizzes.
    *   **Fields:**
        *   `student`: A foreign key to the `Student` model.
        *   `quiz`: A foreign key to the `Quiz` model.
        *   `score_achieved`: An integer field for the score the student got.
        *   `submission_date`: A datetime field that automatically records when the score was submitted.

*   **`SWOT`:**
    *   Stores the SWOT analysis notes for each student.
    *   **Fields:**
        *   `student`: A one-to-one link to the `Student` model.
        *   `strengths`: A text field for strengths.
        *   `weaknesses`: A text field for weaknesses.
        *   `opportunities`: A text field for opportunities.
        *   `threats`: A text field for threats.

## Application Logic

The core logic of the application is handled in `core/views.py`. Here's a breakdown of the main functions:

*   **`signup(request)`:** Handles user registration. When a user signs up, a new `User` is created, and a corresponding `Student` object is created and linked to it.
*   **`login_view(request)`:** Handles user login using Django's authentication framework.
*   **`logout_view(request)`:** Logs the user out and redirects them to the login page.
*   **`dashboard(request)`:** Renders the main dashboard page.
*   **`stats_page(request)`:** Fetches the `Student` object for the currently logged-in user and passes it to the `stats.html` template to display the stats.
*   **`flashcard_generator(request)`:** Handles the web scraping functionality. It takes a URL from a form, uses the `requests` and `BeautifulSoup` libraries to extract the text, and returns it as a downloadable text file.
*   **`notes_page(request)`:** Handles the SWOT analysis notes. It retrieves the user's existing notes or creates a new `SWOT` object if one doesn't exist. It also handles saving the notes when the user submits the form.

## File Layout

The project is organized into the following main directories and files:

*   **`learnquest/`**: The main Django project directory.
    *   `settings.py`: Contains all the project settings, including database configuration, installed apps, and middleware.
    *   `urls.py`: The main URL configuration file for the project. It includes the URLs from the `core` app.

*   **`core/`**: The main application directory.
    *   `models.py`: Defines the database models (`Student`, `Quiz`, `Score`, `SWOT`).
    *   `views.py`: Contains the application's view functions (the logic).
    *   `urls.py`: Contains the URL patterns specific to the `core` app.
    *   **`templates/core/`**: Contains the HTML templates for the application.
        *   `base.html`: The base template that defines the overall layout, including the top bar and sidebar. All other templates extend this one.
        *   `login.html`, `signup.html`: Templates for the authentication pages.
        *   `dashboard.html`, `stats.html`, `flashcards.html`, `notes.html`: Templates for the main feature pages.
    *   **`migrations/`**: Contains the database migration files that Django uses to track changes to the database schema.

*   **`manage.py`**: A command-line utility that lets you interact with the Django project.
*   **`README.md`**: This file, providing documentation for the project.
