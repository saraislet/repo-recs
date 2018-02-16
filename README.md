# Repository Recommendations

See [Product Requirements Document](https://docs.google.com/document/d/1Y0B8MoOj3lp8YS9QbsYC92vsY3Bjg_gF1gXMOUPOnRw) on Google Docs.

The Repository Recommendation engine uses a Github-authenticated user's stars, watches, and follows as features to recommend other repositories or users to follow, using low-rank matrix approximation (may later add kNN or collaborative filtering with additional features).

## Built With
* Languages: Python, SQL (PostGRES), HTML, CSS
* Frameworks: Flask, Jinja
* [W3 CSS](https://www.w3schools.com/w3css/)
* Libraries:
  * [jQuery](https://jquery.com/)
  * [PyGithub](http://pygithub.readthedocs.io)
  * [Progress](https://github.com/verigak/progress/) by @verigak
  * [scikit-learn](http://scikit-learn.org/stable/)
    * [SVDS](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.svds.html)
  * [pandas](https://pandas.pydata.org/)
  * [numpy](http://www.numpy.org/)

### Key algorithms/methods
* [Low-rank matrix approximation](https://en.wikipedia.org/wiki/Low-rank_matrix_approximations)
  * [Singular Value Decomposition](https://en.wikipedia.org/wiki/Singular-value_decomposition)

## File structure

    .
    ├── experiments.ipynb        # Jupyter NB including SVD tests
    ├── model.py                 # Flask-SQLAlchemy classes for the data model
    ├── requirements.txt         # Defines requirements
    ├── server.py                # Flask routes
    ├── test_model.py            # Tests for model.py
    ├── test_utils.py            # Tests for utils.py
    ├── update_pkey_seqs.py      # Script by Katie Byers to introspect DB & set autoincrementing primary keys
    ├── utils.py                 # Helper methods for server.py
    │
    ├── static
    │   └── css
    │       └── style.css
    │
    └── templates
        ├── base.html            # Template (includes navbar, header, & footer)
        ├── home.html            # Homepage
        └── user_info.html       # Details about a user and their repositories

## TODO:
* Plan additional features for 1.0:
  * Refine UI
  * Build React components for showing repos and users
  * Add AJAX to star/watch/follow
  * Add AJAX to request additional suggestions
  * Improve recommendation algorithm
* Test routes
* Move config variables to config.py
* Write API requests instead of using PyGithub?
* Build queue table and handlers instead of crawling recursively
* Set depth of crawl in data model on set_last_crawled_in_user/repo

## Acknowledgements
* [Katie Byers @lobsterkatie](https://github.com/lobsterkatie) — Wrote update_pkey_seqs.py

## Author
* [Sarai Rosenberg](https://sar.ai) [@Saraislet](https://github.com/Saraislet) — Software engineer and mathematician, looking for opportunities
