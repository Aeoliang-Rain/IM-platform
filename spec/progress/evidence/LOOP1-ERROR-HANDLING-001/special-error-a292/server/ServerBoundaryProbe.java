import java.io.*;
import java.net.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
public final class ServerBoundaryProbe {
 static Method handle;
 static Throwable call(Socket s) throws Exception { try {handle.invoke(null,s,"gateway"); return null;} catch(InvocationTargetException e){return e.getCause();} }
 static class Fixture extends Socket {
  final String request; final Throwable fault; final ByteArrayOutputStream out=new ByteArrayOutputStream();
  Fixture(String request,Throwable fault){this.request=request;this.fault=fault;}
  public InputStream getInputStream() throws IOException {if(fault instanceof IOException) throw (IOException)fault;if(fault instanceof RuntimeException) throw (RuntimeException)fault;return new ByteArrayInputStream(request.getBytes(StandardCharsets.US_ASCII));}
  public OutputStream getOutputStream(){return out;}
 }
 public static void main(String[] args) throws Exception {
  handle=InfraPlaceholder.class.getDeclaredMethod("handle",Socket.class,String.class);handle.setAccessible(true);
  Fixture normal=new Fixture("GET /__infra/health HTTP/1.1\r\n\r\n",null);if(call(normal)!=null||!normal.out.toString(StandardCharsets.UTF_8).contains("200 OK"))throw new AssertionError("normal health");
  Fixture malformed=new Fixture("BAD\r\n\r\n",null);if(!(call(malformed) instanceof IOException)||malformed.out.size()!=0)throw new AssertionError("malformed must fail");
  IOException io=new IOException("controlled transport");if(call(new Fixture("",io))!=io)throw new AssertionError("IO root lost");
  IllegalStateException bug=new IllegalStateException("controlled internal bug");if(call(new Fixture("",bug))!=bug)throw new AssertionError("runtime root lost");
  Fixture empty=new Fixture("",null);if(call(empty)!=null||empty.out.size()!=0)throw new AssertionError("EOF falsely succeeds");
  Fixture missing=new Fixture("GET /missing HTTP/1.1\r\n\r\n",null);if(call(missing)!=null||!missing.out.toString(StandardCharsets.UTF_8).contains("404 Not Found"))throw new AssertionError("unknown route");
  System.out.println("PASS Java real compiled candidate handle: health, malformed failure, exact IO/root RuntimeException, EOF no response,404");
 }
}
