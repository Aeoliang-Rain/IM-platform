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
@Composable fun Chat(state:WorkspaceState,open:(String)->Unit,reconnect:()->Unit,retry:(String)->Unit,send:(String)->Unit,draft:String,setDraft:(String)->Unit) {
    val t=useText()

    if(state.selected.isEmpty()){
        ConversationList(state,open);return
    }
    val selected=state.friends.find{it.directConversationId==state.selected};val spacing=(10*state.appearance.density).dp
    Column(Modifier.fillMaxSize(),verticalArrangement=Arrangement.spacedBy(spacing)){
        if(state.conversations.isEmpty()){Panel(Modifier.fillMaxWidth(),state.appearance){Text(t("chat.next"),style=MaterialTheme.typography.titleLarge);Text(t("chat.addHint"))}}else {
            Row(verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(selected?.user?.displayName?:t("chat.conversation"),style=MaterialTheme.typography.titleMedium);Text(if(state.connection=="ready")t("sync.automatic")else t("sync.offline"),style=MaterialTheme.typography.bodyMedium)};TextButton(onClick=reconnect,enabled=state.session!=null){Text(t("auth.reconnect"))}}
        }
        Messages(state,spacing,retry,Modifier.weight(1f))
        Composer(state,draft,setDraft,send){setDraft("")};Spacer(Modifier.height(5.dp))
    }
}
