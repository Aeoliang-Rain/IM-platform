package im.platform.client.sync
const val MAX_RESPONSE=6*1024*1024
class SyncFailure(val kind:String):Exception("Sync $kind failure")
class UserPage
class ConversationPage
object Wire {
 fun userRequest(id:String,cursor:String)="{}"
 fun conversationRequest(id:String,c:String,after:Long)="{}"
 fun user(raw:String,id:String,input:String)=UserPage()
 fun conversation(raw:String,id:String,c:String,after:Long)=ConversationPage()
 fun error(raw:String,id:String,status:Int,conversation:Boolean)=SyncFailure("protocol")
}
