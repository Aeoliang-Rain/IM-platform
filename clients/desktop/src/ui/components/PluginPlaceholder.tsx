import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function PluginPlaceholder({}:{}){
return <section className="page-content"><div className="glass panel"><p className="eyebrow">YOUR WORKSPACE, EXTENDED</p><h2>Plugins</h2><p>Extensions will live here when the plugin platform becomes available.</p><div className="empty"><span>⊞</span><h3>Plugin capabilities unavailable</h3><p>No plugin runtime or installation service is connected in this release.</p></div><span className="badge">Unavailable in Loop 1 S2</span></div></section>;
}
