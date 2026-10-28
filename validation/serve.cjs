// Local validation only. Email delivery is intercepted; no messages leave this process.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve('SHIP-2026-10-28a');
process.env.ACCESS_SECRET=crypto.randomBytes(32).toString('hex');
process.env.RESEND_API_KEY='local-validation-only';process.env.QUOTE_FROM='validation@example.invalid';process.env.QUOTE_TO='validation@example.invalid';
global.fetch=async(url,opts)=>{if(url!=='https://api.resend.com/emails')throw Error('Network prohibited');const p=JSON.parse(opts.body);if(p.subject.startsWith('Your NoFilter Access Code'))fs.writeFileSync('/tmp/nofilter-validation-code',p.subject.split(' · ')[1],{mode:0o600});return {ok:true,text:async()=>''};};
const handlers={};for(const n of ['access-request','access-verify'])handlers[n]=require(path.join(root,'netlify/functions',n+'.js')).handler;
const mime={'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2','.json':'application/json'};
http.createServer(async(req,res)=>{try{const u=new URL(req.url,'http://localhost'),name=u.pathname.split('/').pop();
if(u.pathname.startsWith('/.netlify/functions/')){if(!handlers[name]){res.writeHead(404);return res.end();}let body='';for await(const b of req)body+=b;const r=await handlers[name]({httpMethod:req.method,body,headers:req.headers});res.writeHead(r.statusCode,r.headers||{});return res.end(r.body);}
if(/^\/(?:netlify|\.netlify)(?:\/|$)/.test(u.pathname)){res.writeHead(404);return res.end('Not found');}
let p=path.resolve(root,'.'+decodeURIComponent(u.pathname));if(!p.startsWith(root+path.sep)&&p!==root)throw Error('Path');if(fs.existsSync(p)&&fs.statSync(p).isDirectory())p=path.join(p,'index.html');if(!fs.existsSync(p)){res.writeHead(404);return res.end('Not found');}res.writeHead(200,{'Content-Type':mime[path.extname(p)]||'application/octet-stream','Cache-Control':'no-store'});res.end(fs.readFileSync(p));}catch(e){res.writeHead(500);res.end('Validation server error');}}).listen(4173,'127.0.0.1',()=>console.log('Local validation on http://127.0.0.1:4173; email intercepted'));
