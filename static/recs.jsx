window.onload = makeCalls;

let myData;
let startLoad = new Date().getTime();

ReactDOM.render(
    <PlaceholderList/>,
    document.getElementById("repo-recs")
);

function makeCalls() {
    getRepoRecs();
    updateUser();
}

function updateUser() {
    let payload = {method: "POST",
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/update_user", payload)
        .then( response => response.json() )
        .then( (data) => {
            if (data.Status == 200) {
                let endUserUpdate = new Date().getTime();
                var delta = (endUserUpdate - startLoad)/1000;
                console.log("User updated in " + delta + "seconds.");
            }
        });
}

function getRepoRecs() {
    $.get("/get_repo_recs", showRepoRecs);
}

function showRepoRecs(data) {
    myData = JSON.parse(data);
    renderRepoComponents(myData);
    let endLoad = new Date().getTime();
    var delta = (endLoad - startLoad)/1000;
    console.log("Recs loaded in " + delta + "seconds.");
}

function renderRepoComponents(data) {
    ReactDOM.render(
        <RepoList repos={ data } />,
        document.getElementById("repo-recs")
    );
}
