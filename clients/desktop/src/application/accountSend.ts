import { accountDatabase } from "../storage/database.js";
import { Repository } from "../../../shared/protocol-sdk/src/storage/repository.js";
import { SendApplication, SendStorageFailure, type Session } from "./send.js";
// Tag only the literal native query. Initialization can also write, so its
// transaction adapter remains unchanged; consumers and observers are outside.
export function accountRepository(accountId:string):Repository {
  const db=accountDatabase(accountId);
  return new Repository({...db,query:async(sql,binds)=>{
    try{return await db.query(sql,binds);}catch(error){
      if(typeof error==="string" && ["Storage directory unavailable","Storage open failed","Storage close failed","Storage read open failed","Storage query rejected","Storage result unavailable","Storage result type rejected","Read-only setup failed","Read-only reset failed"].includes(error))throw new SendStorageFailure(error);
      throw error;
    }
  }});
}
export async function accountSend(session: Session): Promise<SendApplication> {
  const repository=accountRepository(session.userId);
  await repository.initialize();
  return new SendApplication(repository,session);
}
