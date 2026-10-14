import im.platform.client.ui.*
import kotlinx.coroutines.runBlocking
fun main()=runBlocking {println("GREEN actual source Kotlin production cleanup checks="+HttpCleanupChecks.run(Auth("https://localhost",Preferences())))}
