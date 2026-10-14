package im.platform.client.send
import java.math.BigInteger
class WireFailure:Exception()
object Wire {fun parse(raw:String,max:Int):Any=emptyMap<String,Any>();fun obj(v:Any?,keys:Set<String>):Map<String,Any?> = emptyMap();fun uuid(v:Any?):String="fixture";fun integer(v:Any?):BigInteger=BigInteger.ONE}
