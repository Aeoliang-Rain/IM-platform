@echo off
call "H:\gradle\wrapper\dists\gradle-8.9-bin\78qddjpeqn5v6yec3xb8kv9ca\gradle-8.9\bin\gradle.bat" --max-workers=1 "-Dorg.gradle.jvmargs=-Xmx768m -Dfile.encoding=UTF-8" -Pkotlin.compiler.execution.strategy=in-process %*
exit /b %errorlevel%
