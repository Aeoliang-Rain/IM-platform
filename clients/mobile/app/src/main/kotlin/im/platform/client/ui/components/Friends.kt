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
@Composable fun Friends(state:WorkspaceState,add:(String)->Unit,search:(String)->Unit,open:(String)->Unit) {
    var query by remember{mutableStateOf("")}
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){
        Panel(Modifier.fillMaxWidth(),state.appearance){Text("People, within reach.",style=MaterialTheme.typography.titleLarge);Text("Find someone by their exact username.",style=MaterialTheme.typography.bodyMedium);OutlinedTextField(value=query,onValueChange={query=it},label={Text("Username")},singleLine=true,modifier=Modifier.fillMaxWidth());Button(onClick={search(query)},enabled=state.session!=null&&!state.busy&&query.isNotBlank()){Text(if(state.busy)"Searching…"else"Search")};state.results.forEach{u->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(u.displayName,fontWeight=FontWeight.SemiBold);Text("@"+u.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={add(u.userId)},enabled=state.session!=null&&u.userId!=state.session?.userId&&!state.busy){Text("Add friend")}}};if(query.isNotEmpty() && state.results.isEmpty() && !state.busy)Text("No matching user shown.",style=MaterialTheme.typography.bodyMedium)}
        Panel(Modifier.fillMaxWidth(),state.appearance){Text("Your friends",style=MaterialTheme.typography.titleLarge);if(state.friends.isEmpty())Text("Your circle is waiting to grow.");state.friends.forEach{f->Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(f.user.displayName,fontWeight=FontWeight.SemiBold);Text("@"+f.user.username,style=MaterialTheme.typography.bodyMedium)};TextButton(onClick={open(f.directConversationId)}){Text("Message")}}}}
    }
}
