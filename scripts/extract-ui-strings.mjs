// Timestamp: 2026-11-18 | Version: 2.5.0
// Author & Credits: https://www.alawise.es/1-s
// Parse JavaScript literals so apostrophes and templates cannot hide UI messages.
import {parse} from 'acorn';
import {readFile,readdir,writeFile} from 'node:fs/promises';
import {join,extname} from 'node:path';
const sys_rad=new URL('../',import.meta.url).pathname;
const dat_txt=new Set();
function visit(node){
  if(!node||typeof node!=='object')return;
  if(node.type==='Literal'&&typeof node.value==='string')dat_txt.add(node.value);
  if(node.type==='TemplateLiteral')for(const part of node.quasis)dat_txt.add(part.value.cooked??part.value.raw);
  for(const [key,val] of Object.entries(node)){
    if(key==='start'||key==='end'||key==='loc'||key==='value')continue;
    if(Array.isArray(val))for(const child of val)visit(child);else if(val&&typeof val==='object')visit(val);
  }
}
async function scan(dir){
  for(const item of await readdir(dir,{withFileTypes:true})){
    const path=join(dir,item.name);
    if(item.isDirectory()&&item.name!=='i18n')await scan(path);
    else if(['.js','.mjs'].includes(extname(path)))visit(parse(await readFile(path,'utf8'),{ecmaVersion:'latest',sourceType:'module'}));
  }
}
await scan(join(sys_rad,'src'));
for(const path of ['dist/app.js','deploy/send/public/app.js'])visit(parse(await readFile(join(sys_rad,path),'utf8'),{ecmaVersion:'latest',sourceType:'module'}));
process.stdout.write(JSON.stringify([...dat_txt]));
