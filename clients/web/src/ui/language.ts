import {validLocale,type Locale} from "./i18n/resources.js";
const LANGUAGE_KEY="plugworldim.language.v1";
export function loadLanguage():Locale {
 try {const raw=window.localStorage.getItem(LANGUAGE_KEY);return validLocale(raw)?raw:"en";}catch{return "en";}
}
export function saveLanguage(value:Locale):boolean {
 if(!validLocale(value))return false;
 try {window.localStorage.setItem(LANGUAGE_KEY,value);return true;}catch{return false;}
}
