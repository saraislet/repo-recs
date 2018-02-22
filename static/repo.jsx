class RepoList extends React.Component {
  render() {
    let repos = this.props.repos
    let listRepos = repos.map( (repo) => buildRepo(repo) );
    return (
      <span>{ listRepos }</span>
    )
  }
}

function buildRepo(repo) {
  let listLangs = null;
  if ( repo.langs.length > 0 ) {
    let languages = repo.langs.map( (lang) => buildLang(lang) );
    listLangs = (<ul>{ languages.slice(0,3) }</ul>);
  }

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
        <Star isStarred="" repo_id={ repo.repo_id }/>
      </div>
    </div>
  )
}

function buildLang(lang) {
  return (
    <li key={ lang.language_id }>{ lang.language_name } : { lang.language_bytes }</li>
  )
}

class PlaceholderList extends React.Component {
  render() {
    let arr = Array.from(Array(9).keys());
    let listPlaceholders = arr.map( (num) => buildPlaceholder(num) );
    return (
      <span>{ listPlaceholders }</span>
    )
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
  )
}

class Star extends React.Component {
  render() {
    let isStarred = this.props.isStarred;
    let repo_id = this.props.repo_id;

    if (isStarred) {
      return <FilledStar repo_id={ repo_id } />; 
    }
    return <OpenStar repo_id={ repo_id } />;
  }
}

class OpenStar extends React.Component {
  constructor(props) {
    super(props);
  }

  add_star(e) {
    console.log("Ran add_star() on " + this.props.repo_id + "!");
    let access_token = document.getElementById("details").dataset.accessToken;
    // console.log(access_token);
    // $.get("/add_star", 
    //       {"repo_id": this.props.repo_id}, 
    //       (response) => JSON.parse(response));
    let data = {"repo_id": this.props.repo_id,
                "access_token": access_token};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/add_star", payload)
          // .then( response => JSON.parse(response))
          .then( response => response.json() )
          // .then( data => console.log(data))
          .then( (data) => this.update_star(data) )
  }

  update_star(data) {
    if (data.Status == 204) {
      console.log("Successfully added star for repo " + data.repo_id + ".");
    }
  }

  render() {
    let repo_id = this.props.repo_id;

    return (
      <span className="star" onClick={this.add_star.bind(this)} repo_id={ repo_id }>☆</span>
    )
  }
}

class FilledStar extends React.Component {
  render() {
    return (
      <span className="star">★</span>
    )
  }
}

