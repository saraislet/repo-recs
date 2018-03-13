# Repo Recommender

[![Coverage Status](https://coveralls.io/repos/github/Saraislet/repo-recs/badge.svg?branch=master)](https://coveralls.io/github/Saraislet/repo-recs?branch=master)

See [Product Requirements Document](https://docs.google.com/document/d/1Y0B8MoOj3lp8YS9QbsYC92vsY3Bjg_gF1gXMOUPOnRw) on Google Docs.

The Repository Recommender system uses a Github-authenticated user's stars as machine learning features to recommend other repositories to follow, using low-rank matrix approximation.

![Repo Recommender Demo Screencast](https://media.giphy.com/media/1jWBZonnxK4WgOpxhR/giphy.gif)

## Built With
* Languages: Python, SQL (PostGRES), JavaScript, HTML, CSS
* Frameworks: Flask, Jinja, [React](https://reactjs.org/), [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/)
* [W3.CSS](https://www.w3schools.com/w3css/)
* Libraries:
  * [PyGithub](http://pygithub.readthedocs.io)
  * [Progress](https://github.com/verigak/progress/) by @verigak
  * [SciPy SVDS](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.svds.html), [pandas](https://pandas.pydata.org/), [numpy](http://www.numpy.org/)
  * [d3](https://d3js.org/)

### Key algorithms/methods
* [Low-rank matrix approximation](https://en.wikipedia.org/wiki/Low-rank_matrix_approximations)
  * [Singular Value Decomposition](https://en.wikipedia.org/wiki/Singular-value_decomposition)

## File structure

    .
    ├── api_utils.py             # Helper functions interfacing with api
    ├── config.py                # Configuration variables
    ├── db_utils.py              # Helper functions interfacing with the database
    ├── experiments.ipynb        # Jupyter NB including SVD tests
    ├── model.py                 # Flask-SQLAlchemy classes for the data model
    ├── requirements.txt         # Defines requirements
    ├── rec.py                   # Recommender system functions
    ├── server.py                # Flask routes
    ├── test_db_utils.py         # Tests for db_utils.py
    ├── test_model.py            # Tests for model.py
    ├── test_rec.py              # Tests for rec.py
    ├── test_server.py           # Tests for server.py and front-end
    ├── test_utils.py            # Tests for utils.py
    ├── timelog.py               # Decorator for logging
    ├── update_pkey_seqs.py      # Script by Katie Byers to introspect DB & set autoincrementing primary keys
    ├── utils.py                 # Helper methods for server.py
    │
    ├── static
    │   ├── graph.js             # d3 for graph on homepage
    │   ├── recs.jsx             # AJAX requests and functions to render React components
    │   ├── repo.jsx             # React components for displaying repositories
    │   └── style.css            # CSS
    │
    └── templates
        ├── base.html            # Template (includes navbar, header, & footer)
        ├── home.html            # Homepage
        ├── repo_recs.html       # Repo recommendations rendered with React components
        └── user_info.html       # Details about a user and their repositories

## TODO:
* Plan features for 2.0:
  * Add AJAX to follow users
  * Write route to show stars of a user
  * Add like/dislike feature to "Like" a repo without starring
    * I.e., "see more like this" / "see less like this"
  * Write API requests instead of using PyGithub?
  * Build queue table and handlers instead of crawling recursively
  * Expand async calls to dynamically increase crawl breadth on login

## Resources used:.
* [SciPy Sparse Single Value Decomposition](http://scipy.github.io/devdocs/generated/scipy.sparse.linalg.svds.html#scipy.sparse.linalg.svds)
* [Matrix Factorization for Movie Recommendations in Python](https://beckernick.github.io/matrix-factorization-recommender/)
* [How the Facebook content placeholder works](https://cloudcannon.com/deconstructions/2014/11/15/facebook-content-placeholder-deconstruction.html)
* [d3](http://bl.ocks.org/mbostock/1153292)

## Acknowledgements
* [Katie Byers @lobsterkatie](https://github.com/lobsterkatie) — Wrote update_pkey_seqs.py

## Author
* [Sarai Rosenberg](https://sar.ai) [@Saraislet](https://github.com/Saraislet) — Software engineer and mathematician, looking for opportunities
