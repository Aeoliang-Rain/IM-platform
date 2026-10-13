package im.platform.client.sync

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import im.platform.client.storage.Repository
import im.platform.client.send.SendStorageFailure
import im.platform.client.send.repositoryRead
import java.util.UUID

// Actual SDK SQLite owned fixtures; NULL uses a deliberately malformed table,
// never a claim that the canonical NOT NULL schema accepts NULL.
internal class ContiguousReadChecks(private val context: Context) {
    private var assertions = 0
    private fun verify(value: Boolean) { check(value); assertions++ }
    fun run(): Int {
        val user = UUID.randomUUID().toString()
        val conversation = UUID.randomUUID().toString()
        val repo = Repository(context,user)
        repo.initialize()
        val field = Repository::class.java.getDeclaredField("db").apply { isAccessible = true }
        val db = field.get(repo) as SQLiteDatabase
        try {
            verify(repo.contiguous(conversation) == 0L)
            db.execSQL("INSERT INTO conversations(conversation_id,contiguous_seq) VALUES(?,?)",arrayOf(conversation,"0"))
            for (value in listOf("0","7","9007199254740993","9223372036854775807")) {
                db.execSQL("UPDATE conversations SET contiguous_seq=? WHERE conversation_id=?",arrayOf(value,conversation))
                verify(repo.contiguous(conversation) == value.toLong())
            }
            db.execSQL("UPDATE conversations SET contiguous_seq=? WHERE conversation_id=?",arrayOf("",conversation))
            verify(repo.query("SELECT CAST(contiguous_seq AS TEXT),typeof(contiguous_seq) FROM conversations WHERE conversation_id=?",arrayOf(conversation)).single() == listOf("","text"))
            val empty = try { repositoryRead { repo.contiguous(conversation) }; error("empty present sequence accepted") } catch (error: IllegalStateException) { error }
            verify(empty !is SendStorageFailure)
            verify(empty.message == "Invalid contiguous sequence")
            verify(empty.stackTrace.any { it.className == Repository::class.java.name && it.methodName == "contiguous" })
            // Test-only schema replacement isolates the previous nullable Elvis path.
            db.execSQL("DROP TABLE conversations")
            db.execSQL("CREATE TABLE conversations(conversation_id TEXT PRIMARY KEY,contiguous_seq INTEGER)")
            db.execSQL("INSERT INTO conversations VALUES(?,NULL)",arrayOf(conversation))
            verify(repo.query("SELECT contiguous_seq FROM conversations WHERE conversation_id=?",arrayOf(conversation)).single() == listOf(null))
            val nullValue = try { repositoryRead { repo.contiguous(conversation) }; error("NULL present sequence accepted") } catch (error: IllegalStateException) { error }
            verify(nullValue !is SendStorageFailure)
            verify(nullValue.message == "Invalid contiguous sequence")
            verify(nullValue.stackTrace.any { it.className == Repository::class.java.name && it.methodName == "contiguous" })
            for (value in listOf("-1","1.5","9223372036854775808")) {
                db.execSQL("UPDATE conversations SET contiguous_seq=? WHERE conversation_id=?",arrayOf(value,conversation))
                val failure = try { repo.contiguous(conversation); null } catch (error: Exception) { error }
                verify(failure is IllegalStateException || failure is NumberFormatException)
            }
            db.execSQL("DELETE FROM conversations")
            verify(repo.contiguous(conversation) == 0L)
        } finally {
            repo.close()
            verify(context.deleteDatabase("im-$user.sqlite"))
        }
        return assertions
    }
}
