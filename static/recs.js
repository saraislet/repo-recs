$("#get-repo-recs").click(getRepoRecs);

let myData;

function getRepoRecs() {
    console.log("Getting repository recommendations.");
    let user_id = document.getElementById("get-repo-recs").getAttribute("user-id");
    $.get("/get_repo_recs", showRepoRecs);
    // fetch("/get_repo_recs?user_id=" + user_id, showRepoRecs)
    //     .then( (response) => response.json() )
    //     .then( (data) => showRepoRecs(data));
    // fetch("http://127.0.0.1:5000/get_repo_recs", {
    //     headers : { 
    //         'Content-Type': 'application/json',
    //         'Accept': 'application/json'
    //    }

    // })
    //     .then( (data) => { console.log(data) } );
        // .then( (response) => response.json() )
        // .then( (data) => showRepoRecs(data) );
}

function showRepoRecsRaw(data) {
    console.log("Showing raw repository recommendations.");
    $("#repo-recs").html(data);
    myData = JSON.parse(data);
}

function showRepoRec(data) {
    console.log("Showing repository recommendation.");
    // $("#repo-recs").html(data);
    myData = JSON.parse(data);
    let repo = myData[0];
    renderRepo(repo);
    // for (let repo of data) {
        // renderRepo(repo);
    // }
}

function showRepoRecs(data) {
    console.log("Showing repository recommendations.");
    // $("#repo-recs").html(data);
    myData = JSON.parse(data);
    // let listRepos = myData.map( (repo) => buildRepo(repo) );
    // renderRepoList(listRepos);
    renderRepoComponents(myData);
}

// ReactDOM.render(
//   <Repo repo_name="Repo Name" repo_description="Repo Description"/>,
//   document.getElementById("repo-recs")
// );

function renderRepo(repo) {
    let name = repo.name;
    let desc = repo.description;
    console.log("repo: ", name, desc);

    ReactDOM.render(
      <Repo repo_name={name} repo_description={desc}/>,
      document.getElementById("repo-recs")
    );
}

function buildRepo(repo) {
    return (
        <div key={ repo.name } className="w3-card-4 w3-margin repo">
          <header className="w3-container w3-blue-grey">
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

function renderRepoList(repoList) {
    ReactDOM.render(
        <Repo repos={ repoList } />,
        document.getElementById("repo-recs")
    );
}

function renderRepoComponents(data) {
    ReactDOM.render(
        <RepoList repos={ data } />,
        document.getElementById("repo-recs")
    );
}
