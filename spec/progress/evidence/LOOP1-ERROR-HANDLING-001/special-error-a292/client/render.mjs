import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const base='C:/Users/21441/.codex/visualizations/2026/10/13/01a1341c-f5bd-7a20-8d63-e5a574250f3c/regular-review-a292-recovery2/fixture/clients/desktop/dist/';
const require=createRequire(base+'package.json');const React=require('react'),{renderToStaticMarkup}=require('react-dom/server');const {Messages}=await import('file:///'+base+'desktop/src/ui/components/Messages.js');
const row=['request','sender','body','SENDING',null,null,null],render=m=>renderToStaticMarkup(React.createElement(Messages,{s:{selected:'conversation',session:{userId:'sender'},offlineAccount:null,messages:[m]},retry:async()=>{},run:()=>{}}));
for(const state of ['SENDING','SENT','FAILED']){assert.match(render([...row.slice(0,3),state,...row.slice(4)]),/body/)}
for(const [index,value,reason] of [[2,null,/Message content missing/],[3,'UNKNOWN',/Unknown message state/]]){const m=[...row];m[index]=value;assert.throws(()=>render(m),reason)}const m=[...row];m[0]=null;assert.throws(()=>render(m),/Message identity missing/);
console.log('PASS fresh compiled Desktop renderer valid three states and required body/identity; unknown state/null body/null identity fail. Single existing dist React runtime.');
