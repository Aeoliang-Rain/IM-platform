// Compiled Web + existing controlled HTTPS/WSS fixture; not real backend/native acceptance.
import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {fixture} from '../web/fixture.mjs';
for(const name of ['WEB_BUILD_DIR','WEB_CERT_FILE','WEB_KEY_FILE','WEB_PLAYWRIGHT_MODULE','WEB_SCREEN_DIR','WEB_CANDIDATE_SHA'])if(!process.env[name])throw Error('Required actual input: '+name);
const sha=process.env.WEB_CANDIDATE_SHA;if(!/^[a-f0-9]{40}$/.test(sha))throw Error('Exact source SHA required');
const build=path.resolve(process.env.WEB_BUILD_DIR),out=path.resolve(process.env.WEB_SCREEN_DIR);
await fs.mkdir(out,{recursive:true});if((await fs.readdir(out)).length)throw Error('Use fresh owned screenshot output');
const {resources,languageNames,languageEntry}=await import(pathToFileURL(path.join(build,'web/src/ui/i18n/resources.js')));
const {chromium}=await import(pathToFileURL(process.env.WEB_PLAYWRIGHT_MODULE));
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const resourceHash=hash(await fs.readFile(path.join(build,'web/src/ui/i18n/resources.js')));
const languageDataHashes={};for(const locale of ['en','zh-CN','ja-JP'])languageDataHashes[locale]=hash(await fs.readFile(path.join(build,'web/src/ui/i18n',locale+'.js')));
const f=await fixture(build,process.env.WEB_CERT_FILE,process.env.WEB_KEY_FILE);
let browser,page;const captures=[],checks=[],errors=[];
const exact=text=>new RegExp('^'+text.replace(/[.*+?^$()|[\]\\{}]/g,'\\$&')+'$');
async function settled(locale){await page.waitForFunction(locale=>document.documentElement.lang===locale,locale);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
async function shot(name,locale,steps){await settled(locale);const file=name+'.png';await page.screenshot({path:path.join(out,file),fullPage:true});
 captures.push({file,sha256:hash(await fs.readFile(path.join(out,file))),source_sha:sha,source_is_clean_committed_candidate:process.env.I18N_CLEAN_CANDIDATE==='1',build_resource_sha256:resourceHash,language_data_sha256:languageDataHashes,locale,steps,viewport:page.viewportSize(),layout:await page.evaluate(()=>({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,theme:document.documentElement.dataset.theme,density:document.documentElement.dataset.density,font:getComputedStyle(document.documentElement).fontSize})),fixture:'existing HTTPS/WSS protocol fixture; not real backend',browser:browser.version()});}
const settings=locale=>page.locator('.rail-footer button').filter({hasText:exact(resources[locale]['nav.settings'])});
async function language(locale){await page.getByRole('button',{name:languageNames[['en','zh-CN','ja-JP'].indexOf(locale)],exact:true}).click();await settled(locale);}
async function login(locale){await page.getByLabel(resources[locale]['auth.username'],{exact:true}).fill('alice');await page.getByLabel(resources[locale]['auth.password'],{exact:true}).fill('controlled-test-password');await page.getByRole('button',{name:resources[locale]['auth.enter'],exact:true}).click();await page.locator('header.top .connection').filter({hasText:exact(resources[locale]['connection.ready'])}).waitFor();await page.getByRole('button',{name:/Bob Chen/}).click();}
try{
 browser=await chromium.launch({headless:true,...(process.env.WEB_BROWSER_EXE?{executablePath:process.env.WEB_BROWSER_EXE}:{})});
 const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1280,height:900}});page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(f.origin);await shot('web-fresh-en-login','en',['fresh browser profile']);await login('en');
 f.realtime('Language / 语言 / 言語 user content');await page.getByText('Language / 语言 / 言語 user content',{exact:true}).waitFor();
 await page.locator('#message').fill('fixture confirmed message');await page.locator('.composer button').click();await page.locator('article.message').filter({hasText:'fixture confirmed message'}).getByText(resources.en['chat.webSent'],{exact:true}).waitFor();
 const identities=f.state.sends.map(send=>send.requestId),draft='draft: English 简体中文 日本語';await page.locator('#message').fill(draft);
 await settings('en').click();await page.locator('.theme-options button').nth(1).click();await page.getByLabel(resources.en['settings.font'],{exact:true}).selectOption('20');await page.getByLabel(resources.en['settings.spacing'],{exact:true}).selectOption('spacious');
 const appearance=await page.evaluate(()=>localStorage.getItem('plugworldim.appearance.v1'));
 for(const locale of ['en','zh-CN','ja-JP']){
  await language(locale);assert.deepEqual(await page.locator('.language-list button').allTextContents(),[...languageNames]);assert.equal(await page.locator('.language-panel legend').innerText(),languageEntry);
  assert.equal(await page.evaluate(()=>localStorage.getItem('plugworldim.language.v1')),locale);assert.equal(await page.evaluate(()=>localStorage.getItem('plugworldim.appearance.v1')),appearance);await shot('web-'+locale+'-settings',locale,['actual fixed language button; warm/20/spacious retained']);
  await page.locator('.rail nav button').nth(0).click();assert.equal(await page.locator('#message').inputValue(),draft);assert.equal(await page.locator('.chat-heading h2').innerText(),'Bob Chen');await page.getByText('Language / 语言 / 言語 user content',{exact:true}).waitFor();
  await page.locator('article.message').filter({hasText:'fixture confirmed message'}).getByText(resources[locale]['chat.webSent'],{exact:true}).waitFor();assert.deepEqual(f.state.sends.map(send=>send.requestId),identities);await shot('web-'+locale+'-chat',locale,['draft/selection/user text/terminal confirmation/request identities retained']);
  for(const [index,name] of [[1,'friends'],[2,'ai'],[3,'plugin']]){await page.locator('.rail nav button').nth(index).click();await shot('web-'+locale+'-'+name,locale,['actual navigation']);}
  await page.locator('.rail-footer button').filter({hasText:exact(resources[locale]['nav.profile'])}).click();await shot('web-'+locale+'-profile',locale,['actual profile page']);
  await settings(locale).click();await page.setViewportSize({width:360,height:800});await shot('web-'+locale+'-narrow-settings',locale,['360px; maximum Web font/density']);await page.setViewportSize({width:1280,height:900});
 }
 checks.push('Three locale pages; draft/selection/user content/confirmation/request identities/appearance retained');
 await page.reload();await settled('ja-JP');await page.getByRole('heading',{name:resources['ja-JP']['auth.webTitle'],exact:true}).waitFor();assert.equal(await page.evaluate(()=>localStorage.getItem('plugworldim.appearance.v1')),appearance);await shot('web-reload-ja-JP-login','ja-JP',['reload restores locale/appearance; Web message memory lifecycle restarts']);
 for(const raw of ['', 'EN','en-US','zh',' en','en\n','\uFEFFen','ja-jp','x'.repeat(10000)]){await page.evaluate(raw=>localStorage.setItem('plugworldim.language.v1',raw),raw);await page.reload();await settled('en');await page.getByRole('heading',{name:resources.en['auth.webTitle'],exact:true}).waitFor();assert.equal(await page.evaluate(()=>localStorage.getItem('plugworldim.appearance.v1')),appearance);}
 await shot('web-invalid-locale-en','en',['invalid/alias/whitespace/BOM/newline/overlong values']);checks.push('Actual reload and invalid storage; appearance unaffected');
 const state=await context.storageState();const unavailable=await browser.newContext({ignoreHTTPSErrors:true,storageState:state,viewport:{width:1280,height:900}});
 await unavailable.addInitScript(()=>{const read=Storage.prototype.getItem,write=Storage.prototype.setItem;Storage.prototype.getItem=function(key){if(key==='plugworldim.language.v1')throw new DOMException('Owned fixture unavailable','SecurityError');return read.call(this,key)};Storage.prototype.setItem=function(key,value){if(key==='plugworldim.language.v1')throw new DOMException('Owned fixture unavailable','QuotaExceededError');return write.call(this,key,value)};});
 page=await unavailable.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto(f.origin);await settled('en');await settings('en').click();await language('ja-JP');await page.getByText(resources['ja-JP']['language.failed'],{exact:true}).waitFor();await shot('web-unavailable-memory-ja-JP','ja-JP',['owned locale storage fault; immediate memory switch and honest failure']);await page.reload();await settled('en');await shot('web-unavailable-reload-en','en',['unavailable read defaults en']);checks.push('Actual browser adapter read/write failure');
 assert.deepEqual(errors,[]);await fs.writeFile(path.join(out,'manifest.json'),JSON.stringify({result:'PASS',scope:'compiled Web browser presentation/storage with protocol fixture; not real backend/native/Architect acceptance',source_sha:sha,captures,checks,requests:f.state.requests.map(({path,method,event})=>({path,method,event})),send_request_ids:identities},null,2));console.log('PASS compiled Web i18n browser fixture; captures='+captures.length+'; Architect pending');
}catch(error){if(page){try{await page.screenshot({path:path.join(out,'failure.png'),fullPage:true})}catch{}}await fs.writeFile(path.join(out,'failure.json'),JSON.stringify({result:'FAIL',message:error.message,stack:error.stack,captures,checks},null,2));throw error;}
finally{await browser?.close();await f.close();}
