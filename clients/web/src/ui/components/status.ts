import type {Connection} from "../../application/client.js";
export const connectionText:Record<Connection,string>={idle:"未连接",ready:"在线",connecting:"正在连接",failed:"连接失败",protocol_error:"协议错误",offline:"连接已断开"};
