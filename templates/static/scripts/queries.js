let currentPage = 1;
let curr_select = "";

function newCall(fname) {
  const proc = document.querySelector('input[name="proc"]:checked');
  fetch_io_events(proc.value, fname);
}

// --- Fetch Data ---
function fetch_query() {
  const type = document.getElementById("query_type").value;
  const proc = document.querySelector('input[name="proc"]:checked');
  const hunk = document.getElementById("hunk").checked;
  const stds = document.getElementById("remove_stds").checked;
  const ro = document.getElementById("reverse_order").checked;

  if (!proc) {
    return;
  }

  curr_select = type;

  fetch(
    `/api/files/${type}?page=${currentPage}&proc=${encodeURIComponent(
      proc.value
    )}&hunk=${hunk}&rmstd=${stds}&desc=${ro}`
  )
    .then((res) => res.json())
    .then(render_query)
    .catch((err) => console.error(err));
}

// --- Render Report + Paging ---
function render_query(resp) {
  const container = document.getElementById("query_report");
  container.innerHTML = "";

  // Build table
  const table = document.createElement("table");
  table.style.borderCollapse = "collapse";
  table.innerHTML = `
    <tr>
        <th style="border: 1px solid black; padding: 4px;">File</th>
        <th style="border: 1px solid black; padding: 4px;">${curr_select}</th>
    </tr>
`;

  // Add rows
  resp.data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td data-fname="${row.fname}" style="border: 1px solid black; padding: 4px; cursor:pointer;">
            ${row.fname}
        </td>
        <td style="border: 1px solid black; padding: 4px;">${row.value}</td>
    `;
    table.appendChild(tr);
  });

  // Add click listener ONCE
  table.addEventListener("click", (e) => {
    const fname = e.target.dataset.fname;
    if (fname) newCall(fname);
  });

  container.appendChild(table);

  // --- paging controls ---
  document.getElementById(
    "page_info"
  ).textContent = `Page ${resp.page} of ${resp.total_pages}`;

  const prevBtn = document.getElementById("prev_page");
  const nextBtn = document.getElementById("next_page");

  prevBtn.disabled = !resp.prev_page;
  nextBtn.disabled = !resp.next_page;

  prevBtn.onclick = () => {
    if (resp.prev_page) {
      currentPage = resp.prev_page;
      fetch_query();
    }
  };

  nextBtn.onclick = () => {
    if (resp.next_page) {
      currentPage = resp.next_page;
      fetch_query();
    }
  };
}

// --- Trigger fetch when dropdown changes ---
document.getElementById("query_type").addEventListener("change", () => {
  currentPage = 1; // reset on type change
  fetch_query();
});

// --- Load initial ---
fetch_query();
