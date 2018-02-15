# Repository Recommendations

See [Product Requirements Document](https://docs.google.com/document/d/1Y0B8MoOj3lp8YS9QbsYC92vsY3Bjg_gF1gXMOUPOnRw) on Google Docs.

The Repository Recommendation engine uses a Github-authenticated user's stars, watches, and follows as features to recommend other repositories or users to follow, using low-rank matrix approximation (may later add kNN or collaborative filtering with additional features).

## File structure

    .
    ├── experiments.ipynb        # Jupyter NB including SVD tests
    ├── model.py                 # Flask-SQLAlchemy classes for the data model
    ├── requirements.txt         # Defines requirements
    ├── server.py                # Flask routes
    ├── test_model.py            # Tests for model.py
    ├── test_utils.py            # Tests for utils.py
    ├── update_pkey_seqs.py      # Script by [Katie Byers](https://github.com/lobsterkatie) to introspect DB and set autoincrementing primary keys appropriately
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
* Complete MVP:
  * Add recommendation algorithm
  * Add route for recs
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
