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

    // getRepoRecs() {
    //     let user_id = document.getElementById("get-repo-recs").getAttribute("user-id");
    //     fetch("/get_repo_recs?user_id=" + user_id, showRepoRecs)
    //         .then( (response) => response.json() )
    //         .then( (data) => showRepoRecs(data));
    // }

    render() {
        let repos = this.props.repos
        let listRepos = myData.map( (repo) => buildRepo(repo) );
        return (
            <span>{ listRepos }</span>
        )
    }
}
