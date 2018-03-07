let myNodes;
let path
let circle
let links
let nodes
let text
let width
let height
let force
let svg

window.onload = getNodes;

function getNodes() {
    let payload = {method: "GET",
                   credentials: "same-origin",
                   headers: new Headers({"Content-Type": "application/json"})};
    fetch("/get_graph", payload)
        .then( response => response.json() )
        .then( (data) => buildGraph(data) );
}

function buildGraph(links) {

    nodes = {};

    // Compute the distinct nodes from the links.
    links.forEach(function(link) {
      link.source = nodes[link.source] || (nodes[link.source] = {name: link.source_name});
      link.target = nodes[link.target] || (nodes[link.target] = {name: ""});
    });

    width = window.innerWidth;
    height = window.innerHeight;

    force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(60)
        .charge(-400)
        .on("tick", tick)
        .start();

    svg = d3.select("body").append("svg")
        .attr("id", "d3")
        .attr("width", width)
        .attr("height", height);

    // Per-type markers, as they don't inherit styles.
    svg.append("defs").selectAll("marker")
        .data(["user-repo", "repo-user"])
      .enter().append("marker")
        .attr("id", function(d) { return d; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");

    path = svg.append("g").selectAll("path")
        .data(force.links())
      .enter().append("path")
        .attr("class", function(d) { return "link " + d.type; })
        .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });

    circle = svg.append("g").selectAll("circle")
        .data(force.nodes())
      .enter().append("circle")
        .attr("r", 3)
        .call(force.drag);

    text = svg.append("g").selectAll("text")
        .data(force.nodes())
      .enter().append("text")
        .attr("x", 8)
        .attr("y", ".31em")
        .text(function(d) { return d.name; });
}

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
  path.attr("d", linkArc);
  circle.attr("transform", transform);
  text.attr("transform", transform);
}

function linkArc(d) {
  var dx = d.target.x - d.source.x,
      dy = d.target.y - d.source.y,
      dr = Math.sqrt(dx * dx + dy * dy);
  return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
}

function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}

window.onresize = function() {
  width = window.innerWidth;
  height = window.innerHeight;
}
