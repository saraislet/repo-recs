class Repo extends React.Component {

    // getRepoRecs() {
    //     let user_id = document.getElementById("get-repo-recs").getAttribute("user-id");
    //     fetch("/get_repo_recs?user_id=" + user_id, showRepoRecs)
    //         .then( (response) => response.json() )
    //         .then( (data) => showRepoRecs(data));
    // }

  render() {
    repos = this.props.repos
    let listRepos = myData.map( (repo) => buildRepo(repo) );
    return (
      <div key={ repo.name } className="w3-card-4 w3-margin repo">
        <header>
          <h2 className="w3-container w3-blue-grey">{ repo.name }</h2>
        </header>
        <div className="w3-container">
          <p>{ repo.description }</p>
          <ul>

            <li>
              lang.language.language_name : lang.language_bytes
            </li>

          </ul>
        </div>
      </div>
    )
  }
}

class RepoList extends React.Component {
  /// getRepoRecs() {
  //     let user_id = document.getElementById("get-repo-recs").getAttribute("user-id");
  //     fetch("/get_repo_recs?user_id=" + user_id, showRepoRecs)
  //         .then( (response) => response.json() )
  //         .then( (data) => showRepoRecs(data));
  // }

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
        <h3 className="w3-container w3-blue-grey">{ repo.name }</h3>
      </header>
      <div className="w3-container">
        <p>{ repo.description }</p>
        { listLangs }
      </div>
    </div>
  )
}

function buildLang(lang) {
  return (
    <li key={ lang.language_id }>{ lang.language_name } : { lang.language_bytes }</li>
  )
}

