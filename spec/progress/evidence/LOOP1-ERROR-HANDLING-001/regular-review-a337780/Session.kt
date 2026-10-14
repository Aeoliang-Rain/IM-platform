package im.platform.client.send
import java.math.BigInteger
data class SendSession(val userId:String,val sessionId:String,val sessionEpoch:BigInteger,val accessToken:String)
