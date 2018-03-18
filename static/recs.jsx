let myData;
let pageNumber = 1;
let startLoad = new Date().getTime();
let code;
let repoIDs;
let callsMade = false;
let scope = document.getElementById("details").dataset.scope;

ReactDOM.render(
    <PlaceholderList count={12} />,
    document.getElementById("repo-recs")
);

function makeCalls() {
    callsMade = true;
    generateCode()
        .then( thisCode => getRepoRecs(pageNumber, thisCode) )
        .then(updateUser);
}

function getRepoRecs(pageNumber, thisCode) {
    let payload = {method: "GET",
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch(`/get_repo_recs?page=${pageNumber}&code=${thisCode}`, payload)
        .then( response => response.json() )
        .then( (data) => showRepoRecs(data) );
}

function showRepoRecs(data) {
    myData = data;
    repoIDs = new Set(data.map( (repo) => getRepoID(repo) ));
    renderRepoComponents(data);
    let endLoad = new Date().getTime();
    var delta = (endLoad - startLoad)/1000;
    console.log("Recs loaded in " + delta + "seconds.");
}

function renderRepoComponents(data) {
    ReactDOM.render(
        <RepoList repos={ data } code={ code } />,
        document.getElementById("repo-recs")
    );
}

function getRepoID(repo) {
    return repo.repo_id;
}
