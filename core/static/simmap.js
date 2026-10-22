(()=>{const K=1/Math.cos(32.5*Math.PI/180),norm=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
const PL={puente:['Puente Central',32.5276,-117.0240],hospital:['Hospital General',32.5236,-117.0262],centro:['Centro',32.5340,-117.0330],aeropuerto:['Aeropuerto',32.5411,-116.9700],universidad:['Universidad',32.5013,-116.9650],plaza:['Plaza Río',32.5300,-117.0150],revolucion:['Av. Revolución',32.5335,-117.0360]};
window.SIM_PLACES=PL;const D=0.0035;
window.simGeocode=q=>{const n=norm(q||'');if(!n.trim())return{error:'Escribe una dirección'};
 for(const[k,[nm,la,lg]]of Object.entries(PL))if(n.includes(k)||n.includes(norm(nm)))return{lat:la,lng:lg,formatted:nm+', Tijuana (simulado)',simulated:true};
 let h=2166136261;for(const c of n){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}h>>>=0;
 return{lat:Math.round((32.49+((h>>>12)%1000)/1000*0.06)/D)*D,lng:Math.round((-117.07+(h%4000)/4000*0.12)/D)*D,formatted:q.trim()+', Tijuana (ubicación simulada)',simulated:true}};
const hs=(i,j,k)=>(((i*73856093)^(j*19349663)^(k*83492791))>>>0)/4294967296;
const RIVER=[[32.5330,-117.075],[32.5300,-117.04],[32.5288,-117.01],[32.5350,-116.97],[32.5430,-116.935]],HWY=[[32.4950,-117.075],[32.5190,-117.0050],[32.5440,-116.94]],
PARKS=[[32.5200,-117.0500,32.5250,-117.0440],[32.5380,-117.0200,32.5420,-117.0130],[32.4980,-117.0300,32.5030,-117.0220],[32.5100,-116.9900,32.5160,-116.9820]];
class SimMap{constructor(el){this.el=el;el.style.position='relative';const c=this.c=document.createElement('canvas');c.style.cssText='width:100%;height:100%;display:block;touch-action:none;cursor:grab';el.appendChild(c);
 this.x=c.getContext('2d');this.cx=-117.0382;this.cy=32.5149;this.z=1;this.U=[];this.I=[];this.sel=null;this.places=Object.values(PL);this.posOf=u=>u;
 const box=document.createElement('div');box.style.cssText='position:absolute;right:10px;top:10px;display:flex;flex-direction:column;gap:2px';
 [['+',1.4],['−',1/1.4]].forEach(([t,f])=>{const b=document.createElement('button');b.textContent=t;b.style.cssText='width:32px;height:32px;border:0;border-radius:3px;background:#fff;color:#444;font-size:18px;box-shadow:0 1px 4px rgba(0,0,0,.3);cursor:pointer';b.onclick=()=>{this.z=Math.min(12,Math.max(.5,this.z*f));this.render()};box.appendChild(b)});el.appendChild(box);
 const tg=document.createElement('div');tg.textContent='Mapa simulado · sin APIs externas';tg.style.cssText='position:absolute;left:8px;bottom:6px;font:10px sans-serif;color:#5f6368;background:rgba(255,255,255,.85);padding:1px 6px;border-radius:3px';el.appendChild(tg);
 let d=null;c.onpointerdown=e=>{d=[e.clientX,e.clientY];c.setPointerCapture(e.pointerId);c.style.cursor='grabbing'};
 c.onpointermove=e=>{if(!d)return;const s=this.sc();this.cx-=(e.clientX-d[0])/s;this.cy+=(e.clientY-d[1])/(s*K);d=[e.clientX,e.clientY];this.render()};
 c.onpointerup=()=>{d=null;c.style.cursor='grab'};c.onwheel=e=>{e.preventDefault();this.z=Math.min(12,Math.max(.5,this.z*(e.deltaY<0?1.15:1/1.15)));this.render()};
 new ResizeObserver(()=>this.render()).observe(el)}
sc(){return 5200*this.z}
P(la,lg){const s=this.sc();return[this.w/2+(lg-this.cx)*s,this.h/2-(la-this.cy)*s*K]}
set(U,I,sel){this.U=U;this.I=I;this.sel=sel;if(!this.fit&&I.length){this.cx=I[0].lng;this.cy=I[0].lat;this.fit=1}this.render()}
render(){if(this.q)return;this.q=requestAnimationFrame(()=>{this.q=0;this.paint()})}
paint(){const c=this.c,r=this.el.getBoundingClientRect(),dp=devicePixelRatio||1;if(!r.width||!r.height)return;this.w=r.width;this.h=r.height;
 if(c.width!==Math.round(r.width*dp)||c.height!==Math.round(r.height*dp)){c.width=Math.round(r.width*dp);c.height=Math.round(r.height*dp)}
 const x=this.x,s=this.sc(),W=this.w,H=this.h;x.setTransform(dp,0,0,dp,0,0);x.lineCap='round';x.lineJoin='round';
 const dk=matchMedia('(prefers-color-scheme:dark)').matches&&document.documentElement.dataset.theme!=='light',
 C=dk?{land:'#242f3e',water:'#17263c',park:'#263c3f',road:'#38414e',cas:'#1f2835',maj:'#746855',hwy:'#9ca5b3',txt:'#9aa6b8',hal:'#242f3e'}:{land:'#f5f5f5',water:'#aadaff',park:'#c8e6c9',road:'#fff',cas:'#dadce0',maj:'#fff',hwy:'#fde293',txt:'#5f6368',hal:'#fff'};
 x.fillStyle=C.land;x.fillRect(0,0,W,H);const p=(a)=>a.map(q=>this.P(q[0],q[1]));
 x.fillStyle=C.park;PARKS.forEach(([a,b,c2,d2])=>{const[p1,p2]=[this.P(a,b),this.P(c2,d2)];x.fillRect(p1[0],p2[1],p2[0]-p1[0],p1[1]-p2[1])});
 const line=(pts,w,col)=>{x.beginPath();pts.forEach((q,i)=>i?x.lineTo(q[0],q[1]):x.moveTo(q[0],q[1]));x.lineWidth=w;x.strokeStyle=col;x.stroke()};
 const lg0=this.cx-W/2/s,lg1=this.cx+W/2/s,la0=this.cy-H/2/(s*K),la1=this.cy+H/2/(s*K),i0=Math.floor(lg0/D)-1,i1=Math.ceil(lg1/D)+1,j0=Math.floor(la0/D)-1,j1=Math.ceil(la1/D)+1,mw=Math.max(2,s*.0004);
 if(this.z>=.7){x.beginPath();for(let i=i0;i<=i1;i++)for(let j=j0;j<=j1;j++){if(i%5&&hs(i,j,0)>.2){const a=this.P(j*D,i*D),b=this.P((j+1)*D,i*D);x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1])}
  if(j%5&&hs(i,j,1)>.2){const a=this.P(j*D,i*D),b=this.P(j*D,(i+1)*D);x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1])}}
  x.lineWidth=mw+2;x.strokeStyle=C.cas;x.stroke();x.lineWidth=mw;x.strokeStyle=C.road;x.stroke()}
 line(p(RIVER),Math.max(8,s*.006),C.water);
 x.beginPath();for(let i=i0;i<=i1;i++)if(i%5==0){const a=this.P(la0,i*D),b=this.P(la1,i*D);x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1])}
 for(let j=j0;j<=j1;j++)if(j%5==0){const a=this.P(j*D,lg0),b=this.P(j*D,lg1);x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1])}
 x.lineWidth=mw*1.8+2;x.strokeStyle=C.cas;x.stroke();x.lineWidth=mw*1.8;x.strokeStyle=C.maj;x.stroke();
 line(p(HWY),mw*2.6+2,dk?'#555':'#f9ab00');line(p(HWY),mw*2.6,C.hwy);
 x.font='600 11px system-ui,sans-serif';x.textAlign='left';x.lineWidth=3;const lb=(t,q,col,dx)=>{x.strokeStyle=C.hal;x.strokeText(t,q[0]+dx,q[1]);x.fillStyle=col;x.fillText(t,q[0]+dx,q[1])};
 this.places.forEach(([n,la,lg])=>{const q=this.P(la,lg);x.fillStyle='#ea4335';x.beginPath();x.arc(q[0],q[1],3,0,7);x.fill();lb(n,q,C.txt,7)});
 lb('Río Tijuana',this.P(32.5296,-117.028),dk?'#6fa8dc':'#4a8fcf',0);lb('Vía Rápida',this.P(32.5110,-117.0200),C.txt,0);
 if(this.sel){const u=this.U.find(u=>u.id===this.sel.unit);if(u){const a=this.P(this.posOf(u).lat,this.posOf(u).lng),b=this.P(this.sel.to.lat,this.sel.to.lng);x.setLineDash([8,6]);line([a,b],3,'#4285f4');x.setLineDash([])}}
 this.I.forEach(i=>{const q=this.P(i.lat,i.lng);x.fillStyle='rgba(234,67,53,.25)';x.beginPath();x.arc(q[0],q[1],17,0,7);x.fill();x.fillStyle='#ea4335';x.strokeStyle='#fff';x.lineWidth=2;x.beginPath();x.arc(q[0],q[1],8,0,7);x.fill();x.stroke();lb(i.folio.slice(-4),q,'#c5221f',12)});
 this.U.forEach(u=>{const o=this.posOf(u),q=this.P(o.lat,o.lng);x.globalAlpha=u.busy?.55:1;x.fillStyle=u.col||'#555';x.strokeStyle='#fff';x.lineWidth=2;x.beginPath();x.arc(q[0],q[1],14,0,7);x.fill();x.stroke();x.fillStyle='#fff';x.font='700 9px system-ui,sans-serif';x.textAlign='center';x.fillText(u.id,q[0],q[1]+3);x.globalAlpha=1})}}
window.SimMap=SimMap})();
