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
          <a class="owner" href={"https://www.github.com/" + repo.owner_login }>
            @{ repo.owner_login } 
          </a>
          &nbsp;/&nbsp;
          <b><a href={"" + repo.url }>
            { repo.name }
          </a></b>
        </h3>
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
