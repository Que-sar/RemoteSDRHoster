const margin = { top: 70, right: 80, bottom: 50, left: 60 };
const width = 1200 - margin.left - margin.right;
const height = 600 - margin.top - margin.bottom;

const x = d3.scaleLinear().range([0, width]);
const y = d3.scaleLinear().range([height, 0]);

const svg = d3.select("#chart-container")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", `translate(${margin.left}, ${margin.top})`);

const yMin = -60;
const yMax = 60;
y.domain([yMin, yMax]);
svg.append("g")
  .call(d3.axisLeft(y));

svg.append("rect")
  .attr("width", width)
  .attr("height", height)
  .attr("fill", "lightgrey");

function renderChart(data) {
  x.domain([d3.min(data.freqAxis), d3.max(data.freqAxis)]);

  const line = d3.line()
    .x((d, i) => x(data.freqAxis[i]))
    .y((d, i) => y(data.spectrumDB[i]))
    .curve(d3.curveLinear);

  const area = d3.area()
    .x((d, i) => x(data.freqAxis[i]))
    .y0(height)
    .y1((d, i) => y(data.spectrumDB[i]));

  // Update the filled area
  svg.select(".area-path")
    .datum(data.spectrumDB)
    .attr("d", area);

  // Update the line path
  svg.select(".line-path")
    .datum(data.spectrumDB)
    .attr("d", line);
}