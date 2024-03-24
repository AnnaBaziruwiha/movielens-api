# MovieLens API

The MovieLens API is a Django REST Framework application that provides endpoints for managing movies, genres, and user ratings. It includes functionality for loading the Movielens 20M dataset into the database and exporting the movies list to a CSV file.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- pip
- Virtualenv (optional)
- PostgreSQL

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/AnnaBaziruwiha/movielens-api.git
   cd movielens-api
   ```

2. (Optional) Create a virtual environment and activate it:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows, use:

   ```
   python3 -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables:

   Create a `.env` file in the root directory of the project and add the following variables:

   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_USER=your_database_user
   DATABASE_PASSWORD=your_database_password
   ```

   Replace `your_secret_key`, `your_database_user`, and `your_database_password` with your actual Django secret key and PostgreSQL credentials.

5. Initialize the database:

   ```
   python manage.py migrate
   ```

6. Load the Movielens 20M dataset (this might take a while):

   ```
   python manage.py load_movielens_data
   ```

### Running the Application

1. Start the Django development server:

   ```
   python manage.py runserver
   ```

2. Visit `http://localhost:8000` in your web browser to start using the API.

### Using the Custom Management Commands

- **Load Movielens Data:**

  To load the Movielens 20M dataset into your database, run:

  ```
  python manage.py load_movielens_data
  ```

- **Export Movies to CSV:**

  To export the movies list to a CSV file, run:

  ```
  python manage.py export_movies
  ```

  This will create a CSV file in the root directory of your project.

## Running Tests

To run the automated tests for this project, use:

```
python manage.py test
```

## Built With

- [Django](https://www.djangoproject.com/) - The web framework used
- [Django REST Framework](https://www.django-rest-framework.org/) - Toolkit for building Web APIs
- [PostgreSQL](https://www.postgresql.org/) - The database used
- [drf-yasg](https://drf-yasg.readthedocs.io/) - Yet another Swagger generator
