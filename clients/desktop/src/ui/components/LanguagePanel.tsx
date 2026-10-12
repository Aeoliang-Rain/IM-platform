import React from "react";
import {useText} from "../i18n/context.js";
import {languageEntry,languageNames,locales,type Locale} from "../i18n/resources.js";
export function LanguagePanel({language,selectLanguage,languageStored}:{language:Locale;selectLanguage:(value:Locale)=>Promise<void>;languageStored:boolean}){const t=useText();
 return <fieldset className="language-panel"><legend>{languageEntry}</legend><div className="language-list" role="group" aria-label={languageEntry}>{locales.map((value,index)=><button type="button" key={value} lang={value} aria-pressed={language===value} onClick={()=>void selectLanguage(value)}>{languageNames[index]}</button>)}</div><p role="status" className={languageStored?"muted":"notice"}>{t(languageStored?"language.saved":"language.failed")}</p></fieldset>;
}
