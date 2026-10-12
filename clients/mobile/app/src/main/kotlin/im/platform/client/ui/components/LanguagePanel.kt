package im.platform.client.ui.components
import androidx.compose.runtime.Composable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import im.platform.client.ui.Appearance
import im.platform.client.ui.i18n.*
@Composable fun LanguagePanel(language:String,stored:Boolean,select:(String)->Unit,prefs:Appearance){val t=useText()
 Panel(Modifier.fillMaxWidth(),prefs){Text(languageEntry,style=MaterialTheme.typography.titleMedium)
  LazyColumn(Modifier.fillMaxWidth().height(150.dp)){itemsIndexed(locales,key={_,locale->locale}){index,locale->FilterChip(selected=language==locale,onClick={select(locale)},label={Text(languageNames[index])})}}
  Text(t(if(stored)"language.saved" else "language.failed"),color=if(stored)MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.error)
 }
}
