package im.platform.client.ui
import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle
import im.platform.client.ui.i18n.*
/** Actual Android preferences/resource behavior; no fake UI screenshot or backend acceptance. */
class I18nPreferencesInstrumentation:Instrumentation(){
 private var owned=false
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);owned=arguments?.getString("ownedFixture")=="i18n-owned-api34";start()}
 override fun onStart(){
  val result=Bundle()
  if(!owned){result.putString("failure","Owned API34 fixture confirmation required");finish(Activity.RESULT_CANCELED,result);return}
  val store=targetContext.getSharedPreferences("appearance",0)
  val credentials=targetContext.getSharedPreferences("secure-refresh",0)
  val original=store.all;val credentialOriginal=credentials.all;val prefs=Preferences(targetContext)
  fun restore(){val editor=store.edit().clear();for((key,value) in original)when(value){
   is String->editor.putString(key,value);is Int->editor.putInt(key,value);is Long->editor.putLong(key,value);is Float->editor.putFloat(key,value);is Boolean->editor.putBoolean(key,value);is Set<*>->editor.putStringSet(key,value.filterIsInstance<String>().toSet())
  };check(editor.commit())}
  try{
   check(android.os.Build.VERSION.SDK_INT==34)
   check(store.edit().remove("language").commit());check(prefs.loadLanguage()=="en")
   for(theme in listOf("cold","warm"))for(font in listOf(14,22))for(density in listOf(.8f,1.2f)){
    val appearance=Appearance(theme,font,density);prefs.saveAppearance(appearance)
    val before=store.all.filterKeys{it!="language"}
    for(locale in locales){prefs.saveLanguage(locale);check(prefs.loadLanguage()==locale);check(Preferences(targetContext).loadLanguage()==locale);check(prefs.loadAppearance()==appearance);check(store.all.filterKeys{it!="language"}==before);check(credentials.all==credentialOriginal)}
   }
   for(raw in listOf("","EN","en-US","zh","ja"," en","en\n","\uFEFFen","ja-jp","e".repeat(10000))){
    val before=store.all;check(runCatching{prefs.saveLanguage(raw)}.isFailure);check(store.all==before)
    check(store.edit().putString("language",raw).commit());check(prefs.loadLanguage()=="en")
   }
   check(store.edit().putBoolean("language",true).commit());check(prefs.loadLanguage()=="en")
   val keys=resources["en"]!!.keys
   for(locale in locales){check(resources[locale]!!.keys==keys);for(key in keys){val regex=Regex("\\{([A-Za-z]+)\\}");check(regex.findAll(resources[locale]!![key]!!).map{it.value}.toList().sorted()==regex.findAll(resources["en"]!![key]!!).map{it.value}.toList().sorted())}}
   // Actual placeholder substitution, including legal reordered parameters.
   for(locale in locales)for((key,value) in resources[locale]!!){
    val names=Regex("\\{([A-Za-z]+)\\}").findAll(value).map{it.groupValues[1]}.toSet()
    val params:Map<String,Any> = names.associateWith{"fixture-"+it}
    var expected=value;for((name,param) in params)expected=expected.replace("{"+name+"}",param.toString())
    check(translate(locale,key,params)==expected)
   }
   val reordered=mapOf("en" to mapOf("test" to "{first} {second}"),"ja-JP" to mapOf("test" to "{second} {first}"))
   check(translate("ja-JP","test",mapOf("first" to "A","second" to "B"),reordered)=="B A")
   val missing=resources.mapValues{it.value.toMutableMap()}.toMutableMap();missing["ja-JP"]!!.remove("nav.chat");check(translate("ja-JP","nav.chat",data=missing)==resources["en"]!!["nav.chat"])
   missing["en"]!!.remove("nav.chat");check(runCatching{translate("ja-JP","nav.chat",data=missing)}.isFailure)
   check(displayText("ja-JP","untrusted server detail")==resources["ja-JP"]!!["error.operation"])
   check(credentials.all==credentialOriginal)
   result.putString("result","PASS actual Android locale persistence/recreation/invalid inputs/appearance and credential isolation/resources")
  }catch(error:Throwable){result.putString("failure",error.stackTraceToString())}
  finally{try{restore();check(store.all==original);check(credentials.all==credentialOriginal)}catch(error:Throwable){result.putString("failure","Restore failed: "+error.stackTraceToString())}}
  finish(if(result.containsKey("failure"))Activity.RESULT_CANCELED else Activity.RESULT_OK,result)
 }
}
