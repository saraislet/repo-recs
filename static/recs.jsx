let myData;
let pageNumber = 1;
let startLoad = new Date().getTime();
let code;
let repoIDs;

window.onload = makeCalls;

ReactDOM.render(
    <PlaceholderList count={12} />,
    document.getElementById("repo-recs")
);

async function generateCode() {
    code = Math.random().toString(36).substring(2);
    return code;
}

function makeCalls() {
    generateCode()
        .then( thisCode => getRepoRecs(pageNumber, thisCode) )
        .then(updateUser);
}

function updateUser() {
    let payload = {method: "POST",
                   body: JSON.stringify({}),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/update_user", payload)
        .then( response => response.json() )
        .then( (data) => {
            if (data.Status == 200) {
                let endUserUpdate = new Date().getTime();
                var delta = (endUserUpdate - startLoad)/1000;
                console.log("User updated in " + delta + "seconds.");
            }})
        .then( () => crawlUser() );
}

function crawlUser() {
    let data = {"crawlFurther": "True"};
    let payload = {method: "POST",
                   body: JSON.stringify(data),
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/update_user", payload)
        .then( response => response.json() )
        .then( (data) => {
            if (data.Status == 200) {
                let endUserCrawl = new Date().getTime();
                var delta = (endUserCrawl - startLoad)/1000;
                console.log("User crawled in " + delta + "seconds.");
            }});
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
