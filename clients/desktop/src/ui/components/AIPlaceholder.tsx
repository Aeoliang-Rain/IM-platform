import {useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function AIPlaceholder({}:{}){
  const t=useText();
return <section className="page-content"><div className="glass future"><div className="orb">✧</div><p className="eyebrow">{t("ai.eyebrow")}</p><h2>{t("ai.title")}</h2><p>{t("ai.description")}</p><span className="badge">{t("ai.later")}</span><p className="muted">{t("ai.detail")}</p></div></section>;
}
