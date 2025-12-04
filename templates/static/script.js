// size and boundary
const svg = d3.select("#chart");
const width = +svg.attr("width");
const height = +svg.attr("height");

const margin = { top: 40, right: 40, bottom: 40, left: 120 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

function plot(events) {
    const parseTime = d3.utcParse("%Y-%m-%d %H:%M:%S.%f");
    events.forEach(d => {
        d.start = parseTime(d.en_datetime);
        d.end   = parseTime(d.ex_datetime);
    });

    // scales
    const xScale = d3.scaleTime()
        .domain([
            d3.min(events, d => d.start),
            d3.max(events, d => d.end)
        ])
        .range([0, innerWidth]);

    const yScale = d3.scaleBand()
        .domain([...new Set(events.map(d => d.event_name))])
        .range([0, innerHeight])
        .padding(0.4);

    // axes
    const xAxis = d3.axisBottom(xScale)
        .ticks(10)
        .tickSize(-innerHeight)
        .tickFormat(d3.utcFormat("%H:%M:%S.%f"));

    const yAxis = d3.axisLeft(yScale);

    const gx = g.append("g")
        .attr("class", "x-axis grid")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(xAxis);

    const gy = g.append("g")
        .attr("class", "y-axis")
        .call(yAxis);

    // draw events
    const lines = g.append("g")
        .attr("class", "event-lines");

    lines.selectAll("line")
        .data(events)
        .enter()
        .append("line")
        .attr("x1", d => xScale(d.start))
        .attr("x2", d => xScale(d.end))
        .attr("y1", d => yScale(d.event_name) + yScale.bandwidth()/2)
        .attr("y2", d => yScale(d.event_name) + yScale.bandwidth()/2)
        .attr("stroke", "#0074D9")
        .attr("stroke-width", 5)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.95)
        .on("mouseover", function(event, d) {
            d3.select("#tooltip")
                .style("opacity", 1)
                .html(`
                    <strong>${d.event_name}</strong><br>
                    <span style="color:#555">${d.fname}</span><br>
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

        // Update axes
        gx.call(xAxis.scale(zx));

        // Update line positions
        lines.selectAll("line")
            .attr("x1", d => zx(d.start))
            .attr("x2", d => zx(d.end));
    }
}

fetch('/api/events')
  .then(r => r.json())
  .then(rawData => {
    plot(rawData)
  })
  .catch(err => console.error('Error loading /api/events', err));
