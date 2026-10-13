package im.platform.client.ui.components
import androidx.compose.runtime.*
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.*

import im.platform.client.ui.*
import im.platform.client.ui.i18n.*
internal fun noSearchMatch(state:WorkspaceState,query:String,submitted:String?) = submitted==query && query.isNotBlank() && state.searchComplete && state.results.isEmpty() && !state.busy && state.error==null
@Composable fun Friends(state:WorkspaceState,add:(String)->Unit,search:(String)->Unit,open:(String)->Unit) {
    val t=useText()

    var query by remember{mutableStateOf("")}
    var submitted by remember{mutableStateOf<String?>(null)}
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){
        Panel(Modifier.fillMaxWidth(),state.appearance){Text(t("friends.reach"),style=MaterialTheme.typography.titleLarge);Text(t("friends.exact"),style=MaterialTheme.typography.bodyMedium);OutlinedTextField(value=query,onValueChange={query=it},label={Text(t("auth.username"))},singleLine=true,modifier=Modifier.fillMaxWidth());Button(onClick={submitted=query;search(query)},enabled=state.session!=null&&!state.busy&&query.isNotBlank()){Text(if(state.busy)t("friends.searching")else t("friends.search"))};state.results.forEach{u->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(u.displayName,fontWeight=FontWeight.SemiBold);Text("@"+u.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={add(u.userId)},enabled=state.session!=null&&u.userId!=state.session?.userId&&!state.busy){Text(t("friends.add"))}}};if(noSearchMatch(state,query,submitted))Text(t("friends.noMatch"),style=MaterialTheme.typography.bodyMedium)}
        Panel(Modifier.fillMaxWidth(),state.appearance){Text(t("friends.your"),style=MaterialTheme.typography.titleLarge);if(state.friends.isEmpty())Text(t("friends.grow"));state.friends.forEach{f->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(f.user.displayName,fontWeight=FontWeight.SemiBold);Text("@"+f.user.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={open(f.directConversationId)}){Text(t("chat.message"))}}}}
    }
}
