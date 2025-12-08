// size and boundary
const svg = d3.select("#chart");
const width = +svg.attr("width");
const height = +svg.attr("height");

const margin = { top: 40, right: 40, bottom: 40, left: 120 };
const innerWidth = width - margin.left - margin.right;
const innerHeight = height - margin.top - margin.bottom;

svg.style("overflow", "hidden");

const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

function plot(events, rendom_events) {
    const parseTime = d3.utcParse("%Y-%m-%d %H:%M:%S.%f");
    events.forEach(d => {
        d.start = parseTime(d.en_datetime);
        d.end   = parseTime(d.ex_datetime);
    });

    rendom_events.forEach(d => {
        d.time  = parseTime(d.datetime);
    });

    // scales
    const xScale = d3.scaleTime()
        .domain([
            d3.min([d3.min(events, d => d.start), d3.min(rendom_events, d => d.time)]),
            d3.max([d3.max(events, d => d.end), d3.max(rendom_events, d => d.time)]),
        ])
        .range([0, innerWidth])
        .nice();

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

    svg.append("text")
      .attr("class", "title")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(${width / 2}, ${margin.top / 2})`)
      .text("Tracing Time");
    
    svg.append("text")
      .attr("class", "axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(${width / 2}, ${height})`)
      .text("time");

    svg.append("text")
      .attr("class", "axis-label")
      .attr("text-anchor", "middle")
      .attr("transform", `translate(40, ${height / 2}) rotate(-90)`)
      .text("operand");
    
    // draw sections
    const sections = g.append("g")
        .attr("class", "sections");
    
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
        sections.selectAll("line")
            .attr("x1", d => zx(d.time))
            .attr("x2", d => zx(d.time));

        lines.selectAll("line")
            .attr("x1", d => zx(d.start))
            .attr("x2", d => zx(d.end));
    }
}

fetch('/api/events/io')
  .then(r => r.json())
  .then(rawData => {
    plot(rawData, [])
  })
  .catch(err => console.error('Error loading /api/events', err));
