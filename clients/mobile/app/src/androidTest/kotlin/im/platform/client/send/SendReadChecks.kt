package im.platform.client.send

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteException
import im.platform.client.storage.Repository
import java.math.BigInteger
import java.util.UUID

// Actual SDK read faults in the existing Send consumers, using owned databases.
internal class SendReadChecks(private val context:Context) {
    private var assertions=0
    private fun verify(value:Boolean){check(value);assertions++}
    suspend fun run():Int {
        val user=UUID.randomUUID().toString();val conversation=UUID.randomUUID().toString();val request=UUID.randomUUID().toString()
        val repo=Repository(context,user);repo.initialize()
        val sender=SendViewModel(repo,SendSession(user,UUID.randomUUID().toString(),BigInteger.ONE,"owned-send-read"))
        val field=Repository::class.java.getDeclaredField("db").apply {isAccessible=true}
        fun reopen(){field.set(repo,SQLiteDatabase.openDatabase(context.getDatabasePath("im-$user.sqlite").path,null,SQLiteDatabase.OPEN_READWRITE))}
        try {
            sender.openConversation(conversation);verify(sender.state.value.messages.isEmpty());verify(sender.state.value.error==null)
            repo.close()
            for(action in listOf<suspend ()->Unit>({sender.openConversation(conversation)},{sender.retry(conversation,request)})) {
                try{action();error("closed Send read accepted")}catch(error:SendStorageFailure){verify(error.cause is IllegalStateException);verify(error.cause!!.message!!.startsWith("attempt to re-open an already-closed object:"));verify(sender.state.value.error=="storage")}
            }
            reopen()
            // Repaired known read still executes normally; no synthetic row.
            sender.openConversation(conversation);verify(sender.state.value.messages.isEmpty())
            (field.get(repo) as SQLiteDatabase).execSQL("DROP TABLE messages")
            val before=sender.state.value
            for(action in listOf<suspend ()->Unit>({sender.openConversation(conversation)},{sender.retry(conversation,request)})) {
                val origin=try{action();error("schema Send read accepted")}catch(error:SQLiteException){error}
                verify(origin.message!!.contains("no such table: messages"));verify(origin.cause==null)
                verify(origin.stackTrace.any {it.className==Repository::class.java.name && it.methodName=="messages"})
                verify(sender.state.value==before)
                // Existing outer consumers do not replace the actual SDK object.
                val fail=im.platform.client.ui.WorkspaceViewModel::class.java.getDeclaredMethod("fail",Exception::class.java,java.lang.Boolean.TYPE).apply {isAccessible=true}
                val workspace=kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main){im.platform.client.ui.WorkspaceViewModel(context.applicationContext as android.app.Application)}
                for(active in listOf(true,false))try{fail.invoke(workspace,origin,active);error("Send schema root swallowed")}catch(error:java.lang.reflect.InvocationTargetException){verify(error.cause===origin)}
                im.platform.client.ui.WorkspaceViewModel::class.java.getDeclaredMethod("onCleared").apply {isAccessible=true}.invoke(workspace)
            }
        } finally {
            // Restore only the test connection for unchanged Send dispose refresh.
            repo.close();context.deleteDatabase("im-$user.sqlite");field.set(repo,SQLiteDatabase.openOrCreateDatabase(context.getDatabasePath("im-$user.sqlite"),null));repo.initialize()
            sender.dispose();repo.close();context.deleteDatabase("im-$user.sqlite")
        }
        return assertions
    }
}
