// size
const width = 1600;
const height = 800;

// boundaries
const margin = { top: 40, right: 40, bottom: 60, left: 120 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

// create a parse time lambda
const parseTime = d3.utcParse("%Y-%m-%d %H:%M:%S.%f");

// define a color scale using a predefined scheme
const color = d3.scaleOrdinal(d3.schemeCategory10);

// plot the diagram
function plot(events, rendom_events) {
    // select the svg element by it's ID
    const svg = d3.select("#chart")
        .attr("width", width)
        .attr("height", height)
        .style("overflow", "hidden");
    
    svg.selectAll("*").remove();
    
    svg.append("defs")
        .append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", innerWidth)
        .attr("height", innerHeight);

    // create a group inside the svg
    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`)
        .attr("width", innerWidth)
        .attr("height", innerHeight)
        .style("overflow", "hidden");

    // set a rectangle as background
    g.append("rect")
        .attr("width", innerWidth)
        .attr("height", innerHeight)
        .attr("fill", "steelblue")
        .attr("opacity", 0.1);

    // parse the datetimes
    events.forEach(d => {
        d.start = parseTime(d.en_datetime);
        d.end   = parseTime(d.ex_datetime);
    });
    rendom_events.forEach(d => {
        d.time  = parseTime(d.datetime);
    });

    // create both x and y scales
    const xScale = d3.scaleTime()
        .domain([
            d3.min([d3.min(events, d => d.start), d3.min(rendom_events, d => d.time)]),
            d3.max([d3.max(events, d => d.end), d3.max(rendom_events, d => d.time)]),
        ])
        .range([0, innerWidth])
        .nice();
    const yScale = d3.scaleBand()
        .domain([...new Set(events.map(d => d.event_name))].sort())
        .range([0, innerHeight])
        .padding(0.4);

    // create x and y axes
    const xAxis = d3.axisBottom(xScale)
        .ticks(10)
        .tickSize(-innerHeight)
        .tickFormat(d3.utcFormat("%H:%M:%S.%f"));
    const yAxis = d3.axisLeft(yScale)
        .tickSize(-innerWidth);

    // create the grid lines
    const gx = g.append("g")
        .attr("class", "x-axis grid")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(xAxis);
    g.append("g")
        .attr("class", "y-axis grid")
        .style("font-weight", "bold")
        .call(yAxis);

    // create the labels
    svg.append("text")
      .attr("class", "title")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(${width / 2}, ${margin.top / 2})`)
      .text("File Access Patterns Tracing");
    svg.append("text")
      .attr("class", "axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(${width / 2}, ${height - 10})`)
      .text("time (ns)");
    svg.append("text")
      .attr("class", "axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(40, ${height / 2}) rotate(-90)`)
      .text("event (operand/operation)");
    
    // draw sections
    const sections = g.append("g")
        .attr("class", "sections")
        .attr("clip-path", "url(#clip)");
    
    sections.selectAll("line")
        .data(rendom_events)
        .enter()
        .append("line")
        .attr("x1", d => xScale(d.time))
        .attr("x2", d => xScale(d.time))
        .attr("y1", _ => 0)
        .attr("y2", _ => innerHeight)
        .attr("stroke", "#e47208ff")
        .attr("stroke-width", 2)

    // draw events
    const lines = g.append("g")
        .attr("class", "event-lines")
        .attr("clip-path", "url(#clip)");

    lines.selectAll("line")
        .data(events)
        .enter()
        .append("line")
        .attr("x1", d => xScale(d.start))
        .attr("x2", d => xScale(d.end))
        .attr("y1", d => yScale(d.event_name) + yScale.bandwidth()/2)
        .attr("y2", d => yScale(d.event_name) + yScale.bandwidth()/2)
        .attr("stroke", (d, _) => color(d.event_name))
        .attr("stroke-width", 7)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.95)
        .on("mouseover", function(_, d) {
            d3.select("#tooltip")
                .style("opacity", 1)
                .html(`
                    <strong>${d.event_name}</strong><br>
                    <span style="color:#555">File:${d.fname}</span><br>
                    <span style="color:#555">Bytes:${d.countbytes}</span><br>
                    <span style="color:#555">Duration:${d.latency}</span><br>
                    <span style="color:#555">Return:${d.ret}</span><br>
                    <small>${d.en_datetime} - ${d.ex_datetime}</small>
                `);
        })
        .on("mousemove", function(event) {
            d3.select("#tooltip")
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px");
        })
        .on("mouseout", function() {
            d3.select("#tooltip")
                .style("opacity", 0);
        });

    // zoom
    const zoom = d3.zoom()
        .scaleExtent([1, 10000])
        .extent([[0, 0], [innerWidth, innerHeight]])
        .translateExtent([[0, 0], [innerWidth, innerHeight]])
        .on("zoom", zoomed);

    svg.call(zoom);

    function zoomed(event) {
        const t = event.transform;
        const zx = t.rescaleX(xScale);

        // update axes
        gx.call(xAxis.scale(zx));

        // update line positions
        sections.selectAll("line")
            .attr("x1", d => zx(d.time))
            .attr("x2", d => zx(d.time));

        lines.selectAll("line")
            .attr("x1", d => zx(d.start))
            .attr("x2", d => zx(d.end));
    }
}

// use fetch to make an API call
function fetch_io_events(proc_name, fname="") {
    const hunk = document.getElementById("hunk").checked;
    const stds = document.getElementById("remove_stds").checked;

    const url = `/api/events/io?proc=${encodeURIComponent(proc_name)}&fname=${encodeURIComponent(fname)}&hunk=${hunk}&rmstd=${stds}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            plot(data, []);
        })
        .catch(err => {
            console.error('Error loading /api/events', err);
            alert(err);
        });
}

// use fetch to get the procs list
function fetch_procs() {
    fetch('/api/events/procs')
        .then(response => response.json())
        .then(data => {
            const el = document.getElementById("procs");
            el.innerHTML = ""; // clear old radios

            data.forEach(proc => {
                // container
                const wrapper = document.createElement("div");

                const id = "proc_" + proc.replace(/[^a-zA-Z0-9]/g, "_");

                // radio input
                const radio = document.createElement("input");
                radio.id = id;
                radio.type = "radio";
                radio.name = "proc";        // same name = radio group
                radio.value = proc;
                radio.addEventListener("change", () => {
                    fetch_io_events(proc);   // call your function
                });

                // label
                const label = document.createElement("label");
                label.textContent = proc;
                label.htmlFor = id;
                label.style.marginLeft = "6px";
                label.addEventListener("click", () => {
                    radio.checked = true;
                    fetch_io_events(proc);
                });

                wrapper.appendChild(radio);
                wrapper.appendChild(label);
                el.appendChild(wrapper);
            });
        })
        .catch(err => {
            console.error('Error loading /api/events', err);
            alert(err);
        })
}

// call the fetch procs
fetch_procs();
