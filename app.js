const $ = (id) => document.getElementById(id);
const fields = ["sleep","activity","stress","radiation","hr"];
const apiFields = ["sleep_hours","activity_index","stress_index","radiation_index","hr_deviation_index"];
const labels = ["Sleep hours","Activity index","Stress index","Radiation index","HR deviation"];

function values(){
  return {
    sleep_hours:Number($("sleep").value),
    activity_index:Number($("activity").value),
    stress_index:Number($("stress").value),
    radiation_index:Number($("radiation").value),
    hr_deviation_index:Number($("hr").value)
  };
}
function updateOutputs(){
  fields.forEach((id,i)=>$(id+"Out").textContent=$(id).value);
  renderBars();
}
fields.forEach(id=>$(id).addEventListener("input",updateOutputs));

function renderBars(){
  const v=values();
  const maxes=[12,100,100,100,30];
  $("barChart").innerHTML=apiFields.map((key,i)=>{
    const pct=Math.max(0,Math.min(100,v[key]/maxes[i]*100));
    return `<div class="bar-row"><span>${labels[i]}</span><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div><b>${v[key]}</b></div>`;
  }).join("");
}
function nav(){
  document.querySelectorAll(".nav").forEach(btn=>btn.addEventListener("click",()=>{
    document.querySelectorAll(".nav").forEach(b=>b.classList.remove("active"));
    document.querySelectorAll(".page").forEach(p=>p.classList.remove("active-page"));
    btn.classList.add("active"); $(btn.dataset.target).classList.add("active-page");
    const titles={overview:"Mission overview",analysis:"AI analysis engine",forecast:"Forecast lab",history:"Mission history"};
    $("pageTitle").textContent=titles[btn.dataset.target];
    if(btn.dataset.target==="history") loadHistory();
  }));
}
async function analyze(){
  const btn=$("analyzeBtn"); btn.disabled=true; btn.textContent="Analyzing...";
  try{
    const response=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(values())});
    if(!response.ok) throw new Error("Analysis request failed");
    const data=await response.json(), a=data.analysis;
    $("flagValue").textContent=a.flag==="unusual_demo_pattern"?"Unusual pattern":"Within demo pattern";
    $("clusterValue").textContent=a.cluster;
    $("scoreValue").textContent=a.screening_score;
    $("explanations").innerHTML=a.top_deviations.map(x=>`<div class="explain-item"><span>${x.feature.replaceAll("_"," ")}</span><b>${x.deviation.toFixed(2)}σ ${x.direction}</b></div>`).join("");
  }catch(e){$("flagValue").textContent="API unavailable";$("explanations").innerHTML=`<p class="muted">${e.message}. Start the FastAPI server and try again.</p>`;}
  finally{btn.disabled=false;btn.innerHTML='Run AI analysis <b>↗</b>';}
}
async function saveReading(){
  const params=new URLSearchParams({crew_id:$("crewId").value,scenario:"Interactive simulation"});
  const response=await fetch("/api/readings?"+params,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(values())});
  alert(response.ok?"Simulation saved locally.":"Could not save this simulation.");
}
async function forecast(){
  const payload={history:[values(),values(),values()]};
  const response=await fetch("/api/forecast",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data=await response.json();
  if(!response.ok){$("forecastResults").innerHTML=`<p class="muted">${data.detail||"Forecast failed."}</p>`;return;}
  $("forecastResults").innerHTML=apiFields.map((key,i)=>{
    const val=data.forecast[key], range=data.illustrative_range[key];
    return `<div class="forecast-item"><span>${labels[i]}</span><b>${val}</b><small>Illustrative range: ${range[0]} – ${range[1]}</small></div>`;
  }).join("");
}
async function loadHistory(){
  const response=await fetch("/api/readings?limit=60");
  const data=await response.json();
  if(!data.items.length){$("historyTable").innerHTML='<p class="muted">No saved records yet. Save a simulation from Overview.</p>';return;}
  const cols=["created_at","crew_id","scenario","sleep_hours","activity_index","stress_index","radiation_index","hr_deviation_index"];
  $("historyTable").innerHTML=`<table><thead><tr>${cols.map(c=>`<th>${c.replaceAll("_"," ")}</th>`).join("")}</tr></thead><tbody>${data.items.map(row=>`<tr>${cols.map(c=>`<td>${row[c]??""}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}
$("analyzeBtn").addEventListener("click",analyze);
$("saveBtn").addEventListener("click",saveReading);
$("forecastBtn").addEventListener("click",forecast);
$("refreshHistory").addEventListener("click",loadHistory);
const exportBtn = document.createElement("button");

exportBtn.id = "exportCsvBtn";
exportBtn.type = "button";
exportBtn.textContent = "Export CSV";
exportBtn.className = $("refreshHistory").className;
exportBtn.disabled = true;
exportBtn.addEventListener("click", exportHistoryCSV);

$("refreshHistory").insertAdjacentElement("afterend", exportBtn);
nav(); updateOutputs();
