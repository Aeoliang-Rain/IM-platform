"""Compile actual Java placeholder and exercise normal/IO/unknown error paths."""
from pathlib import Path
import os,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3]
HARNESS=r"""
import java.io.*;
import java.net.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
public class ErrorProbe {
 static class Peer extends Socket {
  String input;boolean bug;ByteArrayOutputStream output=new ByteArrayOutputStream();
  Peer(String value,boolean fail){input=value;bug=fail;}
  public InputStream getInputStream(){return new ByteArrayInputStream(input.getBytes(StandardCharsets.US_ASCII));}
  public OutputStream getOutputStream(){if(bug)throw original;return output;}
 }
 static IllegalStateException original=new IllegalStateException("controlled request programming bug");
 public static void main(String[] args)throws Exception{
  Method handle=InfraPlaceholder.class.getDeclaredMethod("handle",Socket.class,String.class);handle.setAccessible(true);
  Peer healthy=new Peer("GET /__infra/health HTTP/1.1\r\n\r\n".replace("\r","\r").replace("\n","\n"),false);
  // Literal CRLF from the source test below, not a product alternate parser.
  healthy.input="GET /__infra/health HTTP/1.1"+(char)13+(char)10+(char)13+(char)10;
  handle.invoke(null,healthy,"gateway");if(!healthy.output.toString("UTF-8").contains("200 OK"))throw new AssertionError("normal health failed");
  try{handle.invoke(null,new Peer("bad"+(char)13+(char)10+(char)13+(char)10,false),"gateway");throw new AssertionError("malformed request accepted");}catch(InvocationTargetException error){if(!(error.getCause() instanceof IOException))throw error;}
  try{handle.invoke(null,new Peer(healthy.input,true),"gateway");throw new AssertionError("unknown failure swallowed");}catch(InvocationTargetException error){if(error.getCause()!=original)throw new AssertionError("root cause replaced");}
  System.out.println("PASS compiled actual Java health/malformed IO rejection/original unknown failure");
 }
}
"""
with tempfile.TemporaryDirectory(prefix="error-java-") as temp:
 temp=Path(temp);probe=temp/"ErrorProbe.java";probe.write_text(HARNESS)
 subprocess.run(["javac","-d",str(temp),str(ROOT/"backend/java/InfraPlaceholder.java"),str(probe)],check=True)
 subprocess.run(["java","-cp",str(temp),"ErrorProbe"],check=True)
source=(ROOT/"backend/java/InfraPlaceholder.java").read_text()
assert source.index("Socket accepted = server.accept();") < source.index("try (Socket socket = accepted)")
assert "catch (IOException error)" in source and "catch (Exception error)" not in source
print("PASS listener failure outside request recovery; original source remains bounded non-business skeleton")
