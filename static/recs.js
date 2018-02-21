// $("#get-repo-recs").click(getRepoRecs);
window.onload = getRepoRecs;

let myData;
let startLoad = new Date().getTime();

function getRepoRecs() {
    console.log("Getting repository recommendations.");
    // let user_id = document.getElementById("get-repo-recs").getAttribute("user-id");
    $.get("/get_repo_recs", showRepoRecs);
}

function showRepoRecsRaw(data) {
    console.log("Showing raw repository recommendations.");
    $("#repo-recs").html(data);
    myData = JSON.parse(data);
}

function showRepoRecs(data) {
    console.log("Showing repository recommendations.");
    myData = JSON.parse(data);
    // let listRepos = myData.map( (repo) => buildRepo(repo) );
    // renderRepoList(listRepos);
    renderRepoComponents(myData);
    let endLoad = new Date().getTime();
    var delta = (endLoad - startLoad)/1000;
    console.log("Recs loaded in " + delta + "seconds.");
}

function renderRepo(repo) {
    let name = repo.name;
    let desc = repo.description;
    console.log("repo: ", name, desc);

    ReactDOM.render(
      <Repo repo_name={name} repo_description={desc}/>,
      document.getElementById("repo-recs")
    );
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
