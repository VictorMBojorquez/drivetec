(()=>{const $=s=>document.querySelector(s),
RGZ={puente:[32.5276,-117.0240],hospital:[32.5236,-117.0262],centro:[32.5340,-117.0330],aeropuerto:[32.5411,-116.9700],universidad:[32.5013,-116.9650],plaza:[32.5300,-117.0150]},
px=g=>(g+117.08)/0.14*400,py=a=>(32.56-a)/0.08*300,
csrf=()=>(document.cookie.match(/csrftoken=([^;]+)/)||[])[1]||'',
api=(u,b,m)=>fetch(u,{method:m||(b?'POST':'GET'),headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:b?JSON.stringify(b):undefined,credentials:'same-origin'}).then(r=>r.json()),
COL={Ambulancia:'#10b981',Patrulla:'#64748b',Bomberos:'#f59e0b'},proj=u=>{u.x=px(u.lng);u.y=py(u.lat);return u},
inc=r=>r.lat!=null?{lat:r.lat,lng:r.lng}:r.uk?{lat:RGZ[r.uk][0],lng:RGZ[r.uk][1]}:null;
let ready=false,maps={},mk={},tm,sims={},pos={};const SIM=!(window.DT&&DT.key),SEED={'A-12':[32.5280,-117.0290],'A-07':[32.5090,-116.9800],'P-07':[32.5330,-117.0200],'P-03':[32.4980,-117.0050],'B-03':[32.5400,-117.0100],'B-01':[32.5200,-117.0400]};
S.units.forEach(u=>{if(u.lat==null&&SEED[u.id]){u.lat=SEED[u.id][0];u.lng=SEED[u.id][1]}if(u.lat!=null)proj(u)});
Object.entries(RGZ).forEach(([k,[a,b]])=>{GZ[k][1]=px(b);GZ[k][2]=py(a)});
window.dtSync=()=>{if(!window._dtLoaded)return;clearTimeout(tm);tm=setTimeout(()=>api('/api/state',{reports:S.reports,units:S.units.map(u=>({id:u.id,busy:u.busy})),log:S.log},'PUT').catch(()=>{}),600)};
api('/api/state').then(st=>{window._dtLoaded=true;if(!st.units)return;S.units=st.units.map(proj);S.reports=st.reports;S.log=st.log;S.seq=Math.max(S.seq,st.seq);S.sel=0;try{localStorage.setItem(LS,JSON.stringify(S))}catch(e){}$('nav button.on').click()}).catch(()=>{window._dtLoaded=true});
const gm=id=>maps[id]||(maps[id]=new google.maps.Map($('#g'+id),{center:{lat:32.5149,lng:-117.0382},zoom:12,mapTypeControl:false,streetViewControl:false}));
function gdraw(id,reps){const m=gm(id);(mk[id]||[]).forEach(x=>x.setMap(null));mk[id]=[];const C=google.maps.SymbolPath.CIRCLE;
 S.units.forEach(u=>mk[id].push(new google.maps.Marker({map:m,position:{lat:u.lat,lng:u.lng},title:u.id+' · '+u.t+(u.busy?' (ocupada)':''),label:{text:u.id,fontSize:'9px',fontWeight:'700',color:'#fff'},icon:{path:C,scale:15,fillColor:COL[u.t],fillOpacity:u.busy?.4:1,strokeColor:'#fff',strokeWeight:2}})));
 reps.forEach(r=>{const c=inc(r);if(!c)return;mk[id].push(new google.maps.Marker({map:m,position:c,title:r.folio+' · '+(r.ub||''),icon:{path:C,scale:9,fillColor:'#e11d48',fillOpacity:.9,strokeColor:'#fff',strokeWeight:2}}));
  const u=S.units.find(u=>u.id===r.unit);if(u&&reps.length===1)mk[id].push(new google.maps.Polyline({map:m,path:[c,{lat:u.lat,lng:u.lng}],strokeColor:'#e11d48'}))})}
const hv=(a,b,c,d)=>{const p=Math.PI/180,h=Math.sin((c-a)*p/2)**2+Math.cos(a*p)*Math.cos(c*p)*Math.sin((d-b)*p/2)**2;return 12742*Math.asin(Math.sqrt(h))};
function sdraw(id,reps){const m=sims[id];if(!m)return;m.posOf=u=>pos[u.id]||u;const I=reps.map(r=>{const c=inc(r);return c&&{lat:c.lat,lng:c.lng,folio:r.folio}}).filter(Boolean);let sel=null;
 if(reps.length===1){const c=inc(reps[0]);if(c&&reps[0].unit)sel={unit:reps[0].unit,to:c}}m.set(S.units.filter(u=>u.lat!=null).map(u=>({...u,col:COL[u.t]})),I,sel)}
const draw=(id,reps)=>SIM?sdraw(id,reps):gdraw(id,reps);
function localRank(r,g){const need={choque:r.her?'Ambulancia':'Patrulla',incendio:'Bomberos',robo:'Patrulla',medico:'Ambulancia'}[r.tipo];
 const u=S.units.filter(u=>!u.busy&&u.lat!=null).map(u=>{const km=hv(u.lat,u.lng,g.lat,g.lng)*1.3;return{id:u.id,t:u.t,km:+km.toFixed(1),min:+(km/40*60).toFixed(1),need:u.t===need}}).sort((a,b)=>(b.need-a.need)||a.min-b.min);return{units:u,source:'estimate'}}
function anim(){if(!SIM)return;S.units.forEach(u=>{if(!u.busy&&pos[u.id])delete pos[u.id]});S.reports.forEach(r=>{const u=S.units.find(x=>x.id===r.unit),c=inc(r);if(!u||u.lat==null||!c)return;
 if(r.status==='cerrado'){delete pos[u.id];return}if(r.status!=='despachado'||pos[u.id])return;
 if(Date.now()-(r.t0+(r.resp||0)*1000)>8000){pos[u.id]={lat:c.lat,lng:c.lng};return}
 const ms=Math.max(1500,hv(u.lat,u.lng,c.lat,c.lng)*1.3/40*60*1000),t0=performance.now();pos[u.id]={lat:u.lat,lng:u.lng};
 (function f(t){const k=Math.min(1,(t-t0)/ms);pos[u.id]={lat:u.lat+(c.lat-u.lat)*k,lng:u.lng+(c.lng-u.lng)*k};Object.values(sims).forEach(m=>m.render());if(k<1)requestAnimationFrame(f)})(t0)})}
const od=window.dmap,ou=window.rUni,oa=window.rAud,orp=window.rRep;window.rRep=()=>{orp();anim()};
window.dmap=()=>{od();anim();ready&&draw('map2',S.reports.filter(r=>r.status!=='cerrado'))};
window.rUni=()=>{ou();anim();ctrl();ready&&draw('map',S.reports.slice(S.sel,S.sel+1))};
window.rAud=()=>{oa();if($('#vs'))return;const b=document.createElement('button');b.id='vs';b.className='b s';b.textContent='Verificar en servidor (SHA-256)';
 b.onclick=async()=>{const v=await api('/api/audit/verify');$('#vr').innerHTML=v.ok?` <b class="ok">✔ Servidor: cadena íntegra (${v.count})</b>`:` <b class="er">✖ Servidor: alteración en el evento ${v.bad}</b>`};$('#vf').after(b)};
function ctrl(){if($('#gc'))return;const d=document.createElement('div');d.id='gc';d.className='no-print';
 d.innerHTML="<label>Dirección del incidente (Google Geocoding + Routes)</label><input id='ga' placeholder='Av. Revolución 1000, Tijuana'><button class='b' id='gb'>Ubicar y calcular ETA</button><div id='gr'></div>";
 ($('#gmap')||$('#map')).before(d);$('#gb').onclick=locate}
async function locate(){const r=S.reports[S.sel];if(!r)return alert('Genera un reporte primero.');const q=$('#ga').value.trim();if(!q)return;
 $('#gr').textContent='Buscando…';let g;try{g=await api('/api/geocode',{q})}catch(e){g={error:'x'}}if(g.error&&SIM)g=simGeocode(q);if(g.error){$('#gr').textContent=g.error;return}
 r.lat=g.lat;r.lng=g.lng;r.ub=g.formatted;log(r.folio,'Geocodificado: '+g.formatted);save();
 let k;try{k=await api('/api/rank',{lat:g.lat,lng:g.lng,tipo:r.tipo,her:r.her});if(!k.units)throw 0}catch(e){k=localRank(r,g)}
 $('#gr').innerHTML=`<p><b>${esc(g.formatted)}</b> · ETA: ${k.source==='google'?'Google Routes con tráfico':'estimación'}</p><table><tr><th>Unidad</th><th>Tipo</th><th>Km</th><th>Min</th><th></th></tr>`+k.units.map(u=>`<tr><td>${u.id}</td><td>${u.t}${u.need?' ★':''}</td><td>${u.km}</td><td>${u.min}</td><td><button class="b s" data-as="${u.id}">Asignar</button></td></tr>`).join('')+'</table>';
 $('#gr').onclick=e=>{const id=e.target.dataset.as;if(id&&r.status!=='despachado'){r.unit=id;log(r.folio,'Unidad asignada por ETA: '+id);save();ready&&draw('map',[r])}};ready&&draw('map',[r])}
if(window.DT&&DT.key){window.dtReady=()=>{ready=true;['map2','map'].forEach(id=>{const s=$('#'+id),d=document.createElement('div');d.id='g'+id;d.style.cssText='height:340px;border-radius:8px';s.style.display='none';s.before(d)});$('nav button.on').click()};
 const s=document.createElement('script');s.src='https://maps.googleapis.com/maps/api/js?key='+DT.key+'&callback=dtReady&v=weekly';s.async=true;document.head.appendChild(s)}else{ready=true;['map2','map'].forEach(id=>{const s=$('#'+id),d=document.createElement('div');d.id='g'+id;d.style.cssText='height:340px;border-radius:8px;overflow:hidden';s.style.display='none';s.before(d);d.classList.add('sim');sims[id]=new SimMap(d)});$('nav button.on').click()}
try{const w=document.getElementById('who');if(w&&window.DT&&DT.user)w.textContent=DT.user+' · Turno A'}catch(e){}
})();
