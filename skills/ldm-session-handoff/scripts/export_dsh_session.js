const fs=require('fs'), z=require('zlib');
const file=process.argv[2], outFile=process.argv[3];
const buf=fs.readFileSync(file);
let rest=buf, frames=0, chunks=[];
function step(){
  if(rest.length<4){ finish(); return; }
  const dec=z.createZstdDecompress();
  const parts=[];
  let done=false, err=null;
  dec.on('data',c=>parts.push(c));
  dec.on('error',e=>{err=e;});
  dec.on('close',()=>{
    if(done) return; done=true;
    const used=dec.bytesWritten;
    if(used>0){ chunks.push(Buffer.concat(parts)); frames++; rest=rest.slice(used); }
    if(err && used===0){ rest=rest.slice(1); }          // 不是帧头，跳过一字节再试
    else if(err && used>0){ /* 末帧可能被截断，保留已解出的 */ }
    setImmediate(step);
  });
  dec.end(rest);
}
function finish(){
  const txt=Buffer.concat(chunks).toString('utf8');
  fs.writeFileSync(outFile, txt);
  const lines=txt.split('\n').filter(Boolean);
  const c={};
  lines.forEach(l=>{try{const o=JSON.parse(l);const k=o.type||'?';c[k]=(c[k]||0)+1}catch(e){c['坏行']=(c['坏行']||0)+1}});
  console.log('帧数',frames,'| 解出字节',txt.length,'| 行数',lines.length);
  console.log(c);
}
step();
