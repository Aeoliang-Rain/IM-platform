package im.platform.client.send

// Only the final Repository's direct reads belong here. Callers keep parsing,
// state publication, callbacks and all writes outside this boundary.
internal fun <T> repositoryRead(read:()->T):T {
    try { return read() }
    catch(error:android.database.sqlite.SQLiteDiskIOException){throw SendStorageFailure(error)}
    catch(error:android.database.sqlite.SQLiteDatabaseCorruptException){throw SendStorageFailure(error)}
    catch(error:android.database.sqlite.SQLiteCantOpenDatabaseException){throw SendStorageFailure(error)}
    catch(error:android.database.sqlite.SQLiteDatabaseLockedException){throw SendStorageFailure(error)}
    catch(error:android.database.sqlite.SQLiteAccessPermException){throw SendStorageFailure(error)}
    catch(error:IllegalStateException){
        if(error.message?.startsWith("attempt to re-open an already-closed object:")==true)throw SendStorageFailure(error)
        throw error
    }
}
