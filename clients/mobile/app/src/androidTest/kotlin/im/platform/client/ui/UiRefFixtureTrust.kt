package im.platform.client.ui

import java.io.File
import java.security.KeyStore
import java.security.MessageDigest
import java.security.Provider
import java.security.Security
import java.security.cert.CertificateFactory
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManagerFactory

/** Explicit test-process CA; never installs device trust or changes hostname verification. */
class UiRefFixtureTrust private constructor(private val originalContext:SSLContext,
    private val originalFactory:javax.net.ssl.SSLSocketFactory,
    private val originalProviders:List<String>,private val originalSocketProvider:String):AutoCloseable {
    var restorationProof:String?=null;private set
    override fun close(){
        HttpsURLConnection.setDefaultSSLSocketFactory(originalFactory)
        SSLContext.setDefault(originalContext)
        Security.setProperty("ssl.SocketFactory.provider",originalSocketProvider)
        Security.removeProvider("UIRefFixtureCacheRefresh")
        check(Security.getProviders().map{it.name}==originalProviders)
        check(Security.getProperty("ssl.SocketFactory.provider")==originalSocketProvider)
        check(HttpsURLConnection.getDefaultSSLSocketFactory()===originalFactory)
        check(SSLContext.getDefault()===originalContext)
        restorationProof=org.json.JSONObject().put("providerOrderBefore",org.json.JSONArray(originalProviders)).put("providerOrderAfter",org.json.JSONArray(Security.getProviders().map{it.name})).put("socketProviderBefore",originalSocketProvider).put("socketProviderAfter",Security.getProperty("ssl.SocketFactory.provider")).put("sameDefaultContext",SSLContext.getDefault()===originalContext).put("sameHTTPSFactory",HttpsURLConnection.getDefaultSSLSocketFactory()===originalFactory).put("emptyMarkerAbsent",Security.getProvider("UIRefFixtureCacheRefresh")==null).toString()
    }
    companion object {
        fun install(path:String):UiRefFixtureTrust {
            require(path=="/sdcard/Android/data/im.platform.client/files/ui-ref-ca.der")
            val bytes=File(path).readBytes();require(bytes.size<8192)
            val digest=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString(""){"%02x".format(it)}
            require(digest=="a8042057db2373aa63b5b46c860c61614ba0e4bd6627f1acd3244dcf22d1c2f5")
            val ca=CertificateFactory.getInstance("X.509").generateCertificate(bytes.inputStream()) as java.security.cert.X509Certificate
            ca.checkValidity();require(ca.basicConstraints==0)
            val keys=KeyStore.getInstance(KeyStore.getDefaultType()).apply{load(null);setCertificateEntry("ui-ref-owned-local-fixture",ca)}
            val trust=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm()).apply{init(keys)}
            val context=SSLContext.getInstance("TLS").apply{init(null,trust.trustManagers,null)}
            val original=SSLContext.getDefault();val factory=HttpsURLConnection.getDefaultSSLSocketFactory()
            val hostnameVerifier=HttpsURLConnection.getDefaultHostnameVerifier()
            val providers=Security.getProviders().map{it.name}
            val socketProvider=checkNotNull(Security.getProperty("ssl.SocketFactory.provider")){"Original Android socket provider required for exact restoration"}
            require(Security.getProvider("UIRefFixtureCacheRefresh")==null)
            val lease=UiRefFixtureTrust(original,factory,providers,socketProvider)
            try {
            SSLContext.setDefault(context);HttpsURLConnection.setDefaultSSLSocketFactory(context.socketFactory)
            Security.setProperty("ssl.SocketFactory.provider","")
            // Android caches SSLSocketFactory by Security version, not SSLContext identity.
            // An empty test-process provider refreshes that cache without installing algorithms.
            check(Security.addProvider(object:Provider("UIRefFixtureCacheRefresh",1.0,"Empty test-process cache version marker"){})>0)
            check(HttpsURLConnection.getDefaultHostnameVerifier()===hostnameVerifier)
            return lease
            }catch(e:Throwable){lease.close();throw e}
        }
    }
}
