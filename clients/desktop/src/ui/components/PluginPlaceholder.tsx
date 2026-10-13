import {useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function PluginPlaceholder({}:{}){
  const t=useText();
return <section className="page-content"><div className="glass panel"><p className="eyebrow">{t("plugin.eyebrow")}</p><h2>{t("plugin.title")}</h2><p>{t("plugin.description")}</p><div className="empty"><span>⊞</span><h3>{t("plugin.unavailable")}</h3><p>{t("plugin.detail")}</p></div><span className="badge">{t("plugin.badge")}</span></div></section>;
}
