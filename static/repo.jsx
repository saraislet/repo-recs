class RepoList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {data: [],
                  requestSent: false,
                  count: 9};

    this.handleScroll = this.handleScroll.bind(this)
    this.getRepoRecs = this.getRepoRecs.bind(this)
    this.handleData = this.handleData.bind(this)
  }

  componentDidMount() {
    let repos = this.props.repos;
    let listRepos = repos.map( (repo) => buildRepo(repo) );
    this.setState({data: listRepos});

    window.addEventListener('scroll', this.handleScroll);
    // this.getRepoRecs();
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  }

  getRepoRecs() {
    console.log(`getRepoRecs called; requesting page ${pageNumber} with code ${this.props.code}`);
    this.setState({requestSent: true});
    pageNumber += 1;
    // console.log(`new pageNumber: ${pageNumber}`);
    let payload = {method: "GET",
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch(`/get_repo_recs?page=${pageNumber}&code=${this.props.code}`, payload)
      .then( response => response.json() )
      .then( (data) => this.handleData(data) );
  }

  handleData(data) {
    let newData = [];

    for (let i = 0; i < data.length; i++) {
      if ( !repoIDs.has(data[i].repo_id) ) {
        newData.push(data[i]);
        repoIDs.add(data[i].repo_id);
      } else {
        // console.log(`Oops, repo ${data[i].repo_id} already shown.`);
      }

    }
    
    let oldData = this.state.data;
    let listRepos = newData.map( (repo) => buildRepo(repo) );
    newData = oldData.concat(listRepos);

    this.setState( (prevState) => (
                    {data: newData,
                     requestSent: false,
                    })
                  );
  }

  handleScroll() {
    // http://stackoverflow.com/questions/9439725/javascript-how-to-detect-if-browser-window-is-scrolled-to-bottom
    let scrollTop = (document.documentElement && document.documentElement.scrollTop) || document.body.scrollTop;
    // console.log("document.body.scrollTop: " + document.body.scrollTop)

    if (scrollTop + 1.5 * window.innerHeight > document.body.scrollHeight 
        && !this.state.requestSent && pageNumber<5) {
      // bottom reached
      // console.log("bottom reached")
      setTimeout(this.getRepoRecs, 1);
    }
  }

  render() {
    return (
      <div>
        <span onScroll={this.handleScroll.bind(this)}>
          { this.state.data }
        </span>

        {(() => {
          if (this.state.requestSent) {
            return (
              <div className="data-loading">
                Loading data...
              </div>
            );
          };
        })()}
      </div>
    );
  }
}

function buildRepo(repo) {
  let listLangs = null;
  if ( repo.langs.length > 0 ) {
    let languages = repo.langs.map( (lang) => buildLang(lang) );
    listLangs = (<ul className="repo-langs">{ languages.slice(0,3) }</ul>);
  };

  return (
    <div key={ repo.repo_id } className="w3-card-4 w3-margin repo">
      <header className="w3-container w3-blue-grey">
        <h3 className="w3-container w3-blue-grey">
          <a className="repo-owner" href={"https://www.github.com/" + repo.owner_login }>
            @{ repo.owner_login } 
          </a>
          &nbsp;/&nbsp;
          <b><a className="repo-name" href={"" + repo.url }>
            { repo.name }
          </a></b>
        </h3>
      </header>
      <div className="w3-container">
        <p className="repo-description">{ repo.description }</p>
        { listLangs }
        <div className="repo-footer">
          <Star isStarred="" repo_id={ repo.repo_id }/>
          <Dislike isDisliked="" repo_id={ repo.repo_id }/>
        </div>
      </div>
    </div>
  );
}

function buildLang(lang) {
  return (
    <li key={ lang.language_id }>{ lang.language_name } : { lang.language_bytes }</li>
  );
}

class PlaceholderList extends React.Component {
  render() {
    let arr = Array.from(Array(15).keys());
    let listPlaceholders = arr.map( (num) => buildPlaceholder(num) );
    return (
      <span>{ listPlaceholders }</span>
    );
  }
}

function buildPlaceholder(num) {
  return (
    <div key={ num } className="w3-card-4 w3-margin repo placeholder">
      <div className="placeholder-bg">
        <header className="w3-container">
          <div className="mask-bg header-top"></div>
          <div className="mask-bg header-left"></div>
          <h3 className="w3-container">
            <span className="repo-owner">
              @ 
            </span>
            <div className="mask-bg header-middle">
              &nbsp;/&nbsp;
            </div>
            <b><span className="repo-name">
              
            </span></b>
          </h3>
          <div className="mask-bg header-right"></div>
          <div className="mask-bg header-bottom"></div>
        </header>
        <div className="w3-container">
          <div className="mask-bg body-top"></div>
          <div className="mask-bg body-left"></div>
          <p className="repo-description"></p>
          <div className="mask-bg body-right"></div>
          <div className="mask-bg body2-top"></div>
          <div className="mask-bg body2-left"></div>
          <div className="mask-bg body2-right"></div>
          <div className="mask-bg body-bottom"></div>
          <div className="mask-bg langs-left"></div>
          <span className="repo-langs"></span>
          <div className="mask-bg langs-right"></div>
        </div>
      </div>
    </div>
  );
}

