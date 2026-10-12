import React from "react";
import {useText} from "../i18n/context.js";
import {languageEntry,languageNames,locales,type Locale} from "../i18n/resources.js";
export function LanguagePanel({locale,selectLanguage,languageStored}:{locale:Locale;selectLanguage:(value:Locale)=>void;languageStored:boolean}){const t=useText();
 return <fieldset className="language-panel"><legend>{languageEntry}</legend><div className="language-list" role="group" aria-label={languageEntry}>{locales.map((value,index)=><button type="button" key={value} lang={value} aria-pressed={locale===value} onClick={()=>selectLanguage(value)}>{languageNames[index]}</button>)}</div><p role="status" className={languageStored?"muted":"error"}>{t(languageStored?"language.saved":"language.failed")}</p></fieldset>;
}
