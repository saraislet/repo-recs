async function generateCode() {
    code = Math.random().toString(36).substring(2);
    return code;
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