class Star extends React.Component {
  constructor(props) {
    super(props);
    this.state = {star: "☆",
                  isStarred: false,
                  pending: false};
  }

  handle_error(e) {
    console.error(e);
    this.setState({error: true});
  }

  add_star(e) {
    console.log("Ran add_star() on " + this.props.repo_id + "!");
    let data = {"repo_id": this.props.repo_id};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/add_star", payload)
          .then( response => response.json() )
          .then( (data) => this.update_star(data) )
          .catch( error => this.handle_error(error) )
    this.setState({pending: true});
  }

  remove_star(e) {
    console.log("Ran remove_star() on " + this.props.repo_id + "!");
    let data = {"repo_id": this.props.repo_id};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/remove_star", payload)
          .then( response => response.json() )
          .then( (data) => this.update_star(data) )
          .catch( error => this.handle_error(error) );
    this.setState({pending: true});
  }

  update_star(data) {
    if (data.Status == 204) {
      if (data.action == "add_star") {
        console.log("Successfully starred repo " + data.repo_id + ".");
        this.setState({star: "★",
                       isStarred: true,
                       pending: false,
                       error: false});
      } else if (data.action == "remove_star") {
        console.log("Successfully unstarred repo " + data.repo_id + "."); 
        this.setState({star: "☆",
                       isStarred: false,
                       pending: false,
                       error: false});
      };
    } else {
      this.setState({error: true});
      if (data.action == "add_star") {
        console.log("Unable to star repo " + data.repo_id + ".");
      } else if (data.action == "remove_star") {
        console.log("Unable to unstar repo " + data.repo_id + "."); 
      }
    };
  }

  render() {
    let isStarred = this.props.isStarred;
    let repo_id = this.props.repo_id;

    let className = "star";

    if (this.state.error) {
      className += " star-error";
    };

    if (this.state.pending) {
      className += " star-spin";
    };

    if (this.state.isStarred) {
      return (
        <span className={className} 
            onClick={this.remove_star.bind(this)} 
            repo_id={ repo_id }>
            {this.state.star}
        </span>
      );
    };

    return (
      <span className={className} 
          onClick={this.add_star.bind(this)} 
          repo_id={ repo_id }>
          {this.state.star}
      </span>
    );
  }
}


class Dislike extends React.Component {
  constructor(props) {
    super(props);
    this.state = {dislike: "&#10006;",
                  isDisliked: false,
                  pending: false};
  }

  handle_error(e) {
    console.error(e);
    this.setState({error: true});
  }

  add_dislike(e) {
    console.log("Ran add_dislike() on " + this.props.repo_id + "!");
    let data = {"repo_id": this.props.repo_id};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/add_dislike", payload)
          .then( response => response.json() )
          .then( (data) => this.update_dislike(data) )
          .catch( error => this.handle_error(error) );
    this.setState({pending: true});
  }

  remove_dislike(e) {
    console.log("Ran remove_dislike() on " + this.props.repo_id + "!");
    let data = {"repo_id": this.props.repo_id};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/remove_dislike", payload)
          .then( response => response.json() )
          .then( (data) => this.update_dislike(data) )
          .catch( error => this.handle_error(error) );
    this.setState({pending: true});
  }

  update_dislike(data) {
    if (data.Status == 204) {
      if (data.action == "add_dislike") {
        console.log("Successfully disliked repo " + data.repo_id + ".");
        this.setState({star: "X!&#10006;&#9747;!",
                       isDisliked: true,
                       pending: false,
                       error: false});
      } else if (data.action == "remove_dislike") {
        console.log("Successfully undisliked repo " + data.repo_id + "."); 
        this.setState({star: "X&#9747;&#10006;",
                       isDisliked: false,
                       pending: false,
                       error: false});
      };
    } else {
      this.setState({error: true});
      if (data.action == "add_dislike") {
        console.log("Unable to dislike repo " + data.repo_id + ".");
      } else if (data.action == "remove_dislike") {
        console.log("Unable to undislike repo " + data.repo_id + "."); 
      }
    };
  }

  render() {
    let isDisliked = this.props.isDisliked;
    let repo_id = this.props.repo_id;

    let className = "dislike";
    let iconClassName = "dislike-icon";

    if (this.state.error) {
      className += " dislike-error";
    };

    if (this.state.pending) {
      iconClassName += " star-spin";
    };

    if (this.state.isDisliked) {
      className += " dislike-true";
      return (
        <span className={className} 
            onClick={this.remove_dislike.bind(this)} 
            repo_id={ repo_id }>
            <span className="dislike-text">I dislike this repo</span>
            &nbsp;<span className="dislike-icon">&#10006;</span>
        </span>
      );
    };

    className += " dislike-false";
    return (
      <span className={className} 
          onClick={this.add_dislike.bind(this)} 
          repo_id={ repo_id }>
          <span className="dislike-text">I dislike this repo</span>
          &nbsp;<span className={iconClassName}>&#10006;</span>
      </span>
    );
  }
}
