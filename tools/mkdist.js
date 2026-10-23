// Genera la capa DIST (distritos reales de Tijuana simplificados) que maps.js dibuja
// como overlay sobre el mapa simulado (SimMap, que NO se toca). Fuente de datos:
// tijuana-districts.json (14 distritos; el mapa usa los 10 urbanos).
// Uso:  node tools/mkdist.js            → imprime la constante y validaciones
//       node tools/mkdist.js --write    → actualiza `const DIST=''` en core/static/maps.js
// Sin dependencias externas.
const fs=require('fs'),path=require('path');
const g=JSON.parse(fs.readFileSync(path.join(__dirname,'..','tijuana-districts.json'),'utf8'));
const RURAL=['LA PRESA RURAL','RESTO DEL MUNICIPIO','VALLE DE LAS PALMAS','CUEROS DE VENADO'];
// Douglas-Peucker sobre [lng,lat]
const dp=(pts,tol)=>{const seg=(a,b,p)=>{const dx=b[0]-a[0],dy=b[1]-a[1];let t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy||1);t=Math.max(0,Math.min(1,t));return Math.hypot(p[0]-a[0]-dx*t,p[1]-a[1]-dy*t)};
 if(pts.length<3)return pts;let d=0,i=0;for(let k=1;k<pts.length-1;k++){const q=seg(pts[0],pts[pts.length-1],pts[k]);if(q>d){d=q;i=k}}
 if(d>tol){const l=dp(pts.slice(0,i+1),tol),r=dp(pts.slice(i),tol);return l.slice(0,-1).concat(r)}return[pts[0],pts[pts.length-1]]};
const inn=(px,py,r)=>{let c=false;for(let i=0,j=r.length-1;i<r.length;j=i++){const xi=r[i][0],yi=r[i][1],xj=r[j][0],yj=r[j][1];if((yi>py)!=(yj>py)&&px<(xj-xi)*(py-yi)/(yj-yi)+xi)c=!c}return c};
const R=g.features.filter(f=>!RURAL.includes(f.properties.name)).map(f=>[f.properties.name,dp(f.geometry.coordinates[0],0.0006)]);
const DIST=R.map(([n,r])=>n+'|'+r.map(p=>p[1].toFixed(5)+','+p[0].toFixed(5)).join(' ')).join(';');
if(process.argv[2]==='--write'){
 const p=path.join(__dirname,'..','core','static','maps.js'),src=fs.readFileSync(p,'utf8');
 if(!/\bDIST='/.test(src))throw new Error('No existe el marcador DIST en maps.js');
 fs.writeFileSync(p,src.replace(/\bDIST='(?:[^']|\\')*'/,"DIST='"+DIST+"'"));
 console.log('maps.js actualizado · DIST '+DIST.length+' bytes · '+R.length+' distritos · '+R.reduce((s,[,r])=>s+r.length,0)+' vértices');
 process.exit(0)}
const esc=s=>s.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
const parts=[];for(let i=0;i<DIST.length;i+=1000)parts.push("'"+esc(DIST.slice(i,i+1000))+"'");
console.log('const DIST='+parts[0]+(parts.length>1?'+\n '+parts.slice(1).join('+\n '):'')+';');
console.log('// features '+R.length+' · vértices '+R.reduce((s,[,r])=>s+r.length,0)+' · DIST '+DIST.length+' bytes');
// ── validaciones: contención de lugares reales y orden del ranking de la app (PR-06/07)
const C=([,r])=>{let x=0,y=0;r.forEach(([a,b])=>{x+=a;y+=b});return[x/r.length,y/r.length]};
const LUG={'puente':[32.5315,-117.0450],'hospital':[32.5142,-117.0367],'centro':[32.5150,-117.0350],'aeropuerto':[32.5411,-116.9702],'universidad':[32.5067,-117.0428],'plaza':[32.5231,-117.0490]};
console.log('// contención (punto → distrito que lo contiene):');
for(const[k,[la,lg]]of Object.entries(LUG)){let dn='— fuera; revisar';for(const[n,r]of R)if(inn(lg,la,r)){dn=n;break}console.log('   '+k+' '+la.toFixed(4)+','+lg.toFixed(4)+' → '+dn)}
console.log('// (info) centroide de CENTRO: '+C(R.find(f=>f[0]==='CENTRO')).reverse().map(v=>v.toFixed(4)).join(',')+' — cae en el cauce del río: por eso «centro» es punto fijo');
const SEED={'A-12':[32.5270,-117.0360],'A-07':[32.5090,-116.9800],'P-07':[32.5150,-117.0340],'P-03':[32.4980,-117.0050],'B-03':[32.5430,-117.0100],'B-01':[32.5200,-117.0400]};
const hav=(a,b,c,d)=>{const p=Math.PI/180,h=Math.sin((c-a)*p/2)**2+Math.cos(a*p)*Math.cos(c*p)*Math.sin((d-b)*p/2)**2;return 12742*Math.asin(Math.sqrt(h))};
console.log('// PR-06/07 · distancia de cada unidad al «puente»: '+Object.entries(SEED).map(([k,v])=>k+':'+hav(v[0],v[1],LUG.puente[0],LUG.puente[1]).toFixed(1)+'km').join(' · '));
