import React from "react";
import {translate,displayText,type Locale} from "./resources.js";
export const LanguageContext=React.createContext<Locale>("en");
export function useText(){const locale=React.useContext(LanguageContext);return (key:string,params:Record<string,string|number>={})=>translate(locale,key,params);}
export function useDisplayText(){const locale=React.useContext(LanguageContext);return (value:string)=>displayText(locale,value);}